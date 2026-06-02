from __future__ import annotations

from playwright.sync_api import expect

from common.base_pages.base_page import BasePage


class VendorTeamPage(BasePage):
    def open(self) -> None:
        self.goto("/vendor/team")
        expect(self.page.get_by_text("Team Management", exact=True).first).to_be_visible()

    def open_tab(self, tab: str) -> None:
        self.page.get_by_role("button", name=tab).click()
        expect(self.page.get_by_text(tab, exact=False).first).to_be_visible()

    def open_invite(self) -> None:
        self.page.get_by_role("button", name="Invite by email").click()
        expect(self.page.get_by_placeholder("teammate@company.com")).to_be_visible()

    def open_add_directly(self) -> None:
        self.page.get_by_role("button", name="Add directly").click()
        expect(self.page.get_by_role("button", name="Create")).to_be_visible()

    def expect_invite_requires_valid_email(self) -> None:
        self.open()
        self.open_invite()
        email = self.page.get_by_placeholder("teammate@company.com")
        email.fill("not-an-email")
        assert email.evaluate("element => element.checkValidity()") is False

    def expect_add_direct_form_ready(self) -> None:
        self.open()
        self.open_add_directly()
        expect(self.page.get_by_text("Select a role", exact=False).first).to_be_visible()
        expect(self.page.get_by_placeholder("auto-generated if empty")).to_be_visible()

    def open_first_member_editor(self) -> None:
        edit = self.page.get_by_role("button", name="Edit").first
        expect(edit).to_be_visible()
        edit.click()
        expect(self.page.get_by_role("button", name="Save").or_(self.page.get_by_role("button", name="Update")).first).to_be_visible()
