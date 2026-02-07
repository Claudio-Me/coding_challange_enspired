"""
Grid class for encapsulating floor plan data and room assignments.

Provides a clean interface for:
- Accessing characters at positions
- Checking for walls
- Getting/setting room assignments
- Checking connections to adjacent cells
"""
import sys

from .room import Room


# Characters that represent walls in the floor plan
WALL_CHARS: set[str] = {'-', '|', '+', '/', '\\'}


def is_wall(char: str) -> bool:
    """Check if a character represents a wall."""
    return char in WALL_CHARS


def get_char(lines: list[str], x: int, y: int) -> str:
    """
    Get character at position (x, y) in lines.

    Returns space if position is out of bounds.
    """
    if y < 0 or y >= len(lines):
        return ' '
    if x < 0 or x >= len(lines[y]):
        return ' '
    return lines[y][x]


class Grid:
    """
    Encapsulates the floor plan grid and room assignments.

    The grid stores both the original floor plan text and the room
    assignments for each cell. It provides methods for safe access
    to characters and rooms, with bounds checking.
    """

    def __init__(self, text: str):
        """
        Initialize grid from floor plan text.

        Args:
            text: ASCII floor plan as a string
        """
        self.lines = text.splitlines()
        self.height = len(self.lines)
        self.width = max(len(line) for line in self.lines) if self.lines else 0
        self._cells: list[list[Room | None]] = [
            [None] * self.width for _ in range(self.height)
        ]

    def get_char(self, x: int, y: int) -> str:
        """
        Get character at position (x, y).

        Returns space if position is out of bounds, allowing safe
        access without bounds checking at call sites.
        """
        if y < 0 or y >= self.height:
            return ' '
        if x < 0 or x >= len(self.lines[y]):
            return ' '
        return self.lines[y][x]

    def is_wall(self, x: int, y: int) -> bool:
        """Check if position contains a wall character."""
        return self.get_char(x, y) in WALL_CHARS

    def get_room(self, x: int, y: int) -> Room | None:
        """
        Get room assigned to position.

        Returns None if out of bounds or no room assigned.
        """
        if y < 0 or y >= self.height:
            return None
        if x < 0 or x >= self.width:
            return None
        return self._cells[y][x]

    def set_room(self, x: int, y: int, room: Room) -> None:
        """Assign room to position."""
        self._cells[y][x] = room

    def get_connected_room_above(self, x: int, y: int) -> Room | None:
        """
        Get room from cell above if connected (no wall between).

        Returns None if:
        - At top edge (y == 0)
        - Cell above is a wall
        - No room assigned to cell above
        """
        if y <= 0:
            return None
        if self.is_wall(x, y - 1):
            return None
        return self.get_room(x, y - 1)

    def extract_unique_rooms(self) -> list[Room]:
        """
        Extract unique named rooms from the grid.

        - Uses .final() to follow merge chains
        - Deduplicates by room ID
        - Only returns rooms that have a name (unnamed = external space)
        - Warns to stderr if an unnamed room contains chairs
        """
        seen_ids: set[int] = set()
        rooms: list[Room] = []

        for row in self._cells:
            for cell in row:
                if cell is not None:
                    room = cell.final()
                    if room.id not in seen_ids:
                        seen_ids.add(room.id)

                        if room.name is not None:
                            rooms.append(room)
                        else:
                            total_chairs = sum(room.chairs.values())
                            if total_chairs > 0:
                                print(
                                    f"WARNING: Unnamed room (id={room.id}) contains "
                                    f"{total_chairs} chair(s) - not included in output",
                                    file=sys.stderr
                                )

        return rooms
