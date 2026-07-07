from __future__ import annotations

"""Generic customer module page object and module registry."""

from dataclasses import dataclass

from playwright.sync_api import expect

from pages.base_page import BasePage


@dataclass(frozen=True)
class ModuleDefinition:
    """
    Purpose:
        Describes a customer portal module that should be accessible.

    Why Needed:
        Parametrized smoke tests can validate many modules from one registry.
    """
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
    """Purpose: Provides reusable checks for customer portal modules."""

    def open_module(self, module: ModuleDefinition) -> None:
        """
        Purpose:
            Opens a configured customer module and verifies auth shell.

        Why Needed:
            Module smoke tests need consistent navigation and session checks.

        Args:
            module: ModuleDefinition containing route and expected content.

        Returns:
            None.

        Notes:
            Authentication shell validation runs before module-specific checks.
        """
        self.goto(module.path)
        self.expect_authenticated_shell()

    def expect_authenticated_shell(self) -> None:
        """
        Purpose:
            Confirms the customer authenticated shell is present.

        Why Needed:
            Protected-module checks must fail if the app redirects to login.

        Args:
            None.

        Returns:
            None.

        Notes:
            Also asserts password input absence as a redirect guard.
        """
        expect(self.page.get_by_text("New Customer's Workspace", exact=False).first).to_be_visible()
        expect(self.page.locator("input[type='password']")).not_to_be_visible()

    def expect_module_loaded(self, module: ModuleDefinition) -> None:
        """
        Purpose:
            Verifies a customer module opens and renders expected content.

        Why Needed:
            Smoke coverage must confirm accessible routes are not blank or
            redirected.

        Args:
            module: ModuleDefinition with optional heading and empty-state text.

        Returns:
            None.

        Notes:
            Optional assertions allow one registry to cover varied modules.
        """
        self.open_module(module)
        if module.heading:
            expect(self.page.get_by_role("heading", name=module.heading).first).to_be_visible()
        if module.empty_text:
            expect(self.page.get_by_text(module.empty_text, exact=False).first).to_be_visible()

    def search(self, placeholder: str, value: str) -> None:
        """
        Purpose:
            Enters text into a module search field.

        Why Needed:
            Multiple modules expose search inputs with different placeholders.

        Args:
            placeholder: Placeholder text identifying the search field.
            value: Search value to enter.

        Returns:
            None.

        Notes:
            Includes a short debounce wait for client-side filtering.
        """
        self.page.get_by_placeholder(placeholder).fill(value)
        self.page.wait_for_timeout(300)

    def expect_table_headers(self, *headers: str) -> None:
        """
        Purpose:
            Verifies expected table headers are visible.

        Why Needed:
            Confirms core data tables render their essential columns.

        Args:
            *headers: Header names expected in the current module table.

        Returns:
            None.

        Notes:
            Falls back to exact text for tables that do not expose columnheader
            roles.
        """
        for header in headers:
            header_cell = self.page.get_by_role("columnheader", name=header).or_(
                self.page.get_by_text(header, exact=True)
            )
            expect(header_cell.first).to_be_visible()
