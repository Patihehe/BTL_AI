from typing import List, Tuple, Optional, Dict
from copy import deepcopy
import random
import time
from collections import deque
import pickle
import os

def create_goal_state(N: int) -> List[List[int]]:
    """Tạo trạng thái mục tiêu cho bảng NxN."""
    goal = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i == N-1 and j == N-1:
                goal[i][j] = 0
            else:
                goal[i][j] = i * N + j + 1
    return goal

def create_random_start_board(N: int, max_steps: int = 20) -> List[List[int]]:
    """Tạo trạng thái ban đầu bằng cách xáo trộn trạng thái mục tiêu."""
    board = create_goal_state(N)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for _ in range(max_steps):
        blank_row, blank_col = -1, -1
        for i in range(N):
            for j in range(N):
                if board[i][j] == 0:
                    blank_row, blank_col = i, j
                    break
            if blank_row != -1:
                break
        
        dr, dc = random.choice(directions)
        new_row, new_col = blank_row + dr, blank_col + dc
        if 0 <= new_row < N and 0 <= new_col < N:
            board[blank_row][blank_col], board[new_row][new_col] = board[new_row][new_col], board[blank_row][blank_col]
    
    if is_solvable(board, N):
        return board
    return create_random_start_board(N, max_steps)

def create_pattern_database(N: int, tiles: List[int], max_states: int = 10000) -> Dict[Tuple, int]:
    """Tạo Pattern Database tối ưu cho tập hợp các ô."""
    goal = create_goal_state(N)
    goal_flat = [goal[i][j] for i in range(N) for j in range(N)]
    tiles_set = set(tiles)
    
    pdb = {}
    queue = deque([(goal_flat, 0, N * (N-1) + (N-1))])
    visited = set()
    
    while queue and len(pdb) < max_states:
        board_flat, cost, blank_pos = queue.popleft()
        state_tuple = tuple(board_flat[i] if board_flat[i] in tiles_set or board_flat[i] == 0 else -1 for i in range(N * N))
        if state_tuple not in pdb or cost < pdb[state_tuple]:
            pdb[state_tuple] = cost
            if state_tuple not in visited:
                visited.add(state_tuple)
                blank_row, blank_col = blank_pos // N, blank_pos % N
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                
                for dr, dc in directions:
                    new_row, new_col = blank_row + dr, blank_col + dc
                    if 0 <= new_row < N and 0 <= new_col < N:
                        new_blank_pos = new_row * N + new_col
                        new_board_flat = board_flat[:]
                        new_board_flat[blank_pos], new_board_flat[new_blank_pos] = new_board_flat[new_blank_pos], new_board_flat[blank_pos]
                        queue.append((new_board_flat, cost + 1, new_blank_pos))
    
    return pdb

def load_or_create_pdb(N: int, tiles: List[int], filename: str = "pdb.pkl") -> Dict[Tuple, int]:
    """Tải PDB từ file nếu tồn tại, nếu không thì tạo mới."""
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            pdb = pickle.load(f)
        print(f"Loaded PDB from {filename}, size: {len(pdb)} entries")
        return pdb
    else:
        print(f"Creating PDB for tiles {tiles}...")
        start_time = time.time()
        pdb = create_pattern_database(N, tiles)
        with open(filename, 'wb') as f:
            pickle.dump(pdb, f)
        print(f"PDB created in {time.time() - start_time:.2f} seconds, size: {len(pdb)} entries")
        return pdb

