"""App icon generation for DeskGenie desktop app.

Generates the icon at runtime using Pillow — no external icon file needed.
"""

from typing import Optional
from PIL import Image, ImageDraw, ImageFont


def _make_icon(size: int = 64) -> Image.Image:
    """Draw a rounded indigo square with 'DG' text."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = max(2, size // 10)
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=size // 5,
        fill=(99, 102, 241, 255),  # indigo-500
    )

    font_size = size // 3
    font: Optional[ImageFont.FreeTypeFont] = None
    for name in ('segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf'):
        try:
            font = ImageFont.truetype(name, font_size)
            break
        except (IOError, OSError):
            continue

    draw.text(
        (size / 2, size / 2),
        'DG',
        fill=(255, 255, 255, 255),
        font=font,
        anchor='mm',
    )
    return img


def get_tray_icon() -> Image.Image:
    """Return a 64×64 icon image for the system tray."""
    return _make_icon(64)


def get_window_icon_path(tmp_dir: str) -> str:
    """Save a 256×256 .ico file to tmp_dir and return its path (Windows title bar)."""
    import os
    path = os.path.join(tmp_dir, 'deskgenie.ico')
    img = _make_icon(256)
    img.save(path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
    return path
