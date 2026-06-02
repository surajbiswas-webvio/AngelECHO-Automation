from __future__ import annotations

import pytest

from portals.customer.pages.ai_agents_page import AIAgentsPage
from portals.customer.pages.dashboard_page import DashboardPage
from portals.customer.pages.navigation_page import NavigationPage


@pytest.mark.smoke
@pytest.mark.ui
def test_dashboard_and_sidebar_are_available(page, settings) -> None:
    dashboard = DashboardPage(page, settings)
    dashboard.open()
    dashboard.expect_loaded()
    NavigationPage(page, settings).expect_sidebar_visible()


@pytest.mark.regression
def test_primary_navigation_links(page, settings) -> None:
    nav = NavigationPage(page, settings)
    DashboardPage(page, settings).open()
    nav.go_to_agents()
    AIAgentsPage(page, settings).expect_visible(page.get_by_role("heading", name="Agents Management"))
    nav.go_to_dashboard()
    nav.expect_sidebar_visible()
