from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.locators import LOGIN


class LoginPage(BasePage):
    def open(self) -> None:
        self.goto("/")

    def login(self, email: str, password: str) -> None:
        self.open()
        self.fill(LOGIN.email_input, email)
        self.fill(LOGIN.password_input, password)
        self.page.get_by_role("button", name=LOGIN.submit_button_name).click()
        self.wait_for_page_ready()

    def expect_login_error(self) -> None:
        error = self.page.locator(LOGIN.error_message).first
        expect(error).to_be_visible()

    def logout(self) -> None:
        profile = self.page.locator("[data-testid='profile-menu'], button[aria-haspopup='menu']").first
        if profile.is_visible():
            profile.click()
        self.page.get_by_text(LOGIN.logout_menu_text, exact=False).click()
        self.expect_visible(LOGIN.email_input)

