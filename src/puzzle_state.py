import math
from typing import List, Tuple, Optional, Dict
from .board_utils import create_goal_state

class PuzzleState:
    nodes_visited = 0  # Biến class để đếm tổng số node duyệt

    def __init__(self, board: List[List[int]], g: int = 0, parent: Optional['PuzzleState'] = None,
                  move: str = None, N: int = 4, heuristic_type: str = 'manhattan'):
        self.board = board # Bảng trạng thái hiện tại
        self.g = g # Chi phí từ trạng thái khởi đầu đến trạng thái hiện tại
        self.parent = parent # Lưu trạng thái cha để truy vết đường đi
        self.move = move # Lưu hướng di chuyển từ trạng thái cha đến trạng thái hiện tại
        self.N = N # Kích thước của bảng (NxN)
        self.heuristic_type = heuristic_type # Loại hàm heuristic được sử dụng
        self.target_positions = {(i * self.N + j + 1): (i, j) for i in range(self.N)
                                  for j in range(self.N) if i * self.N + j + 1 < self.N * self.N}
        self.target_positions[0] = (self.N-1, self.N-1)

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
    
    def euclidean_distance(self) -> int:
        total = 0
        for i in range(self.N):
            for j in range(self.N):
                value = self.board[i][j]
                if value == 0:
                    continue
                target_i, target_j = self.target_positions[value]
                # Tính khoảng cách Euclid và lấy phần nguyên
                distance = math.sqrt((i - target_i) ** 2 + (j - target_j) ** 2)
                total += int(round(distance))
        return total

    def h(self) -> int:
        PuzzleState.nodes_visited += 1
        if self.heuristic_type == 'manhattan':
            return self.manhattan_distance()
        elif self.heuristic_type == 'misplaced':
            return self.misplaced_tiles()
        elif self.heuristic_type == 'linear_conflict':
            return self.linear_conflict()
        elif self.heuristic_type == 'euclidean':
            return self.euclidean_distance()
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
                neighbors.append(PuzzleState(new_board, self.g + 1, self, move_name, self.N, self.heuristic_type))
        return neighbors