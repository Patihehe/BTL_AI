# src/utils.py
from typing import Optional
from .puzzle_state import PuzzleState

def print_solution(state: Optional[PuzzleState]):
    """In đường đi giải bài toán."""
    if state is None:
        print("No solution exists for this puzzle.")
        return
    path = []
    moves = []
    while state:
        path.append(state)
        if state.move:
            moves.append(state.move)
        state = state.parent
    print(f"Solution found in {len(moves)} moves:")
    print(f"Nodes visited: {PuzzleState.nodes_visited}")
    for i, state in enumerate(reversed(path)):
        print(f"Step {i}:")
        for row in state.board:
            print(row)
        if i < len(moves):
            print(f"Move: {moves[len(moves)-1-i]}")
        print()