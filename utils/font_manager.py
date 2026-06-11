"""
DeepDive AI — Font Download Manager

Ensures the required Unicode TTF fonts are available in the fonts/ directory.
"""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"

FONT_URLS = {
    "NotoSansDevanagari-Regular.ttf": (
        "https://raw.githubusercontent.com/notofonts/noto-fonts/"
        "main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
    ),
    "NotoSansTelugu-Regular.ttf": (
        "https://raw.githubusercontent.com/notofonts/noto-fonts/"
        "main/hinted/ttf/NotoSansTelugu/NotoSansTelugu-Regular.ttf"
    ),
}


def ensure_fonts_exist() -> None:
    """Ensure Noto Sans Devanagari and Telugu fonts are downloaded locally."""
    FONTS_DIR.mkdir(parents=True, exist_ok=True)

    for font_name, url in FONT_URLS.items():
        font_path = FONTS_DIR / font_name
        if font_path.exists():
            continue

        logger.info("Downloading font %s from Google Fonts...", font_name)
        try:
            # Set user agent to avoid bot detection blocks
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req) as response:
                data = response.read()
                font_path.write_bytes(data)
            logger.info("Successfully downloaded font: %s", font_name)
        except Exception as exc:
            logger.error("Failed to download font %s: %s", font_name, exc)
            # Create a placeholder empty file or raise to prevent crashing
            raise RuntimeError(
                f"Font download failed for {font_name}. "
                "Multilingual PDF generation requires this font. "
                f"Error: {exc}"
            ) from exc


def get_font_path(font_name: str) -> str:
    """Return the absolute path of the requested font file."""
    return str(FONTS_DIR / font_name)
