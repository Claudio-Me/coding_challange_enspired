"""
Row scanning and merging logic for parsing ASCII floor plans.

This module implements a row-by-row scanning algorithm that:
1. Identifies walls and room boundaries
2. Creates Room objects for each cell
3. Merges rooms that connect (using forward pointers)
4. Extracts room names and counts chairs
"""
from .grid import Grid, WALL_CHARS, is_wall, get_char
from .room import Room


# Valid chair type characters
CHAIR_CHARS: set[str] = {'W', 'P', 'S', 'C'}

# Re-export for backward compatibility
__all__ = ['parse', 'is_wall', 'get_char', 'WALL_CHARS', 'CHAIR_CHARS']


def parse(text: str) -> list[Room]:
    """
    Parse an ASCII floor plan and return a list of named rooms with chair counts.

    Algorithm:
    1. Scan row by row, left-to-right
    2. For each non-wall cell, assign to current Room
    3. When crossing a wall, create a new Room
    4. Check cell above: if not wall and different room, merge using merged_into pointer
    5. Track room names when encountering (...) pattern
    6. Count chairs (W, P, S, C) in each room

    Merged rooms form a chain via the merged_into pointer. Use room.final() to
    follow the chain and get the root room that holds the merged data.

    Returns only named rooms. Unnamed rooms (external spaces) are excluded.
    If an unnamed room contains chairs, a warning is printed to stderr.
    """
    grid = Grid(text)
    if grid.height == 0:
        return []

    room_counter = 0

    for y in range(grid.height):
        current_room: Room | None = None
        name_buffer: str | None = None

        for x in range(grid.width):
            char = grid.get_char(x, y)

            if grid.is_wall(x, y):
                current_room = None
                name_buffer = None
                continue

            # Non-wall cell (empty space, chair, or room name char)
            if current_room is None:
                room_counter += 1
                current_room = Room(room_counter)

            # Check cell above - if there's a connected room, merge
            room_above = grid.get_connected_room_above(x, y)
            if room_above is not None:
                final_above = room_above.final()
                final_current = current_room.final()
                if final_above != final_current:
                    final_above.merge_with(final_current)

            # Store in grid
            grid.set_room(x, y, current_room)

            # Track chairs (add to the final/root room)
            if char in CHAIR_CHARS:
                current_room.final().chairs[char] += 1

            # Track room name: detect (...) pattern
            if char == '(':
                name_buffer = ""
            elif char == ')' and name_buffer is not None:
                current_room.final().name = name_buffer
                name_buffer = None
            elif name_buffer is not None:
                name_buffer += char

    return grid.extract_unique_rooms()
