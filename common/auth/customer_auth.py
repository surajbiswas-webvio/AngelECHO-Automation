from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Browser

from common.auth.login_page import LoginPage
from config.settings import Settings


def customer_auth(browser: Browser, settings: Settings, state_path: Path) -> None:
    context = browser.new_context(base_url=settings.customer_base_url)
    page = context.new_page()
    LoginPage(page, settings).login(settings.customer_email, settings.customer_password, require_success=True)
    context.storage_state(path=str(state_path))
    context.close()
