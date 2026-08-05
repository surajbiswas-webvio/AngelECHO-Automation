from __future__ import annotations

"""Page object for customer member management workflows."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class MembersPage(BasePage):
    """Purpose: Encapsulates member list, invite, search, and owner checks."""

    def open(self) -> None:
        """Open Members and verify the page heading; returns None."""
        self.goto("/members")
        expect(self.page.get_by_role("heading", name="Members")).to_be_visible()

    def open_invite_dialog(self) -> None:
        """Open the invite dialog so tests can validate invitation rules."""
        invite_button = self.page.get_by_role("button", name="Invite Members").or_(
            self.page.get_by_role("button", name="Invite Member")
        )
        invite_button.first.click()
        expect(self.page.get_by_role("dialog").first).to_be_visible()

    def expect_invite_requires_valid_email(self) -> None:
        """Assert invalid invite email input is rejected by browser validation."""
        invite = self.page.get_by_role("button", name="Send Invitation").or_(
            self.page.get_by_role("button", name="Invite", exact=True)
        )
        expect(invite.first).to_be_disabled()
        email = self.page.get_by_placeholder("user@example.com").or_(
            self.page.get_by_placeholder("sarah@example.com")
        )
        email.fill("not-an-email")
        is_valid = email.evaluate("element => element.checkValidity()")
        assert is_valid is False

    def search_members(self, value: str) -> None:
        """Search members by value and wait for client-side filtering; returns None."""
        search = self.page.get_by_placeholder("Search Members...")
        if search.count() > 0:
            search.fill(value)
            self.page.wait_for_timeout(300)

    def expect_owner_visible(self, email: str) -> None:
        """Assert a member row for the owner email is visible; returns None."""
        expect(self.page.get_by_role("row").filter(has_text=email).first).to_be_visible()
