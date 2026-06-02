from __future__ import annotations

from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

from config.settings import ROOT_DIR


def capture_screenshot(page: Page, name: str) -> Path:
    screenshot_dir = ROOT_DIR / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in name)
    path = screenshot_dir / f"{safe_name}_{timestamp}.png"
    page.screenshot(path=str(path), full_page=True)
    return path

