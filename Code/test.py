from typing import List, Tuple, Optional
from copy import deepcopy
import random
import time

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

def create_random_start_board(N: int, max_steps: int = 50) -> List[List[int]]:
    """Tạo trạng thái ban đầu bằng cách xáo trộn trạng thái mục tiêu với số bước giới hạn."""
    board = create_goal_state(N)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for _ in range(max_steps):
        # Tìm vị trí ô trống
        blank_row, blank_col = -1, -1
        for i in range(N):
            for j in range(N):
                if board[i][j] == 0:
                    blank_row, blank_col = i, j
                    break
            if blank_row != -1:
                break
        
        # Chọn hướng di chuyển ngẫu nhiên
        dr, dc = random.choice(directions)
        new_row, new_col = blank_row + dr, blank_col + dc
        if 0 <= new_row < N and 0 <= new_col < N:
            board[blank_row][blank_col], board[new_row][new_col] = board[new_row][new_col], board[blank_row][blank_col]
    
    if is_solvable(board, N):
        return board
    # Nếu không giải được, thử lại
    return create_random_start_board(N, max_steps)

class PuzzleState:
    def __init__(self, board: List[List[int]], g: int = 0, parent: Optional['PuzzleState'] = None, move: str = None, N: int = 4):
        self.board = board
        self.g = g
        self.parent = parent
        self.move = move
        self.N = N
        # Bảng tra cứu vị trí mục tiêu
        self.target_positions = {(i * N + j + 1): (i, j) for i in range(N) for j in range(N) if i * N + j + 1 < N * N}
        self.target_positions[0] = (N-1, N-1)

    def __eq__(self, other):
        return self.board == other.board

    def manhattan_distance(self) -> int:
        """Tính heuristic Manhattan với Linear Conflict."""
        distance = 0
        # Tính Manhattan
        for i in range(self.N):
            for j in range(self.N):
                value = self.board[i][j]
                if value != 0:
                    target_row, target_col = self.target_positions[value]
                    distance += abs(i - target_row) + abs(j - target_col)
        
        # Thêm Linear Conflict
        conflicts = 0
        # Kiểm tra hàng
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
        
        # Kiểm tra cột
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

    def f(self) -> int:
        return self.g + self.manhattan_distance()

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
                # Sao chép bảng nhanh hơn
                new_board = [row[:] for row in self.board]
                new_board[row][col], new_board[new_row][new_col] = new_board[new_row][new_col], new_board[row][col]
                neighbors.append(PuzzleState(new_board, self.g + 1, self, move_name, self.N))
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

def ida_star(start_board: List[List[int]], N: int) -> Tuple[Optional[PuzzleState], int]:
    if not is_solvable(start_board, N):
        return None, -1

    start_state = PuzzleState(start_board, N=N)
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
        path.append(state.board)
        if state.move:
            moves.append(state.move)
        state = state.parent
    print(f"Solution found in {len(moves)} moves:")
    for i, board in enumerate(reversed(path)):
        print(f"Step {i}:")
        for row in board:
            print(row)
        if i < len(moves):
            print(f"Move: {moves[len(moves)-1-i]}")
        print()

if __name__ == "__main__":
    N = int(input("Nhap N: "))
    start_time = time.time()
    start_board = create_random_start_board(N)  # Giới hạn 20 bước để dễ giải
    print(f"Random initial state ({N}x{N}):")
    for row in start_board:
        print(row)
    print()

    solution, steps = ida_star(start_board, N)
    print_solution(solution)
    print(f"Time taken: {time.time() - start_time:.2f} seconds")