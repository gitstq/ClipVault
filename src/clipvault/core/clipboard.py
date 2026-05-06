#!/usr/bin/env python3
"""
Clipboard manager - handles reading/writing to system clipboard.
Supports Linux (xclip/xsel/wl-clipboard), macOS (pbcopy/pbpaste), Windows (clip).
"""

import subprocess
import shutil
import os
import sys
import platform


class ClipboardManager:
    """Cross-platform clipboard manager with zero external dependencies."""

    def __init__(self):
        self._os = platform.system()
        self._clipboard_tool = self._detect_clipboard_tool()

    def _detect_clipboard_tool(self) -> str:
        """Detect available clipboard tool for the current platform."""
        if self._os == 'Darwin':
            return 'pbcopy'

        if self._os == 'Windows':
            return 'clip'

        # Linux - try multiple options
        if shutil.which('xclip'):
            return 'xclip'
        if shutil.which('xsel'):
            return 'xsel'
        if shutil.which('wl-copy'):
            return 'wl-copy'
        if shutil.which('wl-paste'):
            return 'wl-paste'

        # Fallback: try python-based approach
        return 'python'

    def _run_command(self, cmd: list, input_data: str = None) -> str:
        """Run a subprocess command and return output."""
        try:
            if input_data is not None:
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            return result.stdout.strip() if result.returncode == 0 else ''
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ''

    def get_text(self) -> str:
        """Get text content from system clipboard."""
        tool = self._clipboard_tool

        if tool == 'pbcopy':
            return self._run_command(['pbpaste'])

        if tool == 'clip':
            # Windows: use PowerShell for reading
            return self._run_command([
                'powershell', '-command',
                'Get-Clipboard', '-Text'
            ])

        if tool == 'xclip':
            return self._run_command(['xclip', '-selection', 'clipboard', '-o'])

        if tool == 'xsel':
            return self._run_command(['xsel', '--clipboard', '--output'])

        if tool == 'wl-paste':
            return self._run_command(['wl-paste', '--no-newline'])

        if tool == 'wl-copy':
            return ''  # wl-copy can't read

        if tool == 'python':
            return self._python_get_clipboard()

        return ''

    def set_text(self, text: str) -> bool:
        """Set text content to system clipboard."""
        if not text:
            return False

        tool = self._clipboard_tool

        if tool == 'pbcopy':
            result = self._run_command(['pbcopy'], input_data=text)
            return True

        if tool == 'clip':
            # Windows: use PowerShell for writing
            result = self._run_command(
                ['powershell', '-command', 'Set-Clipboard', '-Value', text],
                input_data=text
            )
            return True

        if tool == 'xclip':
            result = self._run_command(
                ['xclip', '-selection', 'clipboard'],
                input_data=text
            )
            return True

        if tool == 'xsel':
            result = self._run_command(
                ['xsel', '--clipboard', '--input'],
                input_data=text
            )
            return True

        if tool == 'wl-copy':
            result = self._run_command(['wl-copy'], input_data=text)
            return True

        if tool == 'wl-paste':
            return False  # wl-paste can't write

        if tool == 'python':
            return self._python_set_clipboard(text)

        return False

    def _python_get_clipboard(self) -> str:
        """Fallback: try to read clipboard using Python internals."""
        try:
            if self._os == 'Windows':
                import ctypes
                CF_UNICODETEXT = 13
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32
                user32.OpenClipboard(0)
                handle = user32.GetClipboardData(CF_UNICODETEXT)
                kernel32.GlobalLock.restype = ctypes.c_wchar_p
                text = kernel32.GlobalLock(handle)
                kernel32.GlobalUnlock(handle)
                user32.CloseClipboard()
                return text or ''
        except Exception:
            pass
        return ''

    def _python_set_clipboard(self, text: str) -> bool:
        """Fallback: try to write clipboard using Python internals."""
        try:
            if self._os == 'Windows':
                import ctypes
                CF_UNICODETEXT = 13
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32
                user32.OpenClipboard(0)
                user32.EmptyClipboard()
                # Allocate global memory
                encoding = 'utf-16-le'
                buf = (text + '\0').encode(encoding)
                h = kernel32.GlobalAlloc(0x0042, len(buf))  # GMEM_MOVEABLE | GMEM_ZEROINIT
                p = kernel32.GlobalLock(h)
                ctypes.memmove(p, buf, len(buf))
                kernel32.GlobalUnlock(h)
                user32.SetClipboardData(CF_UNICODETEXT, h)
                user32.CloseClipboard()
                return True
        except Exception:
            pass
        return False

    def is_available(self) -> bool:
        """Check if clipboard access is available."""
        return self._clipboard_tool != 'python' or self._os == 'Windows'

    def get_tool_name(self) -> str:
        """Get the name of the detected clipboard tool."""
        return self._clipboard_tool
