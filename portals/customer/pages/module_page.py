from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import expect

from common.base_pages.base_page import BasePage


@dataclass(frozen=True)
class ModuleDefinition:
    name: str
    path: str
    heading: str | None = None
    empty_text: str | None = None


MODULES: tuple[ModuleDefinition, ...] = (
    ModuleDefinition("Dashboard", "/", "Live Calls"),
    ModuleDefinition("All Agents", "/list", "Agents Management"),
    ModuleDefinition("Knowledge Base", "/knowledge-base"),
    ModuleDefinition("Phone Numbers", "/phone-numbers", "Phone Numbers", "No phone numbers yet"),
    ModuleDefinition("Campaign Calling", "/outbound", "Campaign Calling"),
    ModuleDefinition("Live Calls", "/live-calls", "Live Calls", "No active calls right now"),
    ModuleDefinition("Call History", "/call-history"),
    ModuleDefinition("Campaign History", "/campaign-history", "Campaign Call History"),
    ModuleDefinition("Chat History", "/chat-history"),
    ModuleDefinition("Analytics", "/analytics"),
    ModuleDefinition("Compliance", "/compliance", "Compliance"),
    ModuleDefinition("Billing", "/billing", "Billing"),
    ModuleDefinition("Pricing", "/pricing", "Cost Calculator"),
    ModuleDefinition("Members", "/members", "Members"),
    ModuleDefinition("Roles & Permissions", "/roles-permissions"),
    ModuleDefinition("Setup Guides", "/setup-guides", "Setup Guides"),
    ModuleDefinition("Support", "/support", "Support", "No tickets found"),
)


class ModulePage(BasePage):
    def open_module(self, module: ModuleDefinition) -> None:
        self.goto(module.path)
        self.expect_authenticated_shell()

    def expect_authenticated_shell(self) -> None:
        expect(self.page.get_by_text("New Customer's Workspace", exact=False).first).to_be_visible()
        expect(self.page.locator("input[type='password']")).not_to_be_visible()

    def expect_module_loaded(self, module: ModuleDefinition) -> None:
        self.open_module(module)
        if module.heading:
            expect(self.page.get_by_role("heading", name=module.heading).first).to_be_visible()
        if module.empty_text:
            expect(self.page.get_by_text(module.empty_text, exact=False).first).to_be_visible()

    def search(self, placeholder: str, value: str) -> None:
        self.page.get_by_placeholder(placeholder).fill(value)
        self.page.wait_for_timeout(300)

    def expect_table_headers(self, *headers: str) -> None:
        for header in headers:
            header_cell = self.page.get_by_role("columnheader", name=header).or_(
                self.page.get_by_text(header, exact=True)
            )
            expect(header_cell.first).to_be_visible()
