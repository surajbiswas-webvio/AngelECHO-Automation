from __future__ import annotations

"""Generic vendor module page object and module registry."""

from dataclasses import dataclass

from playwright.sync_api import expect

from pages.vendor_base_page import VendorBasePage


@dataclass(frozen=True)
class VendorModuleDefinition:
    """Purpose: Describes a vendor portal module used by parametrized smoke tests."""
    name: str
    path: str
    heading: str
    expected_text: str | None = None


VENDOR_MODULES: tuple[VendorModuleDefinition, ...] = (
    VendorModuleDefinition("Dashboard", "/vendor/dashboard", "Dashboard", "Welcome back"),
    VendorModuleDefinition("My Leads", "/vendor/leads", "My Leads", "Add Lead"),
    VendorModuleDefinition("Demo Agents", "/vendor/demo-agents", "Demo Agents", "My Demo Agents"),
    VendorModuleDefinition("Earnings", "/vendor/earnings", "Earnings", "Commissions you've earned"),
    VendorModuleDefinition("Coupons & Rates", "/vendor/billing", "Coupons & Rates", "Commission rates"),
    VendorModuleDefinition("Plans & Pricing", "/vendor/plans", "Plans & Pricing", "Available Plans"),
    VendorModuleDefinition("Team Management", "/vendor/team", "Team Management", "Invite teammates"),
    VendorModuleDefinition("Performance", "/vendor/performance", "Performance", "Team Performance"),
    VendorModuleDefinition("Help & Support", "/vendor/support", "Help & Support", "New Ticket"),
    VendorModuleDefinition("Profile", "/vendor/profile", "Profile", "Vendor Profile"),
)


class VendorModulePage(VendorBasePage):
    """Purpose: Provides reusable checks for vendor portal modules."""

    def expect_authenticated_shell(self) -> None:
        """Assert the vendor authenticated shell is visible and login fields are absent."""
        expect(self.page.get_by_text("Vendor Portal", exact=False).first).to_be_visible()
        expect(self.page.locator("input[name='password']")).not_to_be_visible()

    def open_module(self, module: VendorModuleDefinition) -> None:
        """Open a vendor module and verify its heading and optional expected text."""
        self.goto(module.path)
        self.expect_authenticated_shell()
        expect(self.page.get_by_text(module.heading, exact=True).first).to_be_visible()
        if module.expected_text:
            expect(self.page.get_by_text(module.expected_text, exact=False).first).to_be_visible()

    def expect_table_headers(self, *headers: str) -> None:
        """Assert expected vendor table headers are visible; raises on mismatch."""
        for header in headers:
            header_cell = self.page.get_by_role("columnheader", name=header).or_(
                self.page.locator("th").filter(has_text=header)
            ).or_(self.page.get_by_text(header, exact=True))
            expect(header_cell.first).to_be_visible()

    def select_filter(self, name: str, option: str) -> None:
        """Select a named vendor filter option using role and text fallbacks."""
        self.page.get_by_role("combobox", name=name).or_(self.page.get_by_role("button", name=name)).first.click()
        self.page.get_by_role("option", name=option).or_(self.page.get_by_text(option, exact=True)).first.click()
