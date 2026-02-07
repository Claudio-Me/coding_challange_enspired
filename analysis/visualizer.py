"""
Terminal-based visualization of the room parsing algorithm.

Shows the row-scanning process with colored rooms:
- Each room gets a unique color
- Merges are animated by color propagation
- Step-by-step or animated playback
"""
import argparse
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.panel import Panel

from src.parser import WALL_CHARS, CHAIR_CHARS, is_wall, get_char
from src.room import Room


# Color palette for rooms (using rich color names)
ROOM_COLORS = [
    "red", "green", "blue", "yellow", "magenta", "cyan",
    "bright_red", "bright_green", "bright_blue", "bright_yellow",
    "bright_magenta", "bright_cyan", "orange1", "purple",
    "dark_orange", "deep_pink1", "spring_green1", "turquoise2",
]

WALL_STYLE = "white dim"
CURSOR_STYLE = "black on white"


class ParsingVisualizer:
    """Visualizes the room parsing algorithm step by step."""

    def __init__(self, floor_plan: str, delay: float = 0.1):
        self.floor_plan = floor_plan
        self.lines = floor_plan.splitlines()
        self.delay = delay
        self.console = Console()

        self.height = len(self.lines)
        self.width = max(len(line) for line in self.lines) if self.lines else 0

        # Grid storing room assignments (None = wall or unvisited)
        self.grid: list[list[Room | None]] = [
            [None] * self.width for _ in range(self.height)
        ]

        # Room tracking
        self.room_counter = 0
        self.room_colors: dict[int, str] = {}  # room.id -> color

        # Current position
        self.cursor_x = 0
        self.cursor_y = 0

        # Event log
        self.events: list[str] = []

    def _get_room_color(self, room: Room) -> str:
        """Get or assign a color for a room."""
        final_room = room.final()
        if final_room.id not in self.room_colors:
            color_idx = len(self.room_colors) % len(ROOM_COLORS)
            self.room_colors[final_room.id] = ROOM_COLORS[color_idx]
        return self.room_colors[final_room.id]

    def _render_grid(self, show_cursor: bool = True) -> Text:
        """Render the current grid state as rich Text."""
        text = Text()

        for y in range(self.height):
            for x in range(self.width):
                char = get_char(self.lines, x, y)

                # Determine style
                if show_cursor and x == self.cursor_x and y == self.cursor_y:
                    style = CURSOR_STYLE
                elif is_wall(char):
                    style = WALL_STYLE
                elif self.grid[y][x] is not None:
                    room = self.grid[y][x]
                    color = self._get_room_color(room)
                    # Use background color so blank spaces are visible
                    style = f"black on {color}"
                else:
                    style = "dim"

                text.append(char, style=style)

            text.append("\n")

        return text

    def _render_status(self) -> str:
        """Render status information."""
        unique_rooms = set()
        for row in self.grid:
            for cell in row:
                if cell is not None:
                    unique_rooms.add(cell.final().id)

        status_lines = [
            f"Position: ({self.cursor_x}, {self.cursor_y})",
            f"Rooms found: {len(unique_rooms)}",
            f"Room counter: {self.room_counter}",
        ]

        if self.events:
            status_lines.append("")
            status_lines.append("Recent events:")
            for event in self.events[-3:]:
                status_lines.append(f"  {event}")

        return "\n".join(status_lines)

    def _make_panel(self, show_cursor: bool = True) -> Panel:
        """Create a panel with grid and status."""
        grid_text = self._render_grid(show_cursor)
        status = self._render_status()

        content = Text()
        content.append(grid_text)
        content.append("\n")
        content.append(status, style="dim")

        return Panel(content, title="Room Parsing Visualization", border_style="blue")

    def run_animated(self):
        """Run the visualization with animation."""
        current_room: Room | None = None
        name_buffer: str | None = None

        with Live(self._make_panel(), console=self.console, refresh_per_second=30) as live:
            for y in range(self.height):
                current_room = None
                name_buffer = None

                for x in range(self.width):
                    self.cursor_x = x
                    self.cursor_y = y

                    char = get_char(self.lines, x, y)

                    if is_wall(char):
                        current_room = None
                        name_buffer = None
                        live.update(self._make_panel())
                        time.sleep(self.delay / 2)
                        continue

                    # Non-wall cell
                    if current_room is None:
                        self.room_counter += 1
                        current_room = Room(self.room_counter)
                        self.events.append(f"Created room {self.room_counter}")

                    # Check cell above for merge
                    if y > 0:
                        char_above = get_char(self.lines, x, y - 1)
                        if not is_wall(char_above):
                            room_above = self.grid[y - 1][x]
                            if room_above is not None:
                                final_above = room_above.final()
                                final_current = current_room.final()
                                if final_above != final_current:
                                    # Transfer color before merge
                                    old_color = self.room_colors.get(
                                        final_current.id,
                                        ROOM_COLORS[len(self.room_colors) % len(ROOM_COLORS)]
                                    )
                                    final_above.merge_with(final_current)
                                    self.events.append(
                                        f"Merged room {final_current.id} -> {final_above.id}"
                                    )

                    # Store in grid
                    self.grid[y][x] = current_room

                    # Track chairs
                    if char in CHAIR_CHARS:
                        current_room.final().chairs[char] += 1

                    # Track room name
                    if char == '(':
                        name_buffer = ""
                    elif char == ')' and name_buffer is not None:
                        current_room.final().name = name_buffer
                        self.events.append(f"Named room: '{name_buffer}'")
                        name_buffer = None
                    elif name_buffer is not None:
                        name_buffer += char

                    live.update(self._make_panel())
                    time.sleep(self.delay)

            # Final state without cursor
            self.events.append("Parsing complete!")
            live.update(self._make_panel(show_cursor=False))
            time.sleep(1)

        # Print summary
        self._print_summary()

    def run_static(self):
        """Show the final state after parsing (no animation)."""
        # Run parsing without animation
        current_room: Room | None = None
        name_buffer: str | None = None

        for y in range(self.height):
            current_room = None
            name_buffer = None

            for x in range(self.width):
                char = get_char(self.lines, x, y)

                if is_wall(char):
                    current_room = None
                    name_buffer = None
                    continue

                if current_room is None:
                    self.room_counter += 1
                    current_room = Room(self.room_counter)

                if y > 0:
                    char_above = get_char(self.lines, x, y - 1)
                    if not is_wall(char_above):
                        room_above = self.grid[y - 1][x]
                        if room_above is not None:
                            final_above = room_above.final()
                            final_current = current_room.final()
                            if final_above != final_current:
                                final_above.merge_with(final_current)

                self.grid[y][x] = current_room

                if char in CHAIR_CHARS:
                    current_room.final().chairs[char] += 1

                if char == '(':
                    name_buffer = ""
                elif char == ')' and name_buffer is not None:
                    current_room.final().name = name_buffer
                    name_buffer = None
                elif name_buffer is not None:
                    name_buffer += char

        # Show final state
        self.console.print(self._make_panel(show_cursor=False))
        self._print_summary()

    def _print_summary(self):
        """Print parsing summary."""
        self.console.print()

        # Collect unique rooms
        seen_ids: set[int] = set()
        rooms: list[Room] = []

        for row in self.grid:
            for cell in row:
                if cell is not None:
                    room = cell.final()
                    if room.id not in seen_ids:
                        seen_ids.add(room.id)
                        if room.name is not None:
                            rooms.append(room)

        rooms.sort(key=lambda r: r.name or "")

        self.console.print("[bold]Parsing Summary:[/bold]")
        self.console.print(f"  Total rooms found: {len(seen_ids)}")
        self.console.print(f"  Named rooms: {len(rooms)}")
        self.console.print()

        if rooms:
            self.console.print("[bold]Room Details:[/bold]")
            for room in rooms:
                color = self._get_room_color(room)
                chair_str = ", ".join(f"{k}: {v}" for k, v in room.chairs.items())
                # Use background color to match grid visualization
                self.console.print(
                    f"  [black on {color}] {room.name} [/]: {chair_str}"
                )


def visualize_file(file_path: str, animate: bool = True, delay: float = 0.1):
    """Visualize parsing of a floor plan file."""
    with open(file_path, 'r') as f:
        floor_plan = f.read()

    viz = ParsingVisualizer(floor_plan, delay=delay)

    if animate:
        viz.run_animated()
    else:
        viz.run_static()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize the room parsing algorithm"
    )
    parser.add_argument(
        "file",
        help="Path to floor plan file"
    )
    parser.add_argument(
        "--no-animate", "-n",
        action="store_true",
        help="Show final state only (no animation)"
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=0.05,
        help="Delay between steps in seconds (default: 0.05)"
    )

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    visualize_file(args.file, animate=not args.no_animate, delay=args.delay)


if __name__ == "__main__":
    main()
