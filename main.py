import time
from src.board_utils import create_random_start_board
from src.solver import ida_star
from src.utils import print_solution

if __name__ == "__main__":
    N = 4
    max_steps = 50
    heuristics = ['manhattan', 'misplaced', 'linear_conflict', 'out_of_row_col']
    
    start_board = create_random_start_board(N, max_steps)
    print(f"\nInitial state ({N}x{N}):")
    for row in start_board:
        print(row)
    print()

    for heuristic in heuristics:
        print(f"\nTesting heuristic: {heuristic}")
        start_time = time.time()
        solution, steps = ida_star(start_board, N, heuristic)
        print_solution(solution)
        print(f"Time taken: {time.time() - start_time:.2f} seconds")