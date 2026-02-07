# Chair Counter

A command-line tool that reads ASCII floor plans and counts chairs per room.

---

## Installation

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
python -m src.main <input_file>
```

**Example:**
```bash
python -m src.main rooms.txt
```

**Output:**
```
total:
W: 14, P: 7, S: 3, C: 1
balcony:
W: 0, P: 2, S: 0, C: 0
bathroom:
W: 0, P: 1, S: 0, C: 0
...
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parser.py -v

# Run specific fixture test
pytest "tests/test_integration.py::test_fixture[simple]" -v
```

---

## Project Structure

```
chair_counter/
│
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── rooms.txt                 # Sample floor plan
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── main.py               # CLI entry point
│   ├── parser.py             # Row scanning and room merging logic
│   ├── grid.py               # Grid class for floor plan data
│   ├── formatter.py          # Output formatting
│   └── room.py               # Room class with merge support
│
├── analysis/                 # Performance analysis tools
│   ├── performance.ipynb     # Jupyter notebook with benchmarks
│   ├── visualizer.py         # Terminal visualization of parsing
│   └── floor_plan_generator.py  # Random floor plan generation
│
└── tests/                    # Test suite
    ├── __init__.py
    ├── test_room.py          # Unit tests for Room class
    ├── test_parser.py        # Unit tests for parser functions
    ├── test_integration.py   # Integration tests (fixture comparison)
    ├── generator.py          # Random test case generator
    │
    └── fixtures/             # Test floor plans + expected outputs
        ├── *.txt             # Input floor plans (14 fixtures)
        └── expected/         # Expected output for each fixture
```

---

## Algorithm Logic

### Overview

The parser uses a **row scanning algorithm with union-find style merging**:

```
1. Scan grid row by row, left to right
2. Assign each non-wall cell to a Room
3. When crossing a wall or starting a new line → create new Room
4. When cell connects to cell above (no wall) → merge rooms
5. Extract room names from (room name) patterns
6. Count chairs (W, P, S, C) in each room
```


Use  `visualizer.py` (usage described below) in the `analysis/` directory to see an animated step-by-step parsing of the algorithm.


### Data Structures

**Grid** - Encapsulates floor plan data and room assignments:
```python
class Grid:
    lines: list[str]             # Floor plan text lines
    height: int                  # Number of rows
    width: int                   # Max row length
    _cells: list[list[Room]]     # Room assignments per cell

    def get_char(x, y) -> str                    # Get character at position
    def is_wall(x, y) -> bool                    # Check if position is a wall
    def get_connected_room_above(x, y) -> Room   # Get room above if connected
    def extract_unique_rooms() -> list[Room]     # Get all named rooms
```

**Room** - Holds room data with merge support:
```python
class Room:
    id: int                      # Unique identifier
    name: str | None             # Room name from (name) pattern
    chairs: dict[str, int]       # {"W": 0, "P": 0, "S": 0, "C": 0}
    merged_into: Room | None     # Points to parent room after merge
```


## Performance & Complexity Analysis

Let:
- `N` = total characters in floor plan
- `m` = max row length (width)
- `n` = number of rows (height)
- `R` = number of rooms

### Time Complexity: O(N)

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Grid scan | O(N) | Visit each character exactly once |
| Room creation | O(1) | Per new room |
| Merge operation | O(1) | Pointer update + dict merge (path compression) |
| Chair counting | O(1) | Per chair found |
| Name extraction | O(m × n) | Single pass to collect unique rooms |
| Output sorting | O(R log R) | Sort rooms alphabetically |

**Total: O(N)** where N is the number of characters in the input. (To be exact it can be **O(R log R)** in the worst chase scenario where every cell is a separate room, but in practice we expect R << N)

### Space Complexity: O(m × n)

| Structure | Space | Notes |
|-----------|-------|-------|
| Input lines | O(N) | Store input text |
| Grid | O(m × n) | One Room pointer per cell |
| Rooms | O(R) | Room objects (R << m × n) |
| Output | O(R) | Formatted strings |

**Total: O(m × n)** where m is the max row length and n is the number of rows.

### Benchmarks

The `analysis/` directory contains tools for empirical verification of these complexity bounds:

```bash
jupyter notebook analysis/performance.ipynb
```

Benchmarks include:
- Time vs grid size (verifies O(N) scaling)
- Time vs room count (verifies minimal impact)
- Memory usage vs grid dimensions (verifies O(m×n) space)

### Visualizer

Terminal-based visualization showing the row-scanning algorithm with colored rooms:

```bash
# Animated step-by-step parsing
python -m analysis.visualizer tests/fixtures/u_shaped.txt

# Faster animation
python -m analysis.visualizer tests/fixtures/spiral_right.txt --delay 0.02

# Static final state only
python -m analysis.visualizer tests/fixtures/rooms.txt --no-animate
```

---

## Format Requirements

### Room Names

Room names must be enclosed in parentheses within the floor plan:

| Format | Valid | Example |
|--------|-------|---------|
| `(kitchen)` | ✓ | Standard room name |
| `(living room)` | ✓ | Name with spaces |
| `kitchen` | ✗ | No parentheses |
| `[kitchen]` | ✗ | Wrong brackets |

### Hardcoded Characters

The following constants are defined in `src/parser.py` and can be modified to support different floor plan formats:

**Wall characters:**
```python
WALL_CHARS = {'-', '|', '+', '/', '\\'}
```

**Chair characters:**
```python
CHAIR_CHARS = {'W', 'P', 'S', 'C'}
```

To add new chair types or wall characters, modify these constants in `src/parser.py`.

---

## Wall Characters

| Char | Usage |
|------|-------|
| `-` | Horizontal wall |
| `\|` | Vertical wall |
| `+` | Corner/junction |
| `/` | Diagonal wall |
| `\` | Diagonal wall |

---

## Chair Types

| Code | Type |
|------|------|
| W | Wooden chair |
| P | Plastic chair |
| S | Sofa chair |
| C | China chair |

---

## Edge Cases Handled

| Case | Example | Handling |
|------|---------|----------|
| Chairs adjacent to walls | `\|WW\|` | Correctly counted |
| Consecutive chairs | `WWWW` | Each counted individually |
| Double walls | `\|\|` | Properly separates rooms |
| Diagonal walls | `/`, `\` | Treated as walls |
| Room names with spaces | `(living room)` | Supported |
| L-shaped rooms | See l_shaped.txt | Merged via vertical scan |
| Room inside room | See donut.txt | Inner/outer separate |
| Rooms with no chairs | See no_chairs.txt | Included with zero counts |
| Unnamed rooms | Hallways, outside | Excluded from output |
| Unnamed rooms with chairs | External chair | Warning to stderr |
| Thin diagonal walls | See below | NOT a valid room boundary |

**Thin diagonal walls (width 1) are not supported:**

```
    / /
   / /
  / /
 / /
```

This pattern does not form a valid enclosed room. Diagonal walls must be part of a properly enclosed structure with horizontal/vertical walls to define room boundaries.

---

## Example

**Input (simple.txt):**
```
+--------+--------+
|        |        |
| (bed)  | (bath) |
|   W    |   P    |
|        |        |
+--------+--------+
```

**Output:**
```
total:
W: 1, P: 1, S: 0, C: 0
bath:
W: 0, P: 1, S: 0, C: 0
bed:
W: 1, P: 0, S: 0, C: 0
```


