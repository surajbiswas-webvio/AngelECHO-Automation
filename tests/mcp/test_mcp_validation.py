from __future__ import annotations

"""Validation checks for the Playwright MCP helper layer."""

import pytest

from config.settings import Settings
from mcp.browser_manager import MCPBrowserManager
from mcp.playwright_client import PlaywrightMCPClient
from mcp.tools import PlaywrightMCPTools


def test_mcp_configuration_is_available(settings: Settings) -> None:
    """
    Purpose:
        Confirms MCP settings are part of the central Settings object.

    Why this is needed:
        MCP should use the same configuration system as the rest of the
        framework instead of hardcoded paths or browser values.
    """
    assert isinstance(settings.mcp_enabled, bool)
    assert settings.mcp_screenshot_dir.name == "mcp-screenshots"


def test_mcp_fixtures_create_expected_helper_types(
    mcp_client: PlaywrightMCPClient,
    mcp_tools: PlaywrightMCPTools,
    mcp_browser_manager: MCPBrowserManager,
) -> None:
    """
    Purpose:
        Validates that pytest can build the MCP fixtures without import errors.

    Why this is needed:
        This catches broken fixture wiring early before a developer writes
        browser-heavy MCP tests.
    """
    assert isinstance(mcp_client, PlaywrightMCPClient)
    assert isinstance(mcp_tools, PlaywrightMCPTools)
    assert isinstance(mcp_browser_manager, MCPBrowserManager)


@pytest.mark.mcp
def test_mcp_can_inspect_a_simple_page(mcp_browser_manager: MCPBrowserManager, mcp_tools: PlaywrightMCPTools) -> None:
    """
    Purpose:
        Opens a lightweight page and verifies MCP locator/debug helpers work.

    Why this is needed:
        It validates browser launch, page handling, element inspection, locator
        discovery, and debugging support without depending on app data.
    """
    page = mcp_browser_manager.open_page(authenticated=False)
    page.set_content(
        """
        <main>
            <button data-testid="save-agent">Save Agent</button>
            <input name="agentName" aria-label="Agent Name" />
        </main>
        """
    )

    details = mcp_tools.inspect_element(page, "[data-testid='save-agent']")
    suggestions = mcp_tools.discover_locators(page)
    state = mcp_tools.debug_page_state(page)

    assert details["found"] is True
    assert details["tag"] == "button"
    assert any(item["type"] == "test_id" and item["value"] == "save-agent" for item in suggestions)
    assert state["buttons"] == 1
