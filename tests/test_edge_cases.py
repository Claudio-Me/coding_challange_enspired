"""
Edge case tests for the parser.

These tests cover unusual floor plan configurations to ensure
the algorithm handles them correctly.
"""
import pytest
from src.parser import parse
from src.formatter import format_output


class TestMergeChains:
    """Tests for rooms merging through openings."""

    def test_both_sides_connect(self):
        """Two compartments both connecting to room below."""
        floor_plan = """\
+---+---+
|   |   |
| W | W |
|   |   |
+   +   +
|       |
| (room)|
+-------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "room"
        assert rooms[0].chairs["W"] == 2

    def test_three_compartments_merge(self):
        """Three compartments merging into one room."""
        floor_plan = """\
+---+---+---+
| W | W | W |
+   +   +   +
|           |
|   (all)   |
+-----------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "all"
        assert rooms[0].chairs["W"] == 3

    def test_five_compartments_merge(self):
        """Five compartments merging through openings."""
        floor_plan = """\
+-+-+-+-+-+
|W|W|W|W|W|
+ + + + + +
|         |
|  (five) |
+---------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "five"
        assert rooms[0].chairs["W"] == 5

    def test_twenty_compartments_merge(self):
        """Deep merge chain with 20 compartments."""
        floor_plan = """\
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|
+ + + + + + + + + + + + + + + + + + + + +
|                                       |
|              (twenty)                 |
+---------------------------------------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "twenty"
        assert rooms[0].chairs["W"] == 20

    def test_grid_merge(self):
        """Grid of compartments all merging."""
        floor_plan = """\
+-+-+-+-+
|W|W|W|W|
+ + + + +
|W|W|W|W|
+ + + + +
|W|W|W|W|
+ + + + +
|(room)W|
+-+-+-+-+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "room"
        assert rooms[0].chairs["W"] == 13


class TestIsolatedCompartments:
    """Tests for compartments that should NOT merge."""

    def test_one_side_blocked(self):
        """Right compartment is blocked, left connects."""
        floor_plan = """\
+---+---+
|   |   |
| W | W |
|   |   |
+   +---+
|       |
| (room)|
+-------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "room"
        assert rooms[0].chairs["W"] == 1  # Only left W connects

    def test_end_compartments_isolated(self):
        """First and last compartments blocked by walls."""
        floor_plan = """\
+-+-+-+-+-+-+-+-+-+-+
|W|W|W|W|W|W|W|W|W|W|
+-+ + + + + + + + +-+
|                   |
| (deep)            |
+-------------------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "deep"
        assert rooms[0].chairs["W"] == 8  # First and last W are isolated


class TestComplexShapes:
    """Tests for complex room shapes."""

    def test_nested_spiral(self):
        """Room nested inside another room."""
        floor_plan = """\
+---------------+
|               |
|  +---------+  |
|  |         |  |
|  |  +---+  |  |
|  |  | W |  |  |
|  |  |(s)|  |  |
|  |  +   +  |  |
|  |         |  |
|  +---------+  |
|               |
+---------------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "s"
        assert rooms[0].chairs["W"] == 1

    def test_c_shape(self):
        """C-shaped room with indentation."""
        floor_plan = """\
+-------+
|       |
|   W   +--+
|          |
|   (c)    |
|          |
|   W   +--+
|       |
+-------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "c"
        assert rooms[0].chairs["W"] == 2

    def test_diamond_with_diagonals(self):
        """Diamond shape using diagonal walls."""
        floor_plan = """\
    +---+
   /     \\
  /   W   \\
 /         \\
+   (dia)   +
 \\         /
  \\   W   /
   \\     /
    +---+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "dia"
        assert rooms[0].chairs["W"] == 2


class TestRoomNames:
    """Tests for room name handling."""

    def test_name_at_bottom(self):
        """Room name at the very end of the room."""
        floor_plan = """\
+-------+
|       |
|   W   |
|       |
|       |
|       |
| (end) |
+-------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "end"
        assert rooms[0].chairs["W"] == 1

    def test_empty_name(self):
        """Room with empty name ()."""
        floor_plan = """\
+-+
|W|
|()|
+-+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == ""
        assert rooms[0].chairs["W"] == 1

    def test_two_named_rooms_merge(self):
        """When two named rooms merge, the one above wins."""
        floor_plan = """\
+-------+-------+
|(left) |(right)|
|   W   |   W   |
+---+   +   +---+
    |       |
    +-------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        # The room "above" at the merge point wins
        assert rooms[0].name == "right"
        assert rooms[0].chairs["W"] == 2


class TestChairCounting:
    """Tests for chair counting edge cases."""

    def test_same_chairs_different_rooms(self):
        """Multiple rooms each with same chair types."""
        floor_plan = """\
+-----+-----+-----+
| WWW | WWW | WWW |
|(a)  |(b)  |(c)  |
+-----+-----+-----+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 3
        rooms_by_name = {r.name: r for r in rooms}
        assert rooms_by_name["a"].chairs["W"] == 3
        assert rooms_by_name["b"].chairs["W"] == 3
        assert rooms_by_name["c"].chairs["W"] == 3

    def test_packed_room(self):
        """Room completely filled with chairs."""
        floor_plan = """\
+-----+
|WWWWW|
|WWWWW|
|(den)|
|WWWWW|
+-----+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "den"
        assert rooms[0].chairs["W"] == 15

    def test_long_room(self):
        """Very wide room with many chairs."""
        floor_plan = """\
+--------------------------------------------------+
|WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW|
|(long room)                                       |
+--------------------------------------------------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "long room"
        assert rooms[0].chairs["W"] == 50

    def test_empty_room(self):
        """Room with no chairs."""
        floor_plan = """\
+-------+
|       |
|(empty)|
|       |
+-------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "empty"
        assert rooms[0].chairs == {"W": 0, "P": 0, "S": 0, "C": 0}


class TestStress:
    """Stress tests for the parser."""

    def test_thirty_compartments(self):
        """30 compartments merging into one room."""
        floor_plan = """\
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|W|
+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +
|                                                           |
|                         (stress)                          |
+-----------------------------------------------------------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "stress"
        assert rooms[0].chairs["W"] == 30

    def test_two_row_grid(self):
        """Two rows of compartments merging."""
        floor_plan = """\
+---+---+---+---+---+---+---+---+---+---+
| W | W | W | W | W | W | W | W | W | W |
|   +   +   +   +   +   +   +   +   +   |
|                                       |
|                                       |
+---+   +   +   +   +   +   +   +   +---+
| W | W | W | W | W | W | W | W | W | W |
|   +   +   +   +   +   +   +   +   +   |
|                                       |
|                 (grid)                |
+---------------------------------------+
"""
        rooms = parse(floor_plan)
        assert len(rooms) == 1
        assert rooms[0].name == "grid"
        assert rooms[0].chairs["W"] == 20
