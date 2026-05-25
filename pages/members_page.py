from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class MembersPage(BasePage):
    def open(self) -> None:
        self.goto("/members")
        expect(self.page.get_by_role("heading", name="Members")).to_be_visible()

    def open_invite_dialog(self) -> None:
        self.page.get_by_role("button", name="Invite Members").click()
        expect(self.page.get_by_role("dialog", name="Invite New Member")).to_be_visible()

    def expect_invite_requires_valid_email(self) -> None:
        expect(self.page.get_by_role("button", name="Send Invitation")).to_be_disabled()
        email = self.page.get_by_placeholder("user@example.com")
        email.fill("not-an-email")
        is_valid = email.evaluate("element => element.checkValidity()")
        assert is_valid is False

    def search_members(self, value: str) -> None:
        self.page.get_by_placeholder("Search Members...").fill(value)
        self.page.wait_for_timeout(300)

    def expect_owner_visible(self, email: str) -> None:
        expect(self.page.get_by_role("row").filter(has_text=email).first).to_be_visible()
