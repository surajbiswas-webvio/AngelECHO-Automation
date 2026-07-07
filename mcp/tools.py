from __future__ import annotations

"""Beginner-friendly Playwright MCP tool wrappers.

Purpose:
    This file exposes small, named actions for navigation, inspection, locator
    discovery, screenshots, and debugging.

Why this exists:
    New developers can use these methods without knowing every Playwright API
    detail. Advanced teams can also forward a tool call to an external MCP
    server through PlaywrightMCPClient.

How to use:
    In a pytest test, request `mcp_tools` and call methods such as
    `mcp_tools.navigate(page, "/dashboard")` or
    `mcp_tools.discover_locators(page)`.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import Locator, Page

from config.settings import Settings
from mcp.playwright_client import PlaywrightMCPClient, MCPResponse
from utils.logger import get_logger


class PlaywrightMCPTools:
    """
    Purpose:
        Groups reusable MCP-style browser helper actions.

    Why this is needed:
        Tests, page-object authors, and debugging scripts often need the same
        small actions: navigate, inspect, discover locators, and capture
        screenshots. This class keeps those actions easy to find.

    Args:
        settings: Central runtime settings.
        client: Optional external Playwright MCP JSON-RPC client.

    Returns:
        Tool wrapper object used by pytest fixtures and scripts.
    """

    def __init__(self, settings: Settings, client: PlaywrightMCPClient | None = None) -> None:
        self.settings = settings
        self.client = client
        self.logger = get_logger(self.__class__.__name__)

    def navigate(self, page: Page, path_or_url: str = "") -> str:
        """
        Purpose:
            Navigates a page to either an app route or a full URL.

        Why this is needed:
            MCP workflows should use the same BASE_URL rules as the normal page
            objects when a relative route is supplied.

        Args:
            page: Playwright Page to navigate.
            path_or_url: Full URL like "https://..." or app route like
                "/dashboard". Empty string means the configured base URL.

        Returns:
            The final page URL after navigation.
        """
        target = path_or_url if path_or_url.startswith(("http://", "https://")) else self.settings.url_for(path_or_url)
        self.logger.info("MCP navigate: %s", target)
        page.goto(target, wait_until="domcontentloaded")
        return page.url

    def inspect_element(self, page: Page, selector: str) -> dict[str, Any]:
        """
        Purpose:
            Reads useful information from the first element matching a selector.

        Why this is needed:
            Element inspection helps developers understand what locator to use
            and why a test may not be finding a control.

        Args:
            page: Playwright Page containing the element.
            selector: CSS selector to inspect.

        Returns:
            Dictionary containing tag name, text, visibility, and attributes.
        """
        locator = page.locator(selector).first
        return self._describe_locator(locator)

    def discover_locators(self, page: Page, limit: int = 25) -> list[dict[str, str]]:
        """
        Purpose:
            Finds likely stable locators on the current page.

        Why this is needed:
            Beginner developers can quickly see data-testid, role, label, text,
            id, and name candidates before writing a page object.

        Args:
            page: Playwright Page to inspect.
            limit: Maximum number of locator suggestions to return.

        Returns:
            List of locator suggestion dictionaries.
        """
        suggestions = page.evaluate(
            """
            (limit) => {
                const results = [];
                const push = (type, value, reason) => {
                    if (!value || results.length >= limit) return;
                    const exists = results.some((item) => item.type === type && item.value === value);
                    if (!exists) results.push({ type, value, reason });
                };
                const visibleText = (element) => (element.innerText || element.textContent || "").trim().replace(/\\s+/g, " ");
                for (const element of document.querySelectorAll("body *")) {
                    const testId = element.getAttribute("data-testid") || element.getAttribute("data-test");
                    push("test_id", testId, "Preferred because product-owned test ids are stable.");
                    push("id", element.id ? `#${CSS.escape(element.id)}` : "", "Useful when the id is stable.");
                    push("name", element.getAttribute("name"), "Useful for form fields.");
                    const role = element.getAttribute("role");
                    if (role) push("role", role, "Useful with page.get_by_role(...).");
                    const ariaLabel = element.getAttribute("aria-label");
                    push("label", ariaLabel, "Useful with page.get_by_label(...).");
                    const text = visibleText(element);
                    if (text && text.length <= 80 && ["BUTTON", "A", "LABEL", "SPAN", "DIV"].includes(element.tagName)) {
                        push("text", text, "Useful when visible text is stable and user-facing.");
                    }
                    if (results.length >= limit) break;
                }
                return results;
            }
            """,
            limit,
        )
        return list(suggestions)

    def capture_screenshot(self, page: Page, name: str = "mcp-debug") -> Path:
        """
        Purpose:
            Saves a screenshot of the current page for MCP debugging.

        Why this is needed:
            Screenshots make it easier to understand locator failures, page
            state, and visual regressions after an MCP action.

        Args:
            page: Playwright Page to capture.
            name: Human-readable filename prefix.

        Returns:
            Path to the saved PNG screenshot.
        """
        self.settings.mcp_screenshot_dir.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in name).strip("_") or "mcp-debug"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.settings.mcp_screenshot_dir / f"{safe_name}_{timestamp}.png"
        page.screenshot(path=str(path), full_page=True)
        self.logger.info("MCP screenshot captured: %s", path)
        return path

    def debug_page_state(self, page: Page) -> dict[str, Any]:
        """
        Purpose:
            Returns a compact snapshot of the current page state.

        Why this is needed:
            Debug output helps developers see the URL, title, visible buttons,
            inputs, and locator candidates without opening browser devtools.

        Args:
            page: Playwright Page to summarize.

        Returns:
            Dictionary with title, URL, counts, and locator suggestions.
        """
        return {
            "url": page.url,
            "title": page.title(),
            "buttons": page.locator("button").count(),
            "inputs": page.locator("input, textarea, select").count(),
            "links": page.locator("a").count(),
            "locator_suggestions": self.discover_locators(page, limit=10),
        }

    def call_mcp_server_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> MCPResponse:
        """
        Purpose:
            Calls a tool exposed by an external Playwright MCP server.

        Why this is needed:
            Some teams centralize browser actions in a separate MCP server.
            This method lets framework code call those tools when configured.

        Args:
            tool_name: Name of the server-side MCP tool.
            arguments: Input payload expected by that tool.

        Returns:
            MCPResponse from PlaywrightMCPClient.
        """
        if self.client is None:
            raise RuntimeError("No Playwright MCP client was provided to PlaywrightMCPTools.")
        return self.client.call_tool(tool_name, arguments)

    @staticmethod
    def _describe_locator(locator: Locator) -> dict[str, Any]:
        """
        Purpose:
            Converts a Playwright Locator into a serializable description.

        Why this is needed:
            Tests and logs can print dictionaries easily, while raw Locator
            objects are tied to a live browser session.

        Args:
            locator: First matched element locator.

        Returns:
            Dictionary with element details.
        """
        count = locator.count()
        if count == 0:
            return {"found": False}
        details = locator.evaluate(
            """
            (element) => {
                const attrs = {};
                for (const attr of element.attributes) attrs[attr.name] = attr.value;
                return {
                    tag: element.tagName.toLowerCase(),
                    text: (element.innerText || element.textContent || "").trim(),
                    attributes: attrs,
                };
            }
            """
        )
        details["found"] = True
        details["visible"] = locator.is_visible()
        details["enabled"] = locator.is_enabled()
        return details
