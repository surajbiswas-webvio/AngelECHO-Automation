from __future__ import annotations

"""Browser and page management helpers for Playwright MCP workflows.

Purpose:
    This file creates browser contexts and pages that MCP-style tools can use.

Why this exists:
    The framework already has pytest fixtures for browser startup and login
    storage state. MCP workflows should reuse those fixtures instead of
    launching unmanaged browsers in every helper.

How to use:
    Request the `mcp_browser_manager` fixture in a test, then call
    `open_page()` to get a page that uses the same base URL and optional
    authenticated storage state as the rest of the framework.
"""

from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import Settings
from utils.logger import get_logger


class MCPBrowserManager:
    """
    Purpose:
        Creates and tracks browser contexts/pages for MCP helper actions.

    Why this is needed:
        MCP utilities often need a page for inspection, screenshots, and
        debugging. This manager gives them one consistent way to open pages
        without bypassing the existing pytest browser fixture.

    Args:
        browser: Session-scoped Playwright Browser from conftest.py.
        settings: Central runtime settings.
        storage_state_path: Optional authenticated storage-state JSON path.

    Returns:
        Manager object used by `mcp_tools` and validation tests.
    """

    def __init__(self, browser: Browser, settings: Settings, storage_state_path: Path | None = None) -> None:
        self.browser = browser
        self.settings = settings
        self.storage_state_path = storage_state_path
        self.logger = get_logger(self.__class__.__name__)
        self._contexts: list[BrowserContext] = []

    def new_context(self, *, authenticated: bool = True) -> BrowserContext:
        """
        Purpose:
            Creates a browser context configured for MCP work.

        Why this is needed:
            Contexts isolate cookies, local storage, timeouts, and tracing from
            other tests while still allowing authenticated storage reuse.

        Args:
            authenticated: When True, loads the saved login storage state if
                one was provided by the framework.

        Returns:
            A Playwright BrowserContext.
        """
        storage_state = str(self.storage_state_path) if authenticated and self.storage_state_path else None
        context = self.browser.new_context(base_url=self.settings.base_url, storage_state=storage_state)
        context.set_default_timeout(self.settings.default_timeout_ms)
        self._contexts.append(context)
        return context

    def open_page(self, path: str = "", *, authenticated: bool = True) -> Page:
        """
        Purpose:
            Opens a page for MCP actions and optionally navigates to a route.

        Why this is needed:
            Most MCP actions need a real Playwright Page. This helper avoids
            repeating context creation and URL construction.

        Args:
            path: Optional app route such as "/dashboard". Empty string opens
                a blank page so callers can navigate later.
            authenticated: Whether to reuse the login storage state.

        Returns:
            A Playwright Page ready for inspection or actions.
        """
        context = self.new_context(authenticated=authenticated)
        page = context.new_page()
        if path:
            page.goto(self.settings.url_for(path), wait_until="domcontentloaded")
        return page

    def close_all(self) -> None:
        """
        Purpose:
            Closes all MCP-created contexts.

        Why this is needed:
            Tests should release pages and contexts after each test so videos,
            traces, cookies, and memory do not leak into later tests.

        Args:
            None.

        Returns:
            None.
        """
        while self._contexts:
            context = self._contexts.pop()
            context.close()

    @contextmanager
    def managed_page(self, path: str = "", *, authenticated: bool = True) -> Generator[Page, None, None]:
        """
        Purpose:
            Provides a context-manager style page for standalone scripts.

        Why this is needed:
            Outside pytest, a developer may still want automatic cleanup after
            a short MCP exploration script.

        Args:
            path: Optional app route to open.
            authenticated: Whether to reuse the login storage state.

        Returns:
            Generator yielding one Playwright Page.
        """
        page = self.open_page(path=path, authenticated=authenticated)
        try:
            yield page
        finally:
            self.close_all()
