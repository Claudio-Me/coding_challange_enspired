import pytest
from src.room import Room


class TestRoom:
    def test_init(self):
        room = Room(1)
        assert room.id == 1
        assert room.name is None
        assert room.chairs == {"W": 0, "P": 0, "S": 0, "C": 0}
        assert room.merged_into is None

    def test_chair_counting(self):
        room = Room(1)
        room.chairs["W"] = 3
        room.chairs["P"] = 2
        assert room.chairs["W"] == 3
        assert room.chairs["P"] == 2

    def test_merge_combines_chairs(self):
        room_a = Room(1)
        room_a.chairs["W"] = 2
        room_a.chairs["S"] = 1

        room_b = Room(2)
        room_b.chairs["W"] = 1
        room_b.chairs["P"] = 3

        result = room_a.merge_with(room_b)

        assert result is room_a
        assert room_a.chairs == {"W": 3, "P": 3, "S": 1, "C": 0}

    def test_merge_sets_forward_pointer(self):
        room_a = Room(1)
        room_b = Room(2)

        room_a.merge_with(room_b)

        assert room_b.merged_into is room_a

    def test_merge_takes_name_from_other_if_self_has_none(self):
        room_a = Room(1)
        room_b = Room(2)
        room_b.name = "kitchen"

        room_a.merge_with(room_b)

        assert room_a.name == "kitchen"

    def test_merge_keeps_self_name_if_present(self):
        room_a = Room(1)
        room_a.name = "living room"
        room_b = Room(2)
        room_b.name = "kitchen"

        room_a.merge_with(room_b)

        assert room_a.name == "living room"

    def test_final_returns_self_when_not_merged(self):
        room = Room(1)
        assert room.final() is room

    def test_final_follows_single_merge(self):
        room_a = Room(1)
        room_b = Room(2)

        room_a.merge_with(room_b)

        assert room_b.final() is room_a

    def test_final_follows_chain(self):
        room_a = Room(1)
        room_b = Room(2)
        room_c = Room(3)

        room_a.merge_with(room_b)  # b -> a
        room_a.merge_with(room_c)  # c -> a

        assert room_b.final() is room_a
        assert room_c.final() is room_a

    def test_final_follows_deep_chain(self):
        room_a = Room(1)
        room_b = Room(2)
        room_c = Room(3)

        room_b.merge_with(room_c)  # c -> b
        room_a.merge_with(room_b)  # b -> a

        # c -> b -> a
        assert room_c.final() is room_a
        assert room_b.final() is room_a
        assert room_a.final() is room_a
