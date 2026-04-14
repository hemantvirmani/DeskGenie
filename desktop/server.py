"""Server thread management for DeskGenie desktop app."""

import socket
import threading
import time
from typing import Optional

from app import config


def find_free_port(preferred: int = config.DESKTOP_APP_PORT) -> int:
    """Return preferred port if free, otherwise the next available one.

    Args:
        preferred: Port number to try first.

    Returns:
        int: The port that was successfully bound.
    """
    port = preferred
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                if port != preferred:
                    print(f'[DeskGenie] Port {preferred} in use, using port {port} instead.')
                return port
            except OSError:
                port += 1
    raise RuntimeError('No free port found in range 41955–65534.')


def wait_for_server(port: int, timeout: int = 30) -> bool:
    """Poll the health endpoint until the server responds or timeout expires.

    Args:
        port: Port the server is listening on.
        timeout: Maximum seconds to wait.

    Returns:
        bool: True if server is ready, False if timed out.
    """
    import requests
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f'http://127.0.0.1:{port}/health', timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.4)
    return False


def start_server_thread(port: int) -> threading.Thread:
    """Start the FastAPI/uvicorn server in a daemon background thread.

    Args:
        port: Port to bind the server to.

    Returns:
        threading.Thread: The running server thread.
    """
    import uvicorn
    from app.genie_api import app as fastapi_app

    server_config = uvicorn.Config(
        fastapi_app,
        host='127.0.0.1',
        port=port,
        log_level='warning',
    )
    server = uvicorn.Server(server_config)
    thread = threading.Thread(target=server.run, daemon=True, name='deskgenie-server')
    thread.start()
    return thread
