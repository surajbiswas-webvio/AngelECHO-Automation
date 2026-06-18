from __future__ import annotations

"""Page object for vendor team management workflows."""

from playwright.sync_api import expect

from pages.vendor_base_page import VendorBasePage


class VendorTeamPage(VendorBasePage):
    """Purpose: Encapsulates vendor team tabs, invites, direct adds, and member editing."""

    def open(self) -> None:
        """Open vendor team management and verify the page heading."""
        self.goto("/vendor/team")
        expect(self.page.get_by_text("Team Management", exact=True).first).to_be_visible()

    def open_tab(self, tab: str) -> None:
        """Open a team-management tab by name and verify tab content is visible."""
        self.page.get_by_role("button", name=tab).click()
        expect(self.page.get_by_text(tab, exact=False).first).to_be_visible()

    def open_invite(self) -> None:
        """Open invite-by-email mode and verify the email field is visible."""
        self.page.get_by_role("button", name="Invite by email").click()
        expect(self.page.get_by_placeholder("teammate@company.com")).to_be_visible()

    def open_add_directly(self) -> None:
        """Open direct member creation mode and verify the Create action is visible."""
        self.page.get_by_role("button", name="Add directly").click()
        expect(self.page.get_by_role("button", name="Create")).to_be_visible()

    def expect_invite_requires_valid_email(self) -> None:
        """Assert invalid invite email input fails browser-level validation."""
        self.open()
        self.open_invite()
        email = self.page.get_by_placeholder("teammate@company.com")
        email.fill("not-an-email")
        assert email.evaluate("element => element.checkValidity()") is False

    def expect_add_direct_form_ready(self) -> None:
        """Assert role selection and generated-password controls are available."""
        self.open()
        self.open_add_directly()
        expect(self.page.get_by_text("Select a role", exact=False).first).to_be_visible()
        expect(self.page.get_by_placeholder("auto-generated if empty")).to_be_visible()

    def open_first_member_editor(self) -> None:
        """Open the first member editor and verify save/update controls are available."""
        edit = self.page.get_by_role("button", name="Edit").first
        expect(edit).to_be_visible()
        edit.click()
        expect(self.page.get_by_role("button", name="Save").or_(self.page.get_by_role("button", name="Update")).first).to_be_visible()
