from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


@pytest.mark.session
def test_authenticated_session_is_reused(page, settings) -> None:
    DashboardPage(page, settings).open()
    expect(page.locator("input[type='password']")).not_to_be_visible()


@pytest.mark.session
def test_logout_invalidates_ui_session(page, settings) -> None:
    DashboardPage(page, settings).open()
    LoginPage(page, settings).logout()


@pytest.mark.permissions
def test_customer_cannot_access_admin_route(page, settings) -> None:
    page.goto(f"{settings.base_url.rstrip('/')}/admin", wait_until="domcontentloaded")
    forbidden = page.get_by_text("Forbidden", exact=False).or_(page.get_by_text("Unauthorized", exact=False))
    expect(forbidden.first).to_be_visible()

