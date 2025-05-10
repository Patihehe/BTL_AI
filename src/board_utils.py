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

def create_random_start_board(N: int, max_steps: int = 30) -> List[List[int]]:
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
        
        dr, dc = random.choice(directions) #direct_row, direct_col
        new_row, new_col = blank_row + dr, blank_col + dc
        if 0 <= new_row < N and 0 <= new_col < N:
            board[blank_row][blank_col], board[new_row][new_col] = board[new_row][new_col], board[blank_row][blank_col]
    
    return board
