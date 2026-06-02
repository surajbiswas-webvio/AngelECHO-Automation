from __future__ import annotations

import pytest

from portals.customer.pages.dashboard_page import DashboardPage
from common.auth.login_page import LoginPage


@pytest.mark.smoke
def test_customer_can_login(unauthenticated_page, settings) -> None:
    login_page = LoginPage(unauthenticated_page, settings)
    login_page.login(settings.customer_email, settings.customer_password)
    DashboardPage(unauthenticated_page, settings).expect_loaded()


@pytest.mark.negative
def test_login_rejects_invalid_password(unauthenticated_page, settings) -> None:
    login_page = LoginPage(unauthenticated_page, settings)
    login_page.login(settings.customer_email, "WrongPassword@123")
    login_page.expect_login_error()

