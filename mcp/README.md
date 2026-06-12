# Playwright MCP Integration

## What This Folder Does

The `mcp/` package adds MCP-style helper tools on top of the existing Playwright pytest framework. It does not replace the current browser, page, login, storage-state, or page-object flow.

## Files

- `playwright_client.py`: optional JSON-RPC stdio client for an external Playwright MCP server.
- `browser_manager.py`: opens MCP pages and contexts using the existing pytest browser and authenticated storage state.
- `tools.py`: beginner-friendly actions for navigation, element inspection, locator discovery, screenshots, debugging, and external MCP tool calls.

## Configuration

Add these values to `.env` when needed:

```text
MCP_ENABLED=true
MCP_SERVER_COMMAND=
MCP_SERVER_ARGS=
MCP_SCREENSHOT_DIR=reports/mcp-screenshots
```

`MCP_SERVER_COMMAND` is optional. When it is empty, the framework still provides local Playwright MCP helper tools through the `mcp_tools` fixture.

## Pytest Usage

```python
def test_inspect_page(mcp_browser_manager, mcp_tools):
    page = mcp_authenticated_browser_manager.open_page("/dashboard")
    state = mcp_tools.debug_page_state(page)
    assert "url" in state
```

Use `mcp_browser_manager` for unauthenticated or simple debug pages. Use
`mcp_authenticated_browser_manager` when the page must reuse the framework's
saved login storage state.

## Adding A New MCP Action

1. Add a method to `PlaywrightMCPTools`.
2. Keep the method small and name it after one action.
3. Document the purpose, inputs, return value, and why the action exists.
4. Reuse `Settings` for paths, URLs, timeouts, and configuration.
