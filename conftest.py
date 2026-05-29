from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from api_helpers.base_client import BaseApiClient
from config.settings import Settings, get_settings
from pages.login_page import LoginPage
from utils.config_manager import ConfigurationError
from utils.logger import get_logger
from utils.screenshot import capture_screenshot


logger = get_logger("conftest")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--env", action="store", default=None, help="Target environment from config/environments.yaml")
    parser.addoption("--headed-mode", action="store_true", default=False, help="Run browser in headed mode")


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    env = pytestconfig.getoption("--env")
    if env:
        os.environ["ENV"] = env
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
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, settings: Settings) -> Generator[Browser, None, None]:
    browser_type = getattr(playwright_instance, settings.browser)
    browser = browser_type.launch(headless=settings.headless, slow_mo=settings.slow_mo_ms)
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def worker_id(request: pytest.FixtureRequest) -> str:
    return getattr(request.config, "workerinput", {}).get("workerid", "master")


def _storage_state_is_valid(browser: Browser, settings: Settings, state_path: Path) -> bool:
    context = browser.new_context(base_url=settings.base_url, storage_state=str(state_path))
    page = context.new_page()
    page.goto(settings.url_for(), wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        logger.info("Storage-state validation continued before networkidle because the app keeps background requests open.")
    is_sign_in = page.url.rstrip("/").endswith("/sign-in")
    has_login_fields = page.locator("input[type='email'], input[name='email'], input[placeholder*='Email' i], input[name='password']").count() > 0
    has_shell_text = True
    if settings.authenticated_shell_text:
        has_shell_text = page.get_by_text(settings.authenticated_shell_text, exact=False).count() > 0
    context.close()
    return not is_sign_in and not has_login_fields and has_shell_text


@pytest.fixture(scope="session")
def auth_state(browser: Browser, settings: Settings, worker_id: str) -> Path:
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
    page = context.new_page()
    yield page
    failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    if failed:
        path = capture_screenshot(page, request.node.name)
        logger.info("Failure screenshot captured: %s", path)


@pytest.fixture()
def unauthenticated_page(browser: Browser, settings: Settings) -> Generator[Page, None, None]:
    context = browser.new_context(base_url=settings.base_url)
    context.set_default_timeout(settings.default_timeout_ms)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture()
def api_client(settings: Settings) -> BaseApiClient:
    return BaseApiClient(settings)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
