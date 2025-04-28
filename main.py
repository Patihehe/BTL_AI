# main.py
import time
import argparse
from src.board_utils import create_random_start_board
from src.pattern_database import load_or_create_pdb
from src.solver import ida_star
from src.utils import print_solution
from src.gui import run_gui

def run_console():
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='N-Puzzle Solver')
    parser.add_argument('--gui', action='store_true', help='Run with GUI')
    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        run_console()