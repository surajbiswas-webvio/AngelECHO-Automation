from __future__ import annotations

"""Playwright MCP integration helpers for AngelECHO automation.

This package adds optional MCP-style browser utilities without replacing the
existing pytest fixtures, page objects, or authentication storage-state flow.
"""

from mcp.browser_manager import MCPBrowserManager
from mcp.playwright_client import PlaywrightMCPClient
from mcp.tools import PlaywrightMCPTools

__all__ = ["MCPBrowserManager", "PlaywrightMCPClient", "PlaywrightMCPTools"]
