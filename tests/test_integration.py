"""
Integration tests - full file to output comparison.

These tests read floor plan fixtures, parse them, format the output,
and compare against expected output files. On failure, the floor plan
content is printed to help with debugging.
"""
import pytest
from pathlib import Path
from src.parser import parse
from src.formatter import format_output


FIXTURES_DIR = Path(__file__).parent / "fixtures"


# List of all fixture names to test
FIXTURE_NAMES = [
    "simple",
    "single_room",
    "l_shaped",
    "no_chairs",
    "many_rooms",
    "diagonal",
    "corridor",
    "donut",
    "rhomboid",
    "complex",
    "rooms",
    "no_spacing",
    "wall_adjacent",
    "double_wall",
    "open_house",
    "u_shaped",
    "nested_u",
    "spiral_right",
    "spiral_double",
    "tree",
    "open_sides",
    "disjointed",
]


@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_fixture(fixture: str) -> None:
    """
    Integration test: parse floor plan and compare output to expected.

    For each fixture:
    1. Read the input floor plan from fixtures/{fixture}.txt
    2. Parse the floor plan to extract rooms and chair counts
    3. Format the output
    4. Compare against fixtures/expected/{fixture}.txt

    On failure, prints the floor plan content to help debug issues.
    """
    input_path = FIXTURES_DIR / f"{fixture}.txt"
    expected_path = FIXTURES_DIR / "expected" / f"{fixture}.txt"

    # Skip if fixture files don't exist
    if not input_path.exists():
        pytest.skip(f"Input fixture not found: {input_path}")
    if not expected_path.exists():
        pytest.skip(f"Expected output not found: {expected_path}")

    input_text = input_path.read_text()
    expected_output = expected_path.read_text()

    rooms = parse(input_text)
    actual_output = format_output(rooms)

    # On failure, pytest will show this message with the floor plan
    assert actual_output == expected_output, (
        f"\n\n{'=' * 60}\n"
        f"Floor plan for '{fixture}':\n"
        f"{'=' * 60}\n"
        f"{input_text}\n"
        f"{'=' * 60}\n"
        f"\nExpected output:\n"
        f"{'-' * 40}\n"
        f"{expected_output}\n"
        f"{'-' * 40}\n"
        f"\nActual output:\n"
        f"{'-' * 40}\n"
        f"{actual_output}\n"
        f"{'-' * 40}"
    )
