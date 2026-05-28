from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage


@pytest.mark.session
def test_authenticated_session_is_reused(page, settings) -> None:
    DashboardPage(page, settings).open()
    expect(page.locator("input[type='password']")).not_to_be_visible()


@pytest.mark.session
def test_logout_invalidates_ui_session(page, settings) -> None:
    DashboardPage(page, settings).open()
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    page.context.clear_cookies()
    page.goto(settings.url_for(), wait_until="domcontentloaded")
    expect(page.locator("input[type='email'], input[name='email'], input[placeholder*='Email' i]").first).to_be_visible()


@pytest.mark.permissions
def test_customer_cannot_access_admin_route(page, settings) -> None:
    page.goto(settings.url_for("admin"), wait_until="domcontentloaded")
    unavailable = page.get_by_text("Forbidden", exact=False).or_(
        page.get_by_text("Unauthorized", exact=False)
    ).or_(page.get_by_text("Page Not Found", exact=True))
    expect(unavailable.first).to_be_visible()
