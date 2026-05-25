from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.locators import NAVIGATION


class NavigationPage(BasePage):
    def expect_sidebar_visible(self) -> None:
        expect(self.page.locator(NAVIGATION.sidebar).first).to_be_visible()

    def _click_nav_item(self, name: str) -> None:
        self.page.get_by_role("button", name=name).or_(self.page.get_by_role("link", name=name)).click()

    def go_to_dashboard(self) -> None:
        self._click_nav_item(NAVIGATION.dashboard_link_name)
        self.wait_for_page_ready()

    def go_to_agents(self) -> None:
        self._click_nav_item(NAVIGATION.agents_link_name)
        self.wait_for_page_ready()

    def go_to_settings(self) -> None:
        self.page.get_by_role("link", name=NAVIGATION.settings_link_name).click()
        self.wait_for_page_ready()

