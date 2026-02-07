"""
Floor plan generator for benchmarking the chair counter algorithm.

Generates random ASCII floor plans with controllable parameters:
- Grid dimensions (rows x cols)
- Number of rooms
- Chair density
"""
import random
from typing import Optional


# Room name pool for generated rooms
ROOM_NAMES = [
    "kitchen", "bedroom", "bathroom", "living room", "office",
    "dining room", "hallway", "closet", "pantry", "laundry",
    "garage", "basement", "attic", "den", "study",
    "nursery", "guest room", "master bed", "foyer", "balcony",
]

CHAIR_TYPES = ['W', 'P', 'S', 'C']


def generate_floor_plan(
    rows: int,
    cols: int,
    num_rooms: int,
    chair_density: float = 0.1,
    seed: Optional[int] = None
) -> str:
    """
    Generate a random floor plan with specified dimensions and room count.

    Args:
        rows: Number of rows in the grid (height)
        cols: Number of columns in the grid (width)
        num_rooms: Number of rooms to create
        chair_density: Probability of placing a chair in empty space (0.0-1.0)
        seed: Random seed for reproducibility

    Returns:
        ASCII string representing the floor plan
    """
    if seed is not None:
        random.seed(seed)

    # Ensure minimum size for rooms
    if rows < 5 or cols < 5:
        raise ValueError("Grid must be at least 5x5")
    if num_rooms < 1:
        raise ValueError("Must have at least 1 room")

    # Create grid filled with spaces
    grid = [[' ' for _ in range(cols)] for _ in range(rows)]

    # Draw outer border
    _draw_border(grid, 0, 0, rows - 1, cols - 1)

    # Calculate room layout
    rooms = _partition_space(1, 1, rows - 2, cols - 2, num_rooms)

    # Draw room walls and assign names
    room_names = random.sample(ROOM_NAMES, min(num_rooms, len(ROOM_NAMES)))
    if num_rooms > len(ROOM_NAMES):
        # Generate additional names if needed
        for i in range(num_rooms - len(ROOM_NAMES)):
            room_names.append(f"room {i + 1}")

    for i, (r1, c1, r2, c2) in enumerate(rooms):
        # Draw walls for this room
        _draw_room_walls(grid, r1, c1, r2, c2)

        # Place room name
        name = room_names[i]
        _place_room_name(grid, r1, c1, r2, c2, name)

        # Place chairs based on density
        _place_chairs(grid, r1, c1, r2, c2, chair_density)

    # Convert grid to string
    return '\n'.join(''.join(row) for row in grid)


def _draw_border(grid: list[list[str]], r1: int, c1: int, r2: int, c2: int):
    """Draw a rectangular border with corners."""
    # Corners
    grid[r1][c1] = '+'
    grid[r1][c2] = '+'
    grid[r2][c1] = '+'
    grid[r2][c2] = '+'

    # Horizontal walls
    for c in range(c1 + 1, c2):
        grid[r1][c] = '-'
        grid[r2][c] = '-'

    # Vertical walls
    for r in range(r1 + 1, r2):
        grid[r][c1] = '|'
        grid[r][c2] = '|'


def _draw_room_walls(grid: list[list[str]], r1: int, c1: int, r2: int, c2: int):
    """Draw interior walls for a room (may overlap with existing walls)."""
    for c in range(c1, c2 + 1):
        if grid[r1][c] == ' ':
            grid[r1][c] = '-'
        elif grid[r1][c] == '|':
            grid[r1][c] = '+'
        if grid[r2][c] == ' ':
            grid[r2][c] = '-'
        elif grid[r2][c] == '|':
            grid[r2][c] = '+'

    for r in range(r1, r2 + 1):
        if grid[r][c1] == ' ':
            grid[r][c1] = '|'
        elif grid[r][c1] == '-':
            grid[r][c1] = '+'
        if grid[r][c2] == ' ':
            grid[r][c2] = '|'
        elif grid[r][c2] == '-':
            grid[r][c2] = '+'

    # Corners
    grid[r1][c1] = '+'
    grid[r1][c2] = '+'
    grid[r2][c1] = '+'
    grid[r2][c2] = '+'


