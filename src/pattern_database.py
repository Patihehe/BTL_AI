# src/pattern_database.py
from typing import List, Dict, Tuple
from collections import deque
import pickle
import os
import time
from .board_utils import create_goal_state

def create_pattern_database(N: int, tiles: List[int], max_states: int = 1000) -> Dict[Tuple, int]:
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