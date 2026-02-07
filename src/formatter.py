"""
Output formatting for chair counter results.

Formats room and chair data into the required output format:
- Total line with sum of all chairs
- Each room alphabetically with its chair counts
"""
from .room import Room


# Chair types in output order
CHAIR_TYPES: list[str] = ["W", "P", "S", "C"]


def format_chair_line(chairs: dict[str, int]) -> str:
    """
    Format a single line of chair counts.

    Output format: 'W: X, P: X, S: X, C: X'
    """
    parts = [f"{t}: {chairs[t]}" for t in CHAIR_TYPES]
    return ", ".join(parts)


def format_output(rooms: list[Room]) -> str:
    """
    Format the final output string.

    Output structure:
    - First line: 'total:' with sum of all chairs across all rooms
    - Then each room alphabetically by name
    - Each room has name + colon, then chair counts on next line

    Returns the complete output string with trailing newline.
    """
    # Calculate totals across all rooms
    totals: dict[str, int] = {t: 0 for t in CHAIR_TYPES}
    for room in rooms:
        for t in CHAIR_TYPES:
            totals[t] += room.chairs[t]

    # Sort rooms alphabetically by name
    sorted_rooms = sorted(rooms, key=lambda r: r.name or "")

    # Build output lines
    lines: list[str] = []
    lines.append("total:")
    lines.append(format_chair_line(totals))

    for room in sorted_rooms:
        lines.append(f"{room.name}:")
        lines.append(format_chair_line(room.chairs))

    return "\n".join(lines) + "\n"
