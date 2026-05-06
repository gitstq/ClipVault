#!/usr/bin/env python3
"""
TUI (Terminal User Interface) for ClipVault.
A lightweight terminal UI for browsing and managing clipboard history.
"""

import sys
import os
import time
from typing import Optional

from clipvault.utils.helpers import (
    format_size, format_time, clear_screen, get_terminal_size
)


class ClipVaultTUI:
    """Terminal UI for ClipVault clipboard browser."""

    # Color codes
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BG_BLUE = '\033[44m'
    BG_GRAY = '\033[100m'

    def __init__(self, engine):
        """Initialize TUI with engine reference.

        Args:
            engine: ClipVaultEngine instance
        """
        self.engine = engine
        self.items = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.filter_category = None
        self.search_query = ''
        self.mode = 'browse'  # browse, search, detail, help
        self.detail_item = None

    def run(self):
        """Run the TUI main loop."""
        # Check if terminal supports it
        if not sys.stdout.isatty():
            print("TUI requires an interactive terminal.")
            print("Use 'clipvault list' for non-interactive mode.")
            return

        self._load_items()
        if not self.items:
            print("📋 Clipboard history is empty.")
            print("Start monitoring with: clipvault watch")
            return

        self._draw()
        self._input_loop()

    def _load_items(self):
        """Load items from storage."""
        self.items = self.engine.storage.list_clips(
            limit=100,
            category=self.filter_category
        )
        if self.selected_index >= len(self.items):
            self.selected_index = max(0, len(self.items) - 1)

    def _draw(self):
        """Draw the TUI screen."""
        clear_screen()
        width, height = get_terminal_size()

        # Header
        self._draw_header(width)

        # Items list
        visible_height = height - 6  # Reserve space for header/footer
        if self.mode == 'detail' and self.detail_item:
            self._draw_detail(width, visible_height)
        elif self.mode == 'help':
            self._draw_help(width, visible_height)
        else:
            self._draw_list(width, visible_height)

        # Footer
        self._draw_footer(width)

    def _draw_header(self, width: int):
        """Draw the header bar."""
        title = "📋 ClipVault"
        if self.filter_category:
            title += f" [{self.filter_category}]"
        if self.search_query:
            title += f" 🔎 {self.search_query}"

        # Right-align item count
        count_str = f"{len(self.items)} items"
        padding = width - len(title) - len(count_str) - 4
        if padding < 0:
            padding = 0

        print(f"{self.BG_BLUE}{self.WHITE}{self.BOLD} {title}{' ' * padding}{count_str} {self.RESET}")
        print(f"{self.CYAN}{'─' * width}{self.RESET}")

    def _draw_list(self, width: int, visible_height: int):
        """Draw the items list."""
        if not self.items:
            print(f"\n{self.DIM}  No items found.{self.RESET}")
            return

        # Adjust scroll
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_height:
            self.scroll_offset = self.selected_index - visible_height + 1

        for i in range(self.scroll_offset, min(self.scroll_offset + visible_height, len(self.items))):
            item = self.items[i]
            is_selected = (i == self.selected_index)

            # Selection indicator
            if is_selected:
                prefix = f"{self.BG_BLUE}{self.WHITE}{self.BOLD} ▶ {self.RESET}"
            else:
                prefix = "   "

            # Pin indicator
            pin = "📌" if item['pinned'] else "  "

            # Category icon
            cat_icon = self.engine._category_icon(item['category'])

            # ID
            id_str = f"#{item['id']:<4}"

            # Title
            title = item['title'] or item['content'][:35]
            max_title_len = width - 30
            if len(title) > max_title_len:
                title = title[:max_title_len - 3] + "..."

            # Size and time
            size = format_size(len(item['content']))
            time_str = format_time(item['created_at'])

            # Category badge
            cat_str = f"{item['category']}"

            if is_selected:
                line = f"{prefix}{pin} {self.BOLD}{id_str}{self.RESET} {cat_icon} {self.YELLOW}{cat_str:<8}{self.RESET} {title} {self.DIM}{size} {time_str}{self.RESET}"
            else:
                line = f"{prefix}{pin} {id_str} {cat_icon} {cat_str:<8} {self.DIM}{title} {size} {time_str}{self.RESET}"

            print(line)

    def _draw_detail(self, width: int, visible_height: int):
        """Draw item detail view."""
        if not self.detail_item:
            return

        item = self.detail_item
        cat_icon = self.engine._category_icon(item['category'])

        print(f"\n{self.BOLD}  {cat_icon} Item #{item['id']}{self.RESET}")
        print(f"  Category:  {item['category']}")
        print(f"  Pinned:    {'Yes' if item['pinned'] else 'No'}")
        print(f"  Copies:    {item['copy_count']}")
        print(f"  Size:      {format_size(len(item['content']))}")
        print(f"  Created:   {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['created_at']))}")
        print(f"\n{self.CYAN}{'─' * min(width, 60)}{self.RESET}")
        print(f"\n{self.WHITE}{self.BOLD}  Content:{self.RESET}")

        # Display content with line numbers
        lines = item['content'].split('\n')
        max_lines = visible_height - 12
        for i, line in enumerate(lines[:max_lines]):
            line_num = f"{i + 1:<4}"
            # Truncate long lines
            max_line_len = width - 8
            if len(line) > max_line_len:
                line = line[:max_line_len - 3] + "..."
            print(f"  {self.DIM}{line_num}{self.RESET}{line}")

        if len(lines) > max_lines:
            print(f"  {self.DIM}... ({len(lines) - max_lines} more lines){self.RESET}")

    def _draw_help(self, width: int, visible_height: int):
        """Draw help screen."""
        help_lines = [
            ("Navigation", ""),
            ("  ↑/↓ or j/k", "Move selection up/down"),
            ("  PgUp/PgDn", "Scroll page up/down"),
            ("  Home/End", "Jump to first/last item"),
            ("", ""),
            ("Actions", ""),
            ("  Enter", "View item details"),
            ("  y", "Copy selected item to clipboard"),
            ("  p", "Toggle pin on selected item"),
            ("  d", "Delete selected item"),
            ("", ""),
            ("Search & Filter", ""),
            ("  /", "Search mode"),
            ("  f", "Filter by category"),
            ("  Esc", "Clear search/filter / Back"),
            ("", ""),
            ("Other", ""),
            ("  r", "Refresh list"),
            ("  s", "Show statistics"),
            ("  q", "Quit"),
        ]

        for label, desc in help_lines:
            if not label and not desc:
                print()
            elif not desc:
                print(f"  {self.BOLD}{self.CYAN}{label}{self.RESET}")
            else:
                print(f"  {self.YELLOW}{label:<20}{self.RESET} {self.DIM}{desc}{self.RESET}")

    def _draw_footer(self, width: int):
        """Draw the footer bar."""
        if self.mode == 'browse':
            footer = " ↑↓ Navigate │ Enter Detail │ y Copy │ p Pin │ d Delete │ / Search │ f Filter │ h Help │ q Quit "
        elif self.mode == 'detail':
            footer = " Esc Back │ y Copy │ p Pin │ d Delete │ q Quit "
        elif self.mode == 'search':
            footer = f" 🔎 Search: {self.search_query}_ │ Enter Confirm │ Esc Cancel "
        elif self.mode == 'help':
            footer = " Esc Back │ q Quit "
        else:
            footer = ""

        padding = width - len(footer) - 2
        if padding < 0:
            padding = 0
        print(f"{self.CYAN}{'─' * width}{self.RESET}")
        print(f"{self.BG_GRAY}{self.WHITE} {footer}{' ' * padding}{self.RESET}")

    def _input_loop(self):
        """Main input loop."""
        try:
            while True:
                # Read single keypress
                key = self._read_key()

                if key == 'q':
                    break
                elif key == 'h':
                    self.mode = 'help'
                    self._draw()
                elif self.mode == 'help':
                    if key in ('\x1b', 'escape'):
                        self.mode = 'browse'
                        self._draw()
                elif self.mode == 'search':
                    self._handle_search_input(key)
                elif self.mode == 'detail':
                    self._handle_detail_input(key)
                else:
                    self._handle_browse_input(key)
        except KeyboardInterrupt:
            pass

        # Cleanup
        clear_screen()
        print(f"\n{self.CYAN}👋 ClipVault TUI closed.{self.RESET}\n")

    def _handle_browse_input(self, key: str):
        """Handle input in browse mode."""
        if key in ('up', 'k'):
            if self.selected_index > 0:
                self.selected_index -= 1
                self._draw()
        elif key in ('down', 'j'):
            if self.selected_index < len(self.items) - 1:
                self.selected_index += 1
                self._draw()
        elif key == 'pgup':
            self.selected_index = max(0, self.selected_index - 10)
            self._draw()
        elif key == 'pgdn':
            self.selected_index = min(len(self.items) - 1, self.selected_index + 10)
            self._draw()
        elif key == 'home':
            self.selected_index = 0
            self._draw()
        elif key == 'end':
            self.selected_index = len(self.items) - 1
            self._draw()
        elif key == 'enter':
            if self.items:
                self.detail_item = self.items[self.selected_index]
                self.mode = 'detail'
                self._draw()
        elif key == 'y':
            if self.items:
                item = self.items[self.selected_index]
                self.engine.copy_item(item['id'])
                self._draw()
        elif key == 'p':
            if self.items:
                item = self.items[self.selected_index]
                self.engine.toggle_pin(item['id'])
                self._load_items()
                self._draw()
        elif key == 'd':
            if self.items:
                item = self.items[self.selected_index]
                self.engine.delete_item(item['id'])
                self._load_items()
                self._draw()
        elif key == '/':
            self.mode = 'search'
            self.search_query = ''
            self._draw()
        elif key == 'f':
            self._cycle_filter()
        elif key == 'r':
            self._load_items()
            self._draw()
        elif key == 's':
            clear_screen()
            self.engine.show_stats()
            input("\nPress Enter to continue...")
            self._draw()
        elif key in ('\x1b', 'escape'):
            if self.filter_category:
                self.filter_category = None
                self._load_items()
                self._draw()

    def _handle_detail_input(self, key: str):
        """Handle input in detail mode."""
        if key in ('\x1b', 'escape'):
            self.mode = 'browse'
            self.detail_item = None
            self._draw()
        elif key == 'y':
            if self.detail_item:
                self.engine.copy_item(self.detail_item['id'])
        elif key == 'p':
            if self.detail_item:
                self.engine.toggle_pin(self.detail_item['id'])
                self.detail_item = self.engine.storage.get_clip(self.detail_item['id'])
                self._draw()
        elif key == 'd':
            if self.detail_item:
                self.engine.delete_item(self.detail_item['id'])
                self.mode = 'browse'
                self.detail_item = None
                self._load_items()
                self._draw()

    def _handle_search_input(self, key: str):
        """Handle input in search mode."""
        if key in ('\x1b', 'escape'):
            self.mode = 'browse'
            self.search_query = ''
            self._load_items()
            self._draw()
        elif key == 'enter':
            if self.search_query:
                results = self.engine.search_engine.search(
                    query=self.search_query,
                    items=self.engine.storage.list_clips(limit=None),
                    mode='fuzzy'
                )
                self.items = results
                self.selected_index = 0
                self.scroll_offset = 0
            self.mode = 'browse'
            self._draw()
        elif key == 'backspace':
            self.search_query = self.search_query[:-1]
            self._draw()
        elif len(key) == 1 and key.isprintable():
            self.search_query += key
            self._draw()

    def _cycle_filter(self):
        """Cycle through category filters."""
        categories = [None, 'text', 'code', 'link', 'path', 'image', 'email', 'json', 'html', 'command']
        current_idx = categories.index(self.filter_category) if self.filter_category in categories else -1
        next_idx = (current_idx + 1) % len(categories)
        self.filter_category = categories[next_idx]
        self._load_items()
        self._draw()

    def _read_key(self) -> str:
        """Read a single keypress from terminal."""
        try:
            import tty
            import termios
        except ImportError:
            # Fallback for non-Unix systems
            return input().strip().lower()

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)

            if ch == '\x1b':  # Escape sequence
                ch2 = sys.stdin.read(1) if sys.stdin.readable() else ''
                if ch2 == '[':
                    ch3 = sys.stdin.read(1) if sys.stdin.readable() else ''
                    if ch3 == 'A':
                        return 'up'
                    elif ch3 == 'B':
                        return 'down'
                    elif ch3 == '5':
                        sys.stdin.read(1)  # Skip ~
                        return 'pgup'
                    elif ch3 == '6':
                        sys.stdin.read(1)  # Skip ~
                        return 'pgdn'
                    elif ch3 == 'H':
                        return 'home'
                    elif ch3 == 'F':
                        return 'end'
                elif ch2:
                    return 'escape'
                return 'escape'
            elif ch == '\x7f':  # Backspace
                return 'backspace'
            elif ch == '\r' or ch == '\n':
                return 'enter'
            elif ch == '\t':
                return 'tab'
            else:
                return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
