from __future__ import annotations

"""Page object for vendor profile and password validation workflows."""

from playwright.sync_api import expect

from pages.vendor_base_page import VendorBasePage


class VendorProfilePage(VendorBasePage):
    """Purpose: Encapsulates vendor profile edit and change-password checks."""

    def open(self) -> None:
        """Open vendor profile and verify the profile heading is visible."""
        self.goto("/vendor/profile")
        expect(self.page.get_by_text("Vendor Profile", exact=True)).to_be_visible()

    def open_edit(self) -> None:
        """Open profile edit mode and verify the Save action is available."""
        self.page.get_by_role("button", name="Edit Profile").first.click()
        expect(self.page.get_by_role("button", name="Save")).to_be_visible()

    def expect_profile_edit_fields(self) -> None:
        """Assert core profile edit fields are present for vendor onboarding."""
        self.open()
        self.open_edit()
        expect(self.page.locator("input").first).to_be_visible()
        expect(self.page.get_by_placeholder("Phone number")).to_be_visible()
        expect(self.page.locator("textarea").first).to_be_visible()

    def expect_password_button_requires_matching_complete_fields(self) -> None:
        """Verify the password change action stays disabled for incomplete/mismatched values."""
        self.open()
        expect(self.page.get_by_role("button", name="Change Password")).to_be_disabled()
        self.page.get_by_placeholder("Enter current password").fill("wrong-password")
        self.page.locator("#new_password").fill("Passw0rd@12345")
        self.page.get_by_placeholder("Re-enter new password").fill("different-password")
        expect(self.page.get_by_role("button", name="Change Password")).to_be_disabled()

    def expect_password_button_enabled_for_matching_fields(self, current_password: str) -> None:
        """Fill matching password fields and assert the change action becomes enabled."""
        self.open()
        self.page.get_by_placeholder("Enter current password").fill(current_password)
        self.page.locator("#new_password").fill(current_password)
        self.page.get_by_placeholder("Re-enter new password").fill(current_password)
        expect(self.page.get_by_role("button", name="Change Password")).to_be_enabled()
