from __future__ import annotations

import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.locators import LOGIN


class LoginPage(BasePage):
    def open(self) -> None:
        self.goto("/sign-in")

    def login(self, email: str, password: str, *, require_success: bool = False) -> None:
        self.open()
        self.fill(LOGIN.email_input, email)
        self.fill(LOGIN.password_input, password)
        self.page.get_by_role("button", name=LOGIN.submit_button_name).click()
        self.page.wait_for_load_state("domcontentloaded")
        try:
            expect(self.page).not_to_have_url(re.compile(".*/sign-in/?$"), timeout=10000)
        except AssertionError:
            if require_success:
                raise
        if self.page.url.rstrip("/").endswith("/sign-in"):
            return
        if self.settings.authenticated_shell_text:
            expect(self.page.get_by_text(self.settings.authenticated_shell_text, exact=False).first).to_be_visible()
        else:
            expect(self.page.locator(LOGIN.password_input)).not_to_be_visible()

    def expect_login_error(self) -> None:
        error = self.page.locator(LOGIN.error_message).or_(
            self.page.get_by_text("username or password", exact=False)
        )
        expect(error.first).to_be_visible()

    def logout(self) -> None:
        profile_name = self.settings.user_email.split("@", maxsplit=1)[0]
        profile_text = self.page.get_by_text(profile_name, exact=False).first
        expect(profile_text).to_be_visible()
        profile_text.click()
        logout = self.page.get_by_role("menuitem", name=LOGIN.logout_menu_text).or_(
            self.page.get_by_text(LOGIN.logout_menu_text, exact=True)
        )
        expect(logout.first).to_be_visible()
        logout.first.click()
        self.page.wait_for_timeout(2000)
        self.expect_visible(LOGIN.email_input)
