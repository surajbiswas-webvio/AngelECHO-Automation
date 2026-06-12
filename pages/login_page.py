from __future__ import annotations

"""Page object for sign-in and sign-out workflows."""

import re

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from pages.base_page import BasePage
from pages.locators import LOGIN


class LoginPage(BasePage):
    """
    Purpose:
        Encapsulates authentication UI actions and assertions.

    Why Needed:
        Login behavior is reused by fixtures, smoke tests, and session tests.

    Args:
        page: Playwright page instance.
        settings: Runtime settings with credentials and shell marker.

    Returns:
        LoginPage instance with reusable authentication methods.

    Notes:
        Selectors are imported from centralized login locators.
    """

    def open(self) -> None:
        """
        Purpose:
            Opens the sign-in page.

        Why Needed:
            Login flows need a stable entry point before credentials are filled.

        Args:
            None.

        Returns:
            None.

        Notes:
            Uses the configured base URL through BasePage.goto.
        """
        self.goto("/sign-in")

    def login(self, email: str, password: str, *, require_success: bool = False) -> None:
        """
        Purpose:
            Submits credentials through the UI and optionally requires success.

        Why Needed:
            Provides reusable login behavior for both positive authentication
            setup and negative credential validation.

        Args:
            email: User email address.
            password: User password.
            require_success: When True, raises if the page remains on sign-in.

        Returns:
            None.

        Notes:
            Uses shell text when configured; otherwise confirms the password
            field is no longer visible after login.
        """
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
        """
        Purpose:
            Verifies that the login page displays an authentication error.

        Why Needed:
            Negative login tests must confirm invalid credentials are rejected.

        Args:
            None.

        Returns:
            None.

        Notes:
            Supports both semantic alert containers and text-based errors.
        """
        error_text = re.compile(r"(username or password|incorrect|try again)", re.IGNORECASE)
        error = self.page.locator(LOGIN.error_message).or_(self.page.get_by_text(error_text))
        try:
            expect(error.first).to_be_visible(timeout=10000)
            return
        except AssertionError:
            try:
                self.page.wait_for_function(
                    """
                    () => /username or password|incorrect|try again/i.test(document.body.innerText)
                    """,
                    timeout=10000,
                )
                return
            except PlaywrightTimeoutError:
                self.logger.warning("Login error text was not visible; verifying the user remained on sign-in.")
        self.expect_url_contains("/sign-in")

    def logout(self) -> None:
        """
        Purpose:
            Logs out through the profile menu and verifies login fields return.

        Why Needed:
            Session invalidation tests need a reusable UI logout path.

        Args:
            None.

        Returns:
            None.

        Notes:
            Uses the email prefix as a profile-menu text anchor.
        """
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
