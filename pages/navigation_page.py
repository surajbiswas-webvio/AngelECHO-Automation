from __future__ import annotations

"""Page object for authenticated shell navigation."""

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.locators import NAVIGATION


class NavigationPage(BasePage):
    """Purpose: Provides reusable assertions and clicks for primary navigation."""

    def expect_sidebar_visible(self) -> None:
        """
        Purpose:
            Confirms the authenticated sidebar is visible.

        Why Needed:
            Navigation tests use the sidebar as a shell-ready signal.

        Args:
            None.

        Returns:
            None.

        Notes:
            Uses centralized navigation locator constants.
        """
        expect(self.page.locator(NAVIGATION.sidebar).first).to_be_visible()

    def _click_nav_item(self, name: str) -> None:
        """
        Purpose:
            Clicks a navigation item rendered as either a button or link.

        Why Needed:
            The app uses mixed navigation semantics across shell items.

        Args:
            name: Accessible navigation item name.

        Returns:
            None.

        Notes:
            The union locator keeps tests resilient to markup changes.
        """
        self.page.get_by_role("button", name=name).or_(self.page.get_by_role("link", name=name)).click()

    def go_to_dashboard(self) -> None:
        """Purpose: Navigates to Dashboard and waits for page readiness."""
        self._click_nav_item(NAVIGATION.dashboard_link_name)
        self.wait_for_page_ready()

    def go_to_agents(self) -> None:
        """Purpose: Navigates to All Agents and waits for page readiness."""
        self._click_nav_item(NAVIGATION.agents_link_name)
        self.wait_for_page_ready()

    def go_to_settings(self) -> None:
        """Purpose: Navigates to Settings and waits for page readiness."""
        self.page.get_by_role("link", name=NAVIGATION.settings_link_name).click()
        self.wait_for_page_ready()