class PuzzleState:
    def __init__(self, board: List[List[int]], g: int = 0, parent: Optional['PuzzleState'] = None, move: str = None, N: int = 4, heuristic_type: str = 'manhattan', pdb: Optional[Dict] = None):
        self.board = board
        self.g = g
        self.parent = parent
        self.move = move
        self.N = N
        self.heuristic_type = heuristic_type
        self.pdb = pdb
        self.target_positions = {(i * N + j + 1): (i, j) for i in range(N) for j in range(N) if i * N + j + 1 < N * N}
        self.target_positions[0] = (N-1, N-1)
        self.nodes_visited = 0

    def __eq__(self, other):
        return self.board == other.board

    def manhattan_distance(self) -> int:
        distance = 0
        for i in range(self.N):
            for j in range(self.N):
                value = self.board[i][j]
                if value != 0:
                    target_row, target_col = self.target_positions[value]
                    distance += abs(i - target_row) + abs(j - target_col)
        return distance

    def misplaced_tiles(self) -> int:
        count = 0
        goal = create_goal_state(self.N)
        for i in range(self.N):
            for j in range(self.N):
                if self.board[i][j] != goal[i][j] and self.board[i][j] != 0:
                    count += 1
        return count

    def linear_conflict(self) -> int:
        distance = self.manhattan_distance()
        conflicts = 0
        
        for i in range(self.N):
            row_values = [self.board[i][j] for j in range(self.N) if self.board[i][j] != 0]
            for j1 in range(len(row_values)):
                for j2 in range(j1 + 1, len(row_values)):
                    v1, v2 = row_values[j1], row_values[j2]
                    if v1 in self.target_positions and v2 in self.target_positions:
                        t_row1, t_col1 = self.target_positions[v1]
                        t_row2, t_col2 = self.target_positions[v2]
                        if t_row1 == i and t_row2 == i and t_col1 > t_col2:
                            conflicts += 2
        
        for j in range(self.N):
            col_values = [self.board[i][j] for i in range(self.N) if self.board[i][j] != 0]
            for i1 in range(len(col_values)):
                for i2 in range(i1 + 1, len(col_values)):
                    v1, v2 = col_values[i1], col_values[i2]
                    if v1 in self.target_positions and v2 in self.target_positions:
                        t_row1, t_col1 = self.target_positions[v1]
                        t_row2, t_col2 = self.target_positions[v2]
                        if t_col1 == j and t_col2 == j and t_row1 > t_row2:
                            conflicts += 2
        
        return distance + conflicts

    def pattern_database(self) -> int:
        if self.pdb is None:
            return 0
        tiles = list(self.pdb.keys())[0]
        tiles_set = set(i for i in tiles if i != -1 and i != 0)
        board_tuple = tuple(self.board[i // self.N][i % self.N] if self.board[i // self.N][i % self.N] in tiles_set or self.board[i // self.N][i % self.N] == 0 else -1 for i in range(self.N * self.N))
        return self.pdb.get(board_tuple, 0)

    def h(self) -> int:
        self.nodes_visited += 1
        if self.heuristic_type == 'manhattan':
            return self.manhattan_distance()
        elif self.heuristic_type == 'misplaced':
            return self.misplaced_tiles()
        elif self.heuristic_type == 'linear_conflict':
            return self.linear_conflict()
        elif self.heuristic_type == 'pdb':
            return self.pattern_database()
        else:
            raise ValueError(f"Unknown heuristic type: {self.heuristic_type}")

    def f(self) -> int:
        return self.g + self.h()

    def get_blank_pos(self) -> Tuple[int, int]:
        for i in range(self.N):
            for j in range(self.N):
                if self.board[i][j] == 0:
                    return i, j
        return -1, -1

    def get_neighbors(self) -> List['PuzzleState']:
        neighbors = []
        row, col = self.get_blank_pos()
        directions = [
            (-1, 0, "Up"),
            (1, 0, "Down"),
            (0, -1, "Left"),
            (0, 1, "Right")
        ]

        for dr, dc, move_name in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.N and 0 <= new_col < self.N:
                new_board = [row[:] for row in self.board]
                new_board[row][col], new_board[new_row][new_col] = new_board[new_row][new_col], new_board[row][col]
                neighbors.append(PuzzleState(new_board, self.g + 1, self, move_name, self.N, self.heuristic_type, self.pdb))
        return neighbors

def is_solvable(board: List[List[int]], N: int) -> bool:
    flat = [num for row in board for num in row if num != 0]
    inversions = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] > flat[j]:
                inversions += 1

    blank_row = -1
    for i in range(N):
        for j in range(N):
            if board[i][j] == 0:
                blank_row = i
                break
        if blank_row != -1:
            break

    if N % 2 == 1:
        return inversions % 2 == 0
    else:
        taxicab_distance = abs(blank_row - (N - 1))
        return (inversions + taxicab_distance) % 2 == 0

def ida_star(start_board: List[List[int]], N: int, heuristic_type: str = 'manhattan', pdb: Optional[Dict] = None) -> Tuple[Optional[PuzzleState], int]:
    if not is_solvable(start_board, N):
        return None, -1

    start_state = PuzzleState(start_board, N=N, heuristic_type=heuristic_type, pdb=pdb)
    threshold = start_state.f()
    while True:
        result, new_threshold = search(start_state, threshold)
        if result is not None:
            return result, result.g
        if new_threshold == float('inf'):
            return None, -1
        threshold = new_threshold

def search(state: PuzzleState, threshold: int) -> Tuple[Optional[PuzzleState], int]:
    f_value = state.f()
    if f_value > threshold:
        return None, f_value
    if state.board == create_goal_state(state.N):
        return state, threshold

    min_threshold = float('inf')
    for neighbor in state.get_neighbors():
        result, new_threshold = search(neighbor, threshold)
        if result is not None:
            return result, threshold
        min_threshold = min(min_threshold, new_threshold)

    return None, min_threshold

def print_solution(state: Optional[PuzzleState]):
    if state is None:
        print("No solution exists for this puzzle.")
        return
    path = []
    moves = []
    while state:
        path.append(state)  # Lưu PuzzleState thay vì board
        if state.move:
            moves.append(state.move)
        state = state.parent
    print(f"Solution found in {len(moves)} moves:")
    print(f"Nodes visited: {path[0].nodes_visited}")
    for i, state in enumerate(reversed(path)):
        print(f"Step {i}:")
        for row in state.board:
            print(row)
        if i < len(moves):
            print(f"Move: {moves[len(moves)-1-i]}")
        print()

if __name__ == "__main__":
    N = 4
    max_steps = 20
    heuristics = ['manhattan', 'misplaced', 'linear_conflict', 'pdb']
    
    # Tạo hoặc tải PDB cho ô 1-4
    pdb_tiles = [1, 2, 3, 4]
    pdb = load_or_create_pdb(N, pdb_tiles, f"pdb_{N}_{'_'.join(map(str, pdb_tiles))}.pkl")
    
    # Tạo trạng thái ban đầu chung
    start_board = create_random_start_board(N, max_steps)
    print(f"\nRandom initial state ({N}x{N}):")
    for row in start_board:
        print(row)
    print()

    for heuristic in heuristics:
        print(f"\nTesting heuristic: {heuristic}")
        start_time = time.time()
        solution, steps = ida_star(start_board, N, heuristic, pdb if heuristic == 'pdb' else None)
        print_solution(solution)
        print(f"Time taken: {time.time() - start_time:.2f} seconds")