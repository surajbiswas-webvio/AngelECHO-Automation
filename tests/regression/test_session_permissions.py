from __future__ import annotations

import re

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
def test_unauthenticated_customer_route_redirects_to_login(unauthenticated_page, settings) -> None:
    unauthenticated_page.goto(settings.url_for("list"), wait_until="domcontentloaded")
    expect(unauthenticated_page).to_have_url(re.compile(".*/sign-in.*"))
