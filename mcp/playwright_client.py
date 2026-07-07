from __future__ import annotations

"""Optional JSON-RPC client for a Playwright MCP server.

Purpose:
    This file knows how to connect to an external Playwright MCP process when
    a team chooses to run one.

Why this exists:
    The framework can already drive Playwright directly. MCP support adds a
    second path for tool-style actions, such as asking a local MCP server to
    inspect a page or run a browser command. Keeping this code isolated means
    normal tests continue to work even when no MCP server is configured.

How to use:
    Set MCP_ENABLED=true and provide MCP_SERVER_COMMAND, for example a command
    that starts your Playwright MCP server. Tests can then call the
    `mcp_client` fixture or use `mcp_tools.call_mcp_server_tool(...)`.
"""

import json
import subprocess
from dataclasses import dataclass
from typing import Any

from config.settings import Settings
from utils.logger import get_logger


@dataclass(frozen=True)
class MCPResponse:
    """
    Purpose:
        Represents one JSON-RPC response from an MCP server.

    Args:
        result: Successful response payload, if the call succeeded.
        error: Error response payload, if the call failed.

    Returns:
        Dataclass value used by PlaywrightMCPClient.call_tool.
    """

    result: Any | None = None
    error: Any | None = None


class PlaywrightMCPClient:
    """
    Purpose:
        Starts and talks to an optional Playwright MCP server process.

    Why this is needed:
        Some teams expose browser automation as MCP tools. This client keeps
        that server communication separate from direct Playwright page logic.

    Args:
        settings: Runtime Settings object with MCP command configuration.

    Returns:
        A client object. Call `connect()` before sending server tool requests.

    Notes:
        When no MCP server command is configured, the client stays in local
        mode. Local mode is useful because `mcp_tools` can still provide
        Playwright-backed helper actions.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self._process: subprocess.Popen[str] | None = None
        self._next_request_id = 1

    @property
    def is_enabled(self) -> bool:
        """
        Purpose:
            Tells callers whether MCP behavior is enabled in configuration.

        Returns:
            True when MCP_ENABLED is truthy; otherwise False.
        """
        return self.settings.mcp_enabled

    @property
    def is_connected(self) -> bool:
        """
        Purpose:
            Tells callers whether an external MCP server process is active.

        Returns:
            True when a process was started and is still running.
        """
        return self._process is not None and self._process.poll() is None

    def connect(self) -> None:
        """
        Purpose:
            Starts the configured MCP server process.

        Why this is needed:
            MCP tool calls require a server to read JSON-RPC messages from
            stdin and write JSON-RPC responses to stdout.

        Args:
            None. Command and arguments come from Settings.

        Returns:
            None.

        Raises:
            RuntimeError when MCP is enabled but the server cannot be started.
        """
        if not self.settings.mcp_enabled:
            self.logger.info("MCP is disabled; using direct Playwright helpers only.")
            return
        if not self.settings.mcp_server_command:
            self.logger.info("MCP is enabled without MCP_SERVER_COMMAND; using local Playwright MCP helpers.")
            return
        if self.is_connected:
            return

        command = [self.settings.mcp_server_command, *self.settings.mcp_server_args]
        try:
            self._process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
        except OSError as exc:
            raise RuntimeError(f"Unable to start Playwright MCP server: {command}") from exc
        self.logger.info("Started Playwright MCP server: %s", " ".join(command))

    def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> MCPResponse:
        """
        Purpose:
            Sends one MCP `tools/call` JSON-RPC request to the server.

        Why this is needed:
            It gives tests one beginner-friendly method for invoking external
            MCP browser tools without learning JSON-RPC details.

        Args:
            tool_name: Name of the MCP tool exposed by the server.
            arguments: Tool input values. Use an empty dict when not needed.

        Returns:
            MCPResponse with either `result` or `error` populated.

        Raises:
            RuntimeError when no external MCP server is connected.
        """
        if not self.is_connected or self._process is None or self._process.stdin is None or self._process.stdout is None:
            raise RuntimeError("Playwright MCP server is not connected. Configure MCP_SERVER_COMMAND or use local tools.")

        request_id = self._next_request_id
        self._next_request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments or {}},
        }
        self._process.stdin.write(json.dumps(payload) + "\n")
        self._process.stdin.flush()

        response_line = self._process.stdout.readline()
        if not response_line:
            raise RuntimeError("Playwright MCP server closed before returning a response.")
        response = json.loads(response_line)
        return MCPResponse(result=response.get("result"), error=response.get("error"))

    def close(self) -> None:
        """
        Purpose:
            Stops the external MCP server process when this client started it.

        Why this is needed:
            Test sessions should not leave background server processes running.

        Args:
            None.

        Returns:
            None.
        """
        if self._process is None:
            return
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None
