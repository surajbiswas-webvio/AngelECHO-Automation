from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class VendorProfilePage(BasePage):
    def open(self) -> None:
        self.goto("/vendor/profile")
        expect(self.page.get_by_text("Vendor Profile", exact=True)).to_be_visible()

    def open_edit(self) -> None:
        self.page.get_by_role("button", name="Edit Profile").first.click()
        expect(self.page.get_by_role("button", name="Save")).to_be_visible()

    def expect_profile_edit_fields(self) -> None:
        self.open()
        self.open_edit()
        expect(self.page.locator("input").first).to_be_visible()
        expect(self.page.get_by_placeholder("Phone number")).to_be_visible()
        expect(self.page.locator("textarea").first).to_be_visible()

    def expect_password_button_requires_matching_complete_fields(self) -> None:
        self.open()
        expect(self.page.get_by_role("button", name="Change Password")).to_be_disabled()
        self.page.get_by_placeholder("Enter current password").fill("wrong-password")
        self.page.locator("#new_password").fill("Passw0rd@12345")
        self.page.get_by_placeholder("Re-enter new password").fill("different-password")
        expect(self.page.get_by_role("button", name="Change Password")).to_be_disabled()

    def expect_password_button_enabled_for_matching_fields(self, current_password: str) -> None:
        self.open()
        self.page.get_by_placeholder("Enter current password").fill(current_password)
        self.page.locator("#new_password").fill(current_password)
        self.page.get_by_placeholder("Re-enter new password").fill(current_password)
        expect(self.page.get_by_role("button", name="Change Password")).to_be_enabled()
