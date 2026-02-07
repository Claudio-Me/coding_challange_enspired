"""
Tests for the parser module.

Tests cover wall detection, character access, room parsing,
chair counting, room name extraction, and room merging logic.
"""
import pytest
from src.parser import is_wall, get_char, parse


class TestIsWall:
    """Tests for wall character detection."""

    def test_horizontal_wall(self) -> None:
        """Dash character is a wall (horizontal wall segment)."""
        assert is_wall('-') is True

    def test_vertical_wall(self) -> None:
        """Pipe character is a wall (vertical wall segment)."""
        assert is_wall('|') is True

    def test_corner(self) -> None:
        """Plus character (corner/junction) is a wall."""
        assert is_wall('+') is True

    def test_diagonal_forward_slash(self) -> None:
        """Forward slash is a wall (diagonal wall segment)."""
        assert is_wall('/') is True

    def test_diagonal_back_slash(self) -> None:
        """Backslash is a wall (diagonal wall segment)."""
        assert is_wall('\\') is True

    def test_space_not_wall(self) -> None:
        """Space is not a wall (empty floor space)."""
        assert is_wall(' ') is False

    def test_chair_not_wall(self) -> None:
        """Chair characters (W, P, S, C) are not walls."""
        for chair in "WPSC":
            assert is_wall(chair) is False, f"Chair '{chair}' should not be a wall"

    def test_room_name_chars_not_wall(self) -> None:
        """Parentheses and letters used in room names are not walls."""
        for char in "()abcdefghijklmnopqrstuvwxyz ":
            assert is_wall(char) is False, f"'{char}' should not be a wall"


class TestGetChar:
    """Tests for safe character access with bounds checking."""

    def test_valid_position(self) -> None:
        """Returns character at valid position."""
        lines = ["abc", "def"]
        assert get_char(lines, 0, 0) == 'a'
        assert get_char(lines, 1, 0) == 'b'
        assert get_char(lines, 2, 0) == 'c'
        assert get_char(lines, 0, 1) == 'd'

    def test_x_out_of_bounds_positive(self) -> None:
        """Returns space when x exceeds line length."""
        lines = ["abc"]
        assert get_char(lines, 10, 0) == ' '

    def test_x_out_of_bounds_negative(self) -> None:
        """Returns space when x is negative."""
        lines = ["abc"]
        assert get_char(lines, -1, 0) == ' '

    def test_y_out_of_bounds_positive(self) -> None:
        """Returns space when y exceeds number of lines."""
        lines = ["abc"]
        assert get_char(lines, 0, 10) == ' '

    def test_y_out_of_bounds_negative(self) -> None:
        """Returns space when y is negative."""
        lines = ["abc"]
        assert get_char(lines, 0, -1) == ' '

    def test_jagged_lines(self) -> None:
        """Handles lines of different lengths correctly."""
        lines = ["ab", "cdef", "g"]
        assert get_char(lines, 1, 0) == 'b'
        assert get_char(lines, 3, 1) == 'f'
        assert get_char(lines, 1, 2) == ' '  # Out of bounds for short line


