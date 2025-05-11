# src/board_utils.py
from typing import List, Tuple
import random

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

def create_random_start_board(N: int) -> List[List[int]]:
    """Tạo trạng thái ban đầu bằng cách xáo trộn trạng thái mục tiêu,
    tránh đi lại ngược hướng liên tiếp."""
    max_steps = random.randint(15, 20)
    board = create_goal_state(N)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # UP, DOWN, LEFT, RIGHT
    opposite = {(-1, 0): (1, 0), (1, 0): (-1, 0), (0, -1): (0, 1), (0, 1): (0, -1)}
    
    prev_dir = None
    
    for _ in range(max_steps):
        # Tìm vị trí ô trống (0)
        blank_row, blank_col = next((i, j) for i in range(N) for j in range(N) if board[i][j] == 0)
        
        # Tạo danh sách các hướng hợp lệ
        possible_dirs = []
        for dr, dc in directions:
            new_row, new_col = blank_row + dr, blank_col + dc
            if 0 <= new_row < N and 0 <= new_col < N:
                if prev_dir is None or (dr, dc) != opposite.get(prev_dir):
                    possible_dirs.append((dr, dc))
        
        if not possible_dirs:
            continue  # bỏ qua nếu không có hướng nào hợp lệ
        
        dr, dc = random.choice(possible_dirs)
        new_row, new_col = blank_row + dr, blank_col + dc
        
        # Hoán đổi
        board[blank_row][blank_col], board[new_row][new_col] = board[new_row][new_col], board[blank_row][blank_col]
        
        prev_dir = (dr, dc)
    
    return board