def _partition_space(
    r1: int, c1: int, r2: int, c2: int, num_rooms: int
) -> list[tuple[int, int, int, int]]:
    """
    Recursively partition a space into rooms.

    Returns list of (r1, c1, r2, c2) tuples for each room.
    """
    if num_rooms <= 1:
        return [(r1, c1, r2, c2)]

    height = r2 - r1
    width = c2 - c1

    # Need minimum 3 cells per room (wall + content + wall)
    if height < 6 and width < 6:
        return [(r1, c1, r2, c2)]

    # Decide split direction (prefer splitting the longer dimension)
    if height >= width and height >= 6:
        # Horizontal split
        split_point = r1 + height // 2
        rooms_top = num_rooms // 2
        rooms_bottom = num_rooms - rooms_top

        top = _partition_space(r1, c1, split_point, c2, rooms_top)
        bottom = _partition_space(split_point, c1, r2, c2, rooms_bottom)
        return top + bottom
    elif width >= 6:
        # Vertical split
        split_point = c1 + width // 2
        rooms_left = num_rooms // 2
        rooms_right = num_rooms - rooms_left

        left = _partition_space(r1, c1, r2, split_point, rooms_left)
        right = _partition_space(r1, split_point, r2, c2, rooms_right)
        return left + right
    else:
        return [(r1, c1, r2, c2)]


def _place_room_name(
    grid: list[list[str]], r1: int, c1: int, r2: int, c2: int, name: str
):
    """Place room name in the center of the room."""
    # Find center row (avoiding walls)
    center_row = (r1 + r2) // 2
    if center_row == r1:
        center_row = r1 + 1
    if center_row == r2:
        center_row = r2 - 1

    # Calculate name with parentheses
    full_name = f"({name})"

    # Find starting column (centered)
    room_width = c2 - c1 - 1  # Interior width
    start_col = c1 + 1 + (room_width - len(full_name)) // 2

    # Ensure name fits
    if start_col < c1 + 1:
        start_col = c1 + 1
    if start_col + len(full_name) > c2:
        # Truncate name if too long
        available = c2 - start_col - 1
        if available > 3:
            full_name = f"({name[:available-2]})"

    # Place name
    for i, char in enumerate(full_name):
        if start_col + i < c2:
            grid[center_row][start_col + i] = char


def _place_chairs(
    grid: list[list[str]], r1: int, c1: int, r2: int, c2: int, density: float
):
    """Place chairs randomly in the room interior."""
    for r in range(r1 + 1, r2):
        for c in range(c1 + 1, c2):
            if grid[r][c] == ' ' and random.random() < density:
                grid[r][c] = random.choice(CHAIR_TYPES)


def generate_simple_grid(rows: int, cols: int, num_rooms: int) -> str:
    """
    Generate a simple grid layout with equal-sized rooms.

    Creates a grid of rooms arranged in rows, simpler than random partitioning.
    Useful for predictable benchmarking.
    """
    # Calculate grid layout
    rooms_per_row = int(num_rooms ** 0.5)
    if rooms_per_row < 1:
        rooms_per_row = 1
    rooms_per_col = (num_rooms + rooms_per_row - 1) // rooms_per_row

    room_height = (rows - 1) // rooms_per_col
    room_width = (cols - 1) // rooms_per_row

    if room_height < 4 or room_width < 4:
        raise ValueError("Grid too small for requested number of rooms")

    grid = [[' ' for _ in range(cols)] for _ in range(rows)]

    room_names = random.sample(ROOM_NAMES, min(num_rooms, len(ROOM_NAMES)))
    room_idx = 0

    for ri in range(rooms_per_col):
        for ci in range(rooms_per_row):
            if room_idx >= num_rooms:
                break

            r1 = ri * room_height
            c1 = ci * room_width
            r2 = min(r1 + room_height, rows - 1)
            c2 = min(c1 + room_width, cols - 1)

            _draw_border(grid, r1, c1, r2, c2)

            if room_idx < len(room_names):
                _place_room_name(grid, r1, c1, r2, c2, room_names[room_idx])

            room_idx += 1

    return '\n'.join(''.join(row) for row in grid)


if __name__ == "__main__":
    # Demo: generate a sample floor plan
    print("Sample floor plan (20x40, 4 rooms):")
    print("-" * 40)
    plan = generate_floor_plan(20, 40, 4, chair_density=0.05, seed=42)
    print(plan)
