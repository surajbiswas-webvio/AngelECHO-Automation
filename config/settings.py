from __future__ import annotations

"""Runtime settings model for AngelECHO automation.

The module resolves environment files, YAML defaults, and operating-system
environment variables into a frozen Settings object used by fixtures, page
objects, and API clients.
"""

from dataclasses import dataclass
from pathlib import Path

import os

from utils.config_manager import ConfigManager

ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_MANAGER = ConfigManager(ROOT_DIR)


def _as_bool(value: str | bool | None, default: bool = False) -> bool:
    """
    Purpose:
        Converts environment-style boolean values into Python booleans.

    Why Needed:
        CLI and `.env` values arrive as strings while Playwright expects real
        boolean options.

    Args:
        value: Raw string, boolean, or None value to convert.
        default: Fallback returned when value is None.

    Returns:
        Boolean interpretation of the supplied value.

    Notes:
        Accepts common truthy strings such as `true`, `yes`, `1`, and `on`.
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _as_int(value: str | int | None, default: int) -> int:
    """
    Purpose:
        Converts optional environment values into integers.

    Why Needed:
        Timeouts and slow-motion values are configured externally but consumed
        by Playwright as integer milliseconds.

    Args:
        value: Raw string, integer, or None value to convert.
        default: Fallback returned when value is None.

    Returns:
        Integer configuration value.

    Notes:
        Invalid numeric strings intentionally raise ValueError during settings
        creation so bad configuration fails fast.
    """
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    """
    Purpose:
        Immutable runtime configuration shared across automation layers.

    Why Needed:
        Keeps browser, URL, credential, timeout, and artifact options stable
        for the duration of a test run.

    Args:
        Dataclass fields are populated by `get_settings`.

    Returns:
        Settings instances are value objects and do not return data directly.

    Notes:
        `root_dir` anchors generated artifacts and relative data lookups.
    """
    env: str
    base_url: str
    api_base_url: str
    browser: str
    headless: bool
    default_timeout_ms: int
    slow_mo_ms: int
    trace_on_failure: bool
    video_on_failure: bool
    customer_email: str
    customer_password: str
    user_email: str
    user_password: str
    authenticated_shell_text: str
    mcp_enabled: bool
    mcp_server_command: str | None
    mcp_server_args: tuple[str, ...]
    mcp_screenshot_dir: Path
    root_dir: Path = ROOT_DIR

    def url_for(self, path: str = "") -> str:
        """
        Purpose:
            Builds an application URL for the active environment.

        Why Needed:
            Page objects should not duplicate base URL joining rules.

        Args:
            path: Optional route or path fragment.

        Returns:
            Absolute UI URL.

        Notes:
            Leading and trailing slashes are normalized by ConfigManager.
        """
        return ConfigManager.join_url(self.base_url, path)

    def api_url_for(self, path: str = "") -> str:
        """
        Purpose:
            Builds an API endpoint URL for the active environment.

        Why Needed:
            API helpers need consistent endpoint construction regardless of
            whether paths include leading slashes.

        Args:
            path: Optional API path fragment.

        Returns:
            Absolute API URL.

        Notes:
            Uses the derived API base URL when API_BASE_URL is not configured.
        """
        return ConfigManager.join_url(self.api_base_url, path)


def get_settings() -> Settings:
    """
    Purpose:
        Resolves all automation runtime configuration into Settings.

    Why Needed:
        Fixtures, page objects, and API clients require the same validated
        configuration source to avoid environment drift.

    Args:
        None. Values are loaded from `.env`, `.env.<ENV>`, YAML defaults, and
        process environment variables.

    Returns:
        Fully populated Settings dataclass.

    """
    env = CONFIG_MANAGER.load_dotenv_files()
    defaults = CONFIG_MANAGER.load_environment_defaults(env)
    base_url = CONFIG_MANAGER.normalize_base_url(
        CONFIG_MANAGER.get_value("BASE_URL", defaults, required=True) or "",
        name="BASE_URL",
    )
    api_base_url = CONFIG_MANAGER.get_value("API_BASE_URL", defaults)
    if api_base_url:
        api_base_url = CONFIG_MANAGER.normalize_base_url(api_base_url, name="API_BASE_URL")
    else:
        api_base_url = ConfigManager.join_url(base_url, "api/")

    user_email = os.getenv("CUSTOMER_EMAIL", "new_customer@yopmail.com")
    user_password = os.getenv("CUSTOMER_PASSWORD", "Test@123")

    return Settings(
        env=env,
        base_url=base_url,
        api_base_url=api_base_url,
        browser=os.getenv("BROWSER", defaults.get("browser", "chromium")),
        headless=_as_bool(os.getenv("HEADLESS"), defaults.get("headless", True)),
        default_timeout_ms=_as_int(os.getenv("DEFAULT_TIMEOUT_MS"), defaults.get("default_timeout_ms", 15000)),
        slow_mo_ms=_as_int(os.getenv("SLOW_MO_MS"), defaults.get("slow_mo_ms", 0)),
        trace_on_failure=_as_bool(os.getenv("TRACE_ON_FAILURE"), True),
        video_on_failure=_as_bool(os.getenv("VIDEO_ON_FAILURE"), False),
        customer_email=user_email,
        customer_password=user_password,
        user_email=user_email,
        user_password=user_password,
        authenticated_shell_text=CONFIG_MANAGER.get_value("AUTHENTICATED_SHELL_TEXT", defaults) or "",
        mcp_enabled=_as_bool(os.getenv("MCP_ENABLED"), _as_bool(defaults.get("mcp_enabled"), False)),
        mcp_server_command=CONFIG_MANAGER.get_value("MCP_SERVER_COMMAND", defaults),
        mcp_server_args=tuple(
            arg.strip()
            for arg in (CONFIG_MANAGER.get_value("MCP_SERVER_ARGS", defaults) or "").split()
            if arg.strip()
        ),
        mcp_screenshot_dir=ROOT_DIR / (CONFIG_MANAGER.get_value("MCP_SCREENSHOT_DIR", defaults) or "reports/mcp-screenshots"),
    )
