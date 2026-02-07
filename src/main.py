"""
Chair Counter CLI - reads ASCII floor plans and counts chairs per room.

Usage: python -m src.main <input_file>

Reads an ASCII floor plan from the specified file, parses rooms and chairs,
and outputs the chair counts to stdout.
"""
import sys
from .parser import parse
from .formatter import format_output


def main() -> None:
    """
    Main entry point for the CLI.

    - Validates command line arguments
    - Reads the floor plan file
    - Parses rooms and counts chairs
    - Outputs formatted result to stdout
    """
    # Validate arguments
    if len(sys.argv) != 2:
        print("Usage: python -m src.main <input_file>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]

    # Read floor plan
    try:
        with open(input_file, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse and format output
    rooms = parse(text)
    output = format_output(rooms)

    # Print result (no trailing newline since format_output includes it)
    print(output, end='')


if __name__ == '__main__':
    main()
