from __future__ import annotations

"""Screenshot artifact helper for failed UI tests."""

from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

from config.settings import ROOT_DIR


def capture_screenshot(page: Page, name: str) -> Path:
    """
    Purpose:
        Captures a full-page screenshot with a sanitized, timestamped name.

    Why Needed:
        Failure artifacts help diagnose UI state at the exact point a test
        failed without requiring local reproduction first.

    Args:
        page: Playwright page to capture.
        name: Human-readable test or workflow name used in the filename.

    Returns:
        Path to the saved PNG screenshot.

    Notes:
        Non filename-safe characters are replaced with underscores.
    """
    screenshot_dir = ROOT_DIR / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in name)
    path = screenshot_dir / f"{safe_name}_{timestamp}.png"
    page.screenshot(path=str(path), full_page=True)
    return path
