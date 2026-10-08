import random
from collections import deque

CELL = 40

# Stores the maze generated most recently.
# This allows solve(start, goal) to use the current maze
# while keeping the required solve(start, goal) interface.
_current_walls = None


def generate_maze(cols, rows):
    """Generate a maze using the recursive backtracking algorithm."""

    global _current_walls

    visited = [[False] * cols for _ in range(rows)]

    # Each cell has walls in the order:
    # [N, S, E, W]
    walls = [
        [[True, True, True, True] for _ in range(cols)]
        for _ in range(rows)
    ]

    def carve(r, c):
        visited[r][c] = True

        directions = [
            (-1, 0, 0, 1),  # North
            (1, 0, 1, 0),   # South
            (0, 1, 2, 3),   # East
            (0, -1, 3, 2),  # West
        ]

        random.shuffle(directions)

        for dr, dc, wall_dir, opposite_dir in directions:
            nr = r + dr
            nc = c + dc

            if 0 <= nr < rows and 0 <= nc < cols:
                if not visited[nr][nc]:
                    walls[r][c][wall_dir] = False
                    walls[nr][nc][opposite_dir] = False
                    carve(nr, nc)

    carve(0, 0)

    # Store the newly generated maze so solve() can use it.
    _current_walls = walls

    return walls


def solve(start, goal):
    """Find the shortest path between two cells using BFS."""

    if _current_walls is None:
        return []

    rows = len(_current_walls)
    cols = len(_current_walls[0])

    queue = deque([start])

    # parent[cell] = previous cell used to reach it.
    parent = {start: None}

    directions = [
        (-1, 0, 0, 1),  # North
        (1, 0, 1, 0),   # South
        (0, 1, 2, 3),   # East
        (0, -1, 3, 2),  # West
    ]

    while queue:
        r, c = queue.popleft()

        if (r, c) == goal:
            break

        for dr, dc, wall_dir, opposite_dir in directions:
            nr = r + dr
            nc = c + dc

            # Stay inside the maze.
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue

            # Already visited.
            if (nr, nc) in parent:
                continue

            # There must be no wall between the current cell
            # and the neighbouring cell.
            if _current_walls[r][c][wall_dir]:
                continue

            # Also verify the opposite wall of the neighbour.
            if _current_walls[nr][nc][opposite_dir]:
                continue

            parent[(nr, nc)] = (r, c)
            queue.append((nr, nc))

    # No path found.
    if goal not in parent:
        return []

    # Reconstruct the path from goal back to start.
    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = parent[current]

    # Reverse so it becomes start -> goal.
    path.reverse()

    return path


def cell_rect(r, c, import_pygame=None):
    import pygame

    return pygame.Rect(
        c * CELL,
        r * CELL,
        CELL,
        CELL
    )