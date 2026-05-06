#!/usr/bin/env python3
"""
Utility helpers for ClipVault - contains all helper functions.
"""

import os
import sys
import time
import shutil


def print_banner():
    """Print the ClipVault banner."""
    banner = """
╔══════════════════════════════════════════════════╗
║                                                  ║
║   📋 ClipVault v1.0.0                            ║
║   Lightweight Clipboard Intelligent Manager      ║
║   轻量级剪贴板智能管理引擎                         ║
║                                                  ║
║   Zero Dependencies • Cross-Platform • Smart      ║
║                                                  ║
╚══════════════════════════════════════════════════╝
"""
    print(f"\033[36m{banner}\033[0m")


def print_success(msg: str):
    """Print a success message in green."""
    print(f"\033[32m{msg}\033[0m")


def print_error(msg: str):
    """Print an error message in red."""
    print(f"\033[31m{msg}\033[0m", file=sys.stderr)


def print_info(msg: str):
    """Print an info message in cyan."""
    print(f"\033[36m{msg}\033[0m")


def print_warning(msg: str):
    """Print a warning message in yellow."""
    print(f"\033[33m{msg}\033[0m")


def format_size(size: int) -> str:
    """Format byte size to human-readable string."""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    else:
        return f"{size / (1024 * 1024):.1f}MB"


def format_time(timestamp: float) -> str:
    """Format Unix timestamp to relative time string."""
    if not timestamp:
        return '-'

    now = time.time()
    diff = now - timestamp

    if diff < 60:
        return f"{int(diff)}s ago"
    elif diff < 3600:
        return f"{int(diff / 60)}m ago"
    elif diff < 86400:
        return f"{int(diff / 3600)}h ago"
    elif diff < 604800:
        return f"{int(diff / 86400)}d ago"
    else:
        return time.strftime('%m-%d', time.localtime(timestamp))


def print_table(headers: list, rows: list):
    """Print a formatted table.

    Args:
        headers: List of header strings
        rows: List of row lists
    """
    if not rows:
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Add padding
    col_widths = [w + 2 for w in col_widths]

    # Print header
    header_line = ''
    for i, h in enumerate(headers):
        header_line += f"\033[1;36m{h:<{col_widths[i]}}\033[0m"
    print(header_line)

    # Print separator
    separator = ''
    for w in col_widths:
        separator += '─' * w
    print(f"\033[2m{separator}\033[0m")

    # Print rows
    for row in rows:
        line = ''
        for i, cell in enumerate(row):
            if i < len(col_widths):
                line += f"{str(cell):<{col_widths[i]}}"
        print(line)


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def get_terminal_size() -> tuple:
    """Get terminal size (width, height)."""
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except Exception:
        return 80, 24


def truncate_text(text: str, max_len: int = 50, suffix: str = '...') -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)
