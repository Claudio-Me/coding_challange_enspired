# Chair Counter

A command-line tool that reads ASCII floor plans and counts chairs per room.

The core solution is in the **`src/`** directory. Everything else (`tests/`, `analysis/`) is optional supplementary material.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main <input_file>
```

Example:
```bash
python -m src.main rooms.txt
```

Output:
```
total:
W: 14, P: 7, S: 3, C: 1
balcony:
W: 0, P: 2, S: 0, C: 0
bathroom:
W: 0, P: 1, S: 0, C: 0
...
```

## Algorithm

The parser uses a row scanning algorithm with union-find style merging:

1. Scan the grid row by row, left to right
2. Assign each non-wall cell to a Room
3. When crossing a wall or starting a new line, create a new Room
4. When a cell connects to the cell above (no wall), merge rooms
5. Extract room names from `(room name)` patterns
6. Count chairs (`W`, `P`, `S`, `C`) in each room

Time complexity: **O(N)** where N is the number of characters in the input.

## Project Structure

```
├── src/                        # Core solution
│   ├── main.py                 #   CLI entry point
│   ├── parser.py               #   Row scanning and room merging
│   ├── grid.py                 #   Grid class for floor plan data
│   ├── formatter.py            #   Output formatting
│   └── room.py                 #   Room class with merge support
│
├── tests/                      # Optional: test suite (pytest)
│   ├── test_room.py            #   Unit tests for Room
│   ├── test_parser.py          #   Unit tests for parser
│   ├── test_integration.py     #   Integration tests with fixtures
│   └── test_edge_cases.py      #   Edge case coverage
│
└── analysis/                   # Optional: performance analysis
    ├── performance.ipynb       #   Benchmarks (Jupyter notebook)
    └── visualizer.py           #   Animated terminal visualization
```

## Running Tests (optional)

```bash
pytest tests/ -v
```

## Performance Analysis (optional)

- **`performance.html`** - Benchmarks verifying time and space complexity (time vs grid size, time vs room count, memory usage)
- **`visualizer.py`** - A fun terminal visualization to watch the row-scanning algorithm in action

```bash
python -m analysis.visualizer rooms.txt
```