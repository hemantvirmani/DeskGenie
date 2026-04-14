"""System tray icon for DeskGenie desktop app."""

import threading
from typing import Callable

import pystray
from desktop.icon import get_tray_icon


def create_tray(window, on_quit: Callable[[], None]) -> pystray.Icon:
    """Create and start the system tray icon in a daemon thread.

    Args:
        window: The pywebview window instance (for show/hide).
        on_quit: Callback invoked when the user selects Quit from the tray menu.

    Returns:
        pystray.Icon: The running tray icon instance.
    """

    def _on_show(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        window.show()

    def _on_quit(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        icon.stop()
        on_quit()

    menu = pystray.Menu(
        pystray.MenuItem('Open DeskGenie', _on_show, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Quit', _on_quit),
    )

    icon = pystray.Icon('DeskGenie', get_tray_icon(), 'DeskGenie', menu)
    threading.Thread(target=icon.run, daemon=True, name='deskgenie-tray').start()
    return icon
