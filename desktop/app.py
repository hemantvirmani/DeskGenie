"""
DeskGenie Desktop App — Entry Point

Modes
-----
GUI mode (default)
    python desktop/app.py
    DeskGenie.exe

CLI mode
    python desktop/app.py --query "your query"
    DeskGenie.exe --query "your query"

Dev vs Production
-----------------
In dev  (sys.frozen is False): runs directly, hot paths use source files.
In prod (sys.frozen is True):  PyInstaller bundle, paths resolved via sys._MEIPASS.
"""

import sys
import os

# ---------------------------------------------------------------------------
# 1. Path setup — must happen before any project-relative imports
# ---------------------------------------------------------------------------
_is_frozen: bool = getattr(sys, 'frozen', False)

if _is_frozen:
    _base_dir: str = sys._MEIPASS          # type: ignore[attr-defined]
else:
    # desktop/app.py lives one level below the project root
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if _base_dir not in sys.path:
    sys.path.insert(0, _base_dir)

# ---------------------------------------------------------------------------
# 2. Load .env (dev convenience — prod uses system environment variables)
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    _env_file = os.path.join(_base_dir, '.env')
    if os.path.exists(_env_file):
        load_dotenv(_env_file)
except ImportError:
    pass  # python-dotenv not installed — silently skip

# ---------------------------------------------------------------------------
# 3. Detect mode
# ---------------------------------------------------------------------------
_is_cli: bool = '--query' in sys.argv or '--test' in sys.argv

# ---------------------------------------------------------------------------
# 4. Windows console allocation for CLI mode inside a windowed exe
#    print() output is invisible in a --windowed build unless we allocate
#    a console explicitly. On Mac/Linux this is never needed.
# ---------------------------------------------------------------------------
if _is_cli and _is_frozen and sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.AllocConsole()
    sys.stdout = open('CONOUT$', 'w', encoding='utf-8')
    sys.stderr = open('CONOUT$', 'w', encoding='utf-8')
    sys.stdin  = open('CONIN$',  'r', encoding='utf-8')


# ---------------------------------------------------------------------------
# CLI mode
# ---------------------------------------------------------------------------
def _run_cli() -> None:
    """Delegate to app/main.py CLI handling (--query and --test)."""
    from utils.log_streamer import set_global_logger, ConsoleLogger
    set_global_logger(ConsoleLogger(task_id='cli'))

    from app.main import main as _main
    _main()


# ---------------------------------------------------------------------------
# GUI mode
# ---------------------------------------------------------------------------
def _run_gui() -> None:
    """Start the FastAPI server, then open a native pywebview window."""
    import webview
    from desktop.single_instance import acquire, focus_existing_window, release
    from desktop.server import find_free_port, start_server_thread, wait_for_server
    from desktop.tray import create_tray

    # Enforce single instance
    if not acquire():
        focus_existing_window()
        sys.exit(0)

    try:
        port = find_free_port(41955)
        print(f'[DeskGenie] Starting on http://127.0.0.1:{port}')

        start_server_thread(port)

        if not wait_for_server(port):
            print('[DeskGenie] ERROR: Server did not start within 30 seconds. Exiting.')
            sys.exit(1)

        window = webview.create_window(
            'DeskGenie',
            f'http://127.0.0.1:{port}',
            width=1280,
            height=800,
            min_size=(800, 600),
        )

        _quit_requested: list[bool] = [False]

        def _on_closing() -> bool:
            """Hide to tray on close; only allow destroy when quit is requested."""
            if _quit_requested[0]:
                return True   # allow the window to close
            window.hide()
            return False      # cancel the default close

        window.events.closing += _on_closing

        def _quit() -> None:
            _quit_requested[0] = True
            window.destroy()

        def _on_started() -> None:
            """Called by pywebview after the GUI event loop starts."""
            create_tray(window, _quit)

        webview.start(_on_started, debug=os.environ.get('DESKGENIE_DEBUG') == '1')

    finally:
        release()

    sys.exit(0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    if _is_cli:
        _run_cli()
    else:
        _run_gui()
