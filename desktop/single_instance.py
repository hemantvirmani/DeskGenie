"""Single-instance enforcement for DeskGenie desktop app.

Uses a sentinel TCP socket bound to a fixed port. If already bound,
another instance is running — focus its window and exit.
"""

import socket
import sys
from typing import Optional

_SENTINEL_PORT = 41956  # one above the app port
_sentinel_socket: Optional[socket.socket] = None


def acquire() -> bool:
    """Try to acquire the single-instance lock.

    Returns:
        bool: True if this is the first instance, False otherwise.
    """
    global _sentinel_socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    try:
        sock.bind(('127.0.0.1', _SENTINEL_PORT))
        _sentinel_socket = sock
        return True
    except OSError:
        sock.close()
        return False


def focus_existing_window() -> None:
    """Bring the already-running DeskGenie window to the foreground (Windows)."""
    if sys.platform == 'win32':
        try:
            import ctypes
            hwnd = ctypes.windll.user32.FindWindowW(None, 'DeskGenie')
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 9)   # SW_RESTORE
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass


def release() -> None:
    """Release the sentinel socket on clean exit."""
    global _sentinel_socket
    if _sentinel_socket:
        _sentinel_socket.close()
        _sentinel_socket = None
