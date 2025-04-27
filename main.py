# main.py
import time
from src.board_utils import create_random_start_board
from src.pattern_database import load_or_create_pdb
from src.solver import ida_star
from src.utils import print_solution

if __name__ == "__main__":
    N = 4
    max_steps = 20
    heuristics = ['manhattan', 'misplaced', 'linear_conflict', 'pdb']
    
    # Tạo hoặc tải PDB cho ô 1-4
    pdb_tiles = [1, 2, 3, 4]
    pdb = load_or_create_pdb(N, pdb_tiles, f"pdb_{N}_{'_'.join(map(str, pdb_tiles))}.pkl")
    
    start_board = create_random_start_board(N)
    print(f"\nInitial state ({N}x{N}):")
    for row in start_board:
        print(row)
    print()

    for heuristic in heuristics:
        print(f"\nTesting heuristic: {heuristic}")
        start_time = time.time()
        solution, steps = ida_star(start_board, N, heuristic, pdb if heuristic == 'pdb' else None)
        print_solution(solution)
        print(f"Time taken: {time.time() - start_time:.2f} seconds")