from __future__ import annotations

"""Pytest framework wiring for browser, session, and API test execution.

This module centralizes command-line options, environment resolution,
Playwright lifecycle management, authenticated storage-state reuse, and
failure artifacts. Keeping these fixtures in one place gives UI, API, smoke,
regression, and vendor workflows the same runtime behavior.
"""

import os
import re
from pathlib import Path
from typing import Generator
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from api_helpers.base_client import BaseApiClient
from config.settings import Settings, get_settings
from mcp.browser_manager import MCPBrowserManager
from mcp.playwright_client import PlaywrightMCPClient
from mcp.tools import PlaywrightMCPTools
from pages.login_page import LoginPage
from utils.config_manager import ConfigurationError
from utils.logger import get_logger
from utils.screenshot import capture_screenshot


logger = get_logger("conftest")


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Purpose:
        Registers automation-specific pytest command-line options.

    Why Needed:
        Allows engineers and CI jobs to choose the target environment and
        headed/headless browser mode without changing test code.

    Args:
        parser: Pytest parser used to add custom CLI flags.

    Returns:
        None. Options are registered on the supplied parser.

    Notes:
        Values are later consumed by the `settings` fixture.
    """
    parser.addoption("--env", action="store", default=None, help="Target environment from config/environments.yaml")
    parser.addoption("--headed-mode", action="store_true", default=False, help="Run browser in headed mode")


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    """
    Purpose:
        Builds the immutable runtime settings object for the test session.

    Why Needed:
        Provides a single validated source of truth for URLs, credentials,
        browser options, timeouts, and artifact behavior across all tests.

    Args:
        pytestconfig: Active pytest configuration containing CLI options.

    Returns:
        A validated Settings instance for the selected environment.

    Notes:
        Exits pytest with a configuration error when required environment
        values are missing or malformed.
    """
    env = pytestconfig.getoption("--env")
    if env:
        # ensure value assigned to environment is a string for type checkers
        os.environ["ENV"] = str(env)
    try:
        resolved = get_settings()
    except ConfigurationError as exc:
        logger.error("Invalid automation configuration: %s", exc)
        pytest.exit(f"Invalid automation configuration: {exc}", returncode=2)
    if pytestconfig.getoption("--headed-mode"):
        os.environ["HEADLESS"] = "false"
        try:
            resolved = get_settings()
        except ConfigurationError as exc:
            logger.error("Invalid automation configuration: %s", exc)
            pytest.exit(f"Invalid automation configuration: {exc}", returncode=2)
    logger.info("Running automation against %s environment: %s", resolved.env, resolved.base_url)
    return resolved


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """
    Purpose:
        Starts and yields the Playwright driver for the test session.

    Why Needed:
        Avoids repeated Playwright startup cost while ensuring the driver is
        closed after the session completes.

    Args:
        None.

    Returns:
        Generator yielding a Playwright instance.

    Notes:
        The context manager owns Playwright cleanup.
    """
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, settings: Settings) -> Generator[Browser, None, None]:
    """
    Purpose:
        Launches the configured browser once per pytest session.

    Why Needed:
        Shares browser startup cost across tests while keeping per-test
        isolation at the browser-context level.

    Args:
        playwright_instance: Session-scoped Playwright driver.
        settings: Runtime browser configuration.

    Returns:
        Generator yielding a Playwright Browser.

    Notes:
        Browser type, headless mode, and slow motion are environment driven.
    """
    browser_type = getattr(playwright_instance, settings.browser)
    browser = browser_type.launch(headless=settings.headless, slow_mo=settings.slow_mo_ms)
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def worker_id(request: pytest.FixtureRequest) -> str:
    """
    Purpose:
        Resolves the pytest-xdist worker identifier for storage-state names.

    Why Needed:
        Prevents parallel workers from writing to the same authentication file.

    Args:
        request: Fixture request containing pytest worker metadata.

    Returns:
        Worker id such as `gw0`, or `master` for non-xdist runs.

    Notes:
        The value is safe to use in generated artifact filenames.
    """
    return getattr(request.config, "workerinput", {}).get("workerid", "master")


def _storage_state_is_valid(browser: Browser, settings: Settings, state_path: Path) -> bool:
    """
    Purpose:
        Verifies that a saved Playwright storage state still represents a
        logged-in application session.

    Why Needed:
        Reusing valid auth state avoids repetitive UI login, but stale state
        must be detected before tests depend on it.

    Args:
        browser: Browser used to create a temporary validation context.
        settings: Environment settings containing base URL and shell marker.
        state_path: Existing storage-state JSON file to validate.

    Returns:
        True when the state opens an authenticated shell; otherwise False.

    Notes:
        Network-idle is best-effort because some apps keep background polling
        requests open after page load.
    """
    context = browser.new_context(base_url=settings.base_url, storage_state=str(state_path))
    page = context.new_page()
    page.goto(settings.url_for(), wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        logger.info("Storage-state validation continued before networkidle because the app keeps background requests open.")
    parsed_url = urlparse(page.url)
    is_sign_in = parsed_url.path.rstrip("/") == "/sign-in"
    has_login_fields = page.locator("input[type='email'], input[name='email'], input[placeholder*='Email' i], input[name='password']").count() > 0
    has_shell_text = False
    if settings.authenticated_shell_text:
        has_shell_text = page.get_by_text(settings.authenticated_shell_text, exact=False).count() > 0
    context.close()
    return not is_sign_in and not has_login_fields and has_shell_text


@pytest.fixture(scope="session")
def auth_state(browser: Browser, settings: Settings, worker_id: str) -> Path:
    """
    Purpose:
        Provides a reusable authenticated Playwright storage-state file.

    Why Needed:
        Authenticated UI tests need a logged-in session, and persisting storage
        state reduces test runtime and login flakiness.

    Args:
        browser: Session browser used for validation and login.
        settings: Runtime credentials and environment configuration.
        worker_id: Unique pytest worker id for parallel-safe state files.

    Returns:
        Path to a valid storage-state JSON file.

    Notes:
        Creates a fresh state via LoginPage when no valid cached state exists.
    """
    state_dir = settings.root_dir / "storage_states"
    state_dir.mkdir(exist_ok=True)
    safe_user = re.sub(r"[^a-zA-Z0-9]+", "-", settings.user_email).strip("-").lower() or "user"
    state_path = state_dir / f"{settings.env}-{worker_id}-{safe_user}.json"
    if state_path.exists() and _storage_state_is_valid(browser, settings, state_path):
        return state_path

    context = browser.new_context(base_url=settings.base_url)
    page = context.new_page()
    LoginPage(page, settings).login(settings.user_email, settings.user_password, require_success=True)
    context.storage_state(path=str(state_path))
    context.close()
    return state_path


@pytest.fixture()
def context(browser: Browser, settings: Settings, auth_state: Path, request: pytest.FixtureRequest) -> Generator[BrowserContext, None, None]:
    """
    Purpose:
        Creates an isolated authenticated browser context for each test.

    Why Needed:
        Keeps cookies, local storage, tracing, and optional video artifacts
        scoped to the current test while reusing the session browser.

    Args:
        browser: Session-scoped Playwright browser.
        settings: Runtime artifact and timeout configuration.
        auth_state: Path to reusable authenticated storage state.
        request: Pytest request used to inspect test outcome.

    Returns:
        Generator yielding an authenticated BrowserContext.

    Notes:
        Failure traces are saved only when `TRACE_ON_FAILURE` is enabled and
        the call phase fails.
    """
    video_dir = settings.root_dir / "reports" / "videos"
    context = browser.new_context(
        base_url=settings.base_url,
        storage_state=str(auth_state),
        record_video_dir=str(video_dir) if settings.video_on_failure else None,
    )
    context.set_default_timeout(settings.default_timeout_ms)
    if settings.trace_on_failure:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context

    failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    if settings.trace_on_failure:
        trace_dir = settings.root_dir / "reports" / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        if failed:
            context.tracing.stop(path=str(trace_dir / f"{request.node.name}.zip"))
        else:
            context.tracing.stop()
    context.close()


@pytest.fixture()
def page(context: BrowserContext, settings: Settings, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
    """
    Purpose:
        Opens a fresh authenticated page for each UI test.

    Why Needed:
        Page-level isolation keeps workflows independent while sharing the
        already-authenticated browser context.

    Args:
        context: Per-test authenticated browser context.
        settings: Runtime settings, kept available for fixture symmetry.
        request: Pytest request used to capture screenshots on failure.

    Returns:
        Generator yielding a Playwright Page.

    Notes:
        Screenshots are captured after failed test calls for debugging.
    """
    page = context.new_page()
    yield page
    failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    if failed:
        path = capture_screenshot(page, request.node.name)
        logger.info("Failure screenshot captured: %s", path)


@pytest.fixture()
def unauthenticated_page(browser: Browser, settings: Settings) -> Generator[Page, None, None]:
    """
    Purpose:
        Opens a fresh browser page without stored authentication.

    Why Needed:
        Login, logout, and protected-route tests must validate unauthenticated
        behavior independently from the shared auth-state fixture.

    Args:
        browser: Session-scoped Playwright browser.
        settings: Runtime base URL and timeout configuration.

    Returns:
        Generator yielding an unauthenticated Playwright Page.

    Notes:
        The temporary browser context is closed after the test.
    """
    context = browser.new_context(base_url=settings.base_url)
    context.set_default_timeout(settings.default_timeout_ms)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture()
def api_client(settings: Settings) -> BaseApiClient:
    """
    Purpose:
        Creates a base API client configured for the active environment.

    Why Needed:
        API tests and helper clients require consistent base URL, headers, and
        timeout behavior.

    Args:
        settings: Runtime API configuration.

    Returns:
        BaseApiClient instance without an authentication token.

    Notes:
        Tests can set a token later or instantiate specialized API clients.
    """
    return BaseApiClient(settings)


@pytest.fixture(scope="session")
def mcp_client(settings: Settings) -> Generator[PlaywrightMCPClient, None, None]:
    """
    Purpose:
        Provides the optional Playwright MCP server client for the test session.

    Why Needed:
        MCP-enabled tests may call tools exposed by an external Playwright MCP
        server. When no server command is configured, this fixture still yields
        a client in local mode so the rest of the MCP helpers can be used.

    Args:
        settings: Runtime MCP configuration from `.env` and YAML defaults.

    Returns:
        Generator yielding PlaywrightMCPClient.

    Notes:
        The client closes any server process it starts during teardown.
    """
    client = PlaywrightMCPClient(settings)
    client.connect()
    yield client
    client.close()


@pytest.fixture()
def mcp_browser_manager(
    browser: Browser,
    settings: Settings,
) -> Generator[MCPBrowserManager, None, None]:
    """
    Purpose:
        Creates a per-test manager for MCP browser contexts and pages.

    Why Needed:
        MCP tools need pages for inspection and screenshots, but simple MCP
        validation should not force an application login.

    Args:
        browser: Session-scoped Playwright Browser.
        settings: Runtime framework configuration.
    Returns:
        Generator yielding MCPBrowserManager without saved authentication.

    Notes:
        Contexts opened through the manager are closed after each test.
    """
    manager = MCPBrowserManager(browser, settings)
    yield manager
    manager.close_all()


@pytest.fixture()
def mcp_authenticated_browser_manager(
    browser: Browser,
    settings: Settings,
    auth_state: Path,
) -> Generator[MCPBrowserManager, None, None]:
    """
    Purpose:
        Creates a per-test MCP manager that reuses authenticated storage state.

    Why Needed:
        Authenticated MCP workflows should use the same login/session handling
        as normal UI tests instead of logging in manually.

    Args:
        browser: Session-scoped Playwright Browser.
        settings: Runtime framework configuration.
        auth_state: Existing authenticated storage-state JSON path.

    Returns:
        Generator yielding MCPBrowserManager with saved authentication.

    Notes:
        Request this fixture when the MCP page must open logged in.
    """
    manager = MCPBrowserManager(browser, settings, auth_state)
    yield manager
    manager.close_all()


@pytest.fixture()
def mcp_tools(settings: Settings, mcp_client: PlaywrightMCPClient) -> PlaywrightMCPTools:
    """
    Purpose:
        Provides beginner-friendly MCP actions to tests and debugging scripts.

    Why Needed:
        Test authors can request one fixture for navigation, locator discovery,
        screenshots, page-state debugging, and optional external MCP calls.

    Args:
        settings: Runtime framework configuration.
        mcp_client: Optional external MCP JSON-RPC client.

    Returns:
        PlaywrightMCPTools instance.
    """
    return PlaywrightMCPTools(settings, mcp_client)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    """
    Purpose:
        Stores each pytest phase report on the test item.

    Why Needed:
        Fixtures running teardown code need to know whether the test call
        failed so they can conditionally save screenshots, traces, and videos.

    Args:
        item: Current pytest test item.
        call: Pytest call information for setup, call, or teardown phase.

    Returns:
        Hook generator result controlled by pytest.

    Notes:
        The `rep_call` attribute is consumed by page/context teardown logic.
    """
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
