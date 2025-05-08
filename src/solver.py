from typing import List, Tuple, Optional
from .puzzle_state import PuzzleState
from .board_utils import create_goal_state

def ida_star(start_board: List[List[int]], N: int, heuristic_type: str = 'manhattan') -> Tuple[Optional[PuzzleState], int]:
    """Giải bài toán n-puzzle bằng thuật toán IDA*."""

    PuzzleState.nodes_visited = 0
    start_state = PuzzleState(start_board, N=N, heuristic_type=heuristic_type)
    threshold = start_state.f()
    while True:
        result, new_threshold = search(start_state, threshold)
        if result is not None:
            return result, result.g
        if new_threshold == float('inf'):
            return None, -1
        threshold = new_threshold

def search(state: PuzzleState, threshold: int) -> Tuple[Optional[PuzzleState], int]:
    """Tìm kiếm theo chiều sâu với ngưỡng."""
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