class TestParse:
    """Tests for the main parsing function."""

    def test_empty_input(self) -> None:
        """Empty input returns empty room list."""
        rooms = parse("")
        assert rooms == []

    def test_simple_single_room(self) -> None:
        """Single rectangular room with name and one chair."""
        floor_plan = """\
+-------+
|       |
| (bed) |
|   W   |
|       |
+-------+"""
        rooms = parse(floor_plan)

        assert len(rooms) == 1
        room = rooms[0]
        assert room.name == "bed"
        assert room.chairs == {"W": 1, "P": 0, "S": 0, "C": 0}

    def test_two_adjacent_rooms(self) -> None:
        """Two rooms side by side, separated by a wall."""
        floor_plan = """\
+------+------+
|      |      |
| (a)  | (b)  |
|  W   |  P   |
|      |      |
+------+------+"""
        rooms = parse(floor_plan)

        assert len(rooms) == 2
        rooms_by_name = {r.name: r for r in rooms}

        assert "a" in rooms_by_name
        assert "b" in rooms_by_name
        assert rooms_by_name["a"].chairs["W"] == 1
        assert rooms_by_name["b"].chairs["P"] == 1

    def test_vertical_merge(self) -> None:
        """L-shaped room requires merging across rows."""
        floor_plan = """\
+----------+--------+
|          |        |
|          | (den)  |
|          |   C    |
|          +--------+
|                   |
| (living room)     |
|                   |
|  W  W  W          |
|                   |
+-------------------+"""
        rooms = parse(floor_plan)

        assert len(rooms) == 2
        rooms_by_name = {r.name: r for r in rooms}

        assert "living room" in rooms_by_name
        assert "den" in rooms_by_name

        # Living room has 3 wooden chairs
        assert rooms_by_name["living room"].chairs["W"] == 3

        # Den has 1 china chair
        assert rooms_by_name["den"].chairs["C"] == 1

    def test_all_chair_types(self) -> None:
        """All four chair types are counted correctly."""
        floor_plan = """\
+-------------+
|             |
| (showroom)  |
|  W W W      |
|  P P        |
|  S          |
|  C C C C    |
|             |
+-------------+"""
        rooms = parse(floor_plan)

        assert len(rooms) == 1
        room = rooms[0]
        assert room.name == "showroom"
        assert room.chairs == {"W": 3, "P": 2, "S": 1, "C": 4}

    def test_room_name_with_spaces(self) -> None:
        """Room names can contain spaces: (living room)."""
        floor_plan = """\
+------------------+
|                  |
| (living room)    |
|                  |
+------------------+"""
        rooms = parse(floor_plan)

        assert len(rooms) == 1
        assert rooms[0].name == "living room"

    def test_room_with_no_chairs(self) -> None:
        """Rooms with no chairs are included with zero counts."""
        floor_plan = """\
+--------+
|        |
| (hall) |
|        |
+--------+"""
        rooms = parse(floor_plan)

        assert len(rooms) == 1
        room = rooms[0]
        assert room.name == "hall"
        assert room.chairs == {"W": 0, "P": 0, "S": 0, "C": 0}

    def test_unnamed_rooms_excluded(self) -> None:
        """Rooms without names (external spaces) are not in output."""
        floor_plan = """\
        +--------+
        |        |
        | (room) |
        |   W    |
        +--------+"""
        rooms = parse(floor_plan)

        # Only the named room is returned, not the external space
        assert len(rooms) == 1
        assert rooms[0].name == "room"

    def test_unnamed_room_with_chairs_warns(self, capsys) -> None:
        """Unnamed room with chairs prints warning to stderr."""
        # A chair outside any named room
        floor_plan = """\
W
+--------+
| (room) |
+--------+"""
        rooms = parse(floor_plan)

        # Only named room returned
        assert len(rooms) == 1
        assert rooms[0].name == "room"

        # Warning should be printed to stderr
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "Unnamed room" in captured.err

    def test_complex_merge_pattern(self) -> None:
        """
        Room that spans multiple rows with gaps tests merge stability.

        This catches the "stale reference" bug if merge direction is wrong.
        """
        floor_plan = """\
+-----+-----+
|     |     |
|     |     |
|     +--+--+
|        |
| (big)  |
|   W    |
|        |
+--------+"""
        rooms = parse(floor_plan)

        # The big L-shaped room should be properly merged
        rooms_by_name = {r.name: r for r in rooms}
        assert "big" in rooms_by_name
        assert rooms_by_name["big"].chairs["W"] == 1

    def test_multiple_chairs_same_row(self) -> None:
        """Multiple chairs on the same row are all counted."""
        floor_plan = """\
+---------------+
|               |
| (office)      |
|  W  W  W  W   |
+---------------+"""
        rooms = parse(floor_plan)

        assert len(rooms) == 1
        assert rooms[0].chairs["W"] == 4

    def test_chairs_scattered_in_room(self) -> None:
        """Chairs scattered across multiple rows are all counted."""
        floor_plan = """\
+--------+
| W      |
|   P    |
|     S  |
| (room) |
|      C |
+--------+"""
        rooms = parse(floor_plan)

        assert len(rooms) == 1
        assert rooms[0].chairs == {"W": 1, "P": 1, "S": 1, "C": 1}
