from __future__ import annotations

"""Page object and data model for vendor lead CRUD workflows."""

from dataclasses import dataclass

from playwright.sync_api import expect

from pages.vendor_base_page import VendorBasePage


@dataclass(frozen=True)
class VendorLead:
    """Purpose: Represents vendor lead form data used by CRUD tests."""
    contact_name: str
    phone: str
    email: str
    company: str
    industry: str
    address: str = "123 QA Street"
    owner_name: str = "QA Owner"
    decision_maker: str = "QA Decision Maker"
    website: str = "https://example.com"
    notes: str = "Created by vendor automation"


class VendorLeadsPage(VendorBasePage):
    """Purpose: Encapsulates vendor lead list, create, view, edit, and search actions."""

    def open(self) -> None:
        """Open vendor leads and verify the My Leads surface is visible."""
        self.goto("/vendor/leads")
        expect(self.page.get_by_text("My Leads", exact=True).first).to_be_visible()

    def open_add_lead(self) -> None:
        """Open the add-lead form and verify the first required field is present."""
        self.page.get_by_role("button", name="Add Lead").click()
        expect(self.page.get_by_placeholder("John Doe")).to_be_visible()

    def fill_lead_form(self, lead: VendorLead) -> None:
        """Fill all reusable vendor lead fields from a VendorLead object."""
        self.page.get_by_placeholder("John Doe").fill(lead.contact_name)
        self.page.get_by_placeholder("Phone number").fill(lead.phone)
        self.page.get_by_placeholder("john@example.com").fill(lead.email)
        self.page.get_by_placeholder("Acme Corp").fill(lead.company)
        self.page.get_by_placeholder("e.g. Flower Shop, Restaurant, Medical").fill(lead.industry)
        self.page.get_by_placeholder("123 Main St, City, State").fill(lead.address)
        self.page.get_by_placeholder("Business owner").fill(lead.owner_name)
        self.page.get_by_placeholder("Decision maker").fill(lead.decision_maker)
        self.page.get_by_placeholder("https://example.com").fill(lead.website)
        self.page.get_by_placeholder("Additional notes about this lead...").fill(lead.notes)

    def create_lead(self, lead: VendorLead) -> None:
        """Create a lead through the UI, assert success toast, and verify row visibility."""
        self.open()
        self.open_add_lead()
        self.fill_lead_form(lead)
        self.page.get_by_role("button", name="Create Lead").click()
        expect(self.toast()).to_contain_text("Lead created")
        self.expect_lead_visible(lead.company)

    def search(self, value: str) -> None:
        """Search vendor leads by value and wait for client-side filtering."""
        self.page.get_by_placeholder("Search leads...").fill(value)
        self.page.wait_for_timeout(300)

    def row_for(self, company: str):
        """Return the first table row locator matching the supplied company name."""
        return self.page.locator("tbody tr").filter(has_text=company).first

    def expect_lead_visible(self, company: str) -> None:
        """Assert a vendor lead row is visible after searching by company."""
        self.search(company)
        expect(self.row_for(company)).to_be_visible()

    def open_row_menu(self, company: str) -> None:
        """Open the action menu for a vendor lead row identified by company."""
        self.expect_lead_visible(company)
        self.row_for(company).locator("button").last.click()
        expect(self.page.get_by_role("menuitem", name="View Details").first).to_be_visible()

    def view_lead(self, company: str) -> None:
        """Open lead details and verify the detail view and edit action are visible."""
        self.open_row_menu(company)
        self.page.get_by_role("menuitem", name="View Details").first.click()
        expect(self.page.get_by_text(company, exact=False).first).to_be_visible()
        expect(self.page.get_by_role("button", name="Edit Lead")).to_be_visible()

    def edit_lead(self, company: str) -> None:
        """Open the edit form for a lead identified by company."""
        self.open_row_menu(company)
        self.page.get_by_role("menuitem", name="Edit Lead").first.click()
        expect(self.page.get_by_role("button", name="Update Lead")).to_be_visible()

    def update_notes(self, company: str, notes: str) -> None:
        """
        Purpose:
            Updates lead notes and verifies the new notes appear in details.

        Why Needed:
            CRUD regression coverage must confirm edit persistence through the
            user interface.

        Args:
            company: Company name used to find the lead.
            notes: Replacement notes text.

        Returns:
            None.

        Notes:
            Closes any existing details dialog before opening edit mode.
        """
        close = self.page.get_by_role("button", name="Close")
        if close.count() > 0 and close.first.is_visible():
            close.first.click()
        self.edit_lead(company)
        self.page.get_by_placeholder("Additional notes about this lead...").fill(notes)
        self.page.get_by_role("button", name="Update Lead").click()
        expect(self.toast()).to_contain_text("Lead updated")
        self.view_lead(company)
        expect(self.page.get_by_text(notes, exact=False)).to_be_visible()

    def expect_required_field_validation(self) -> None:
        """Verify empty lead creation keeps the form visible and blocks creation."""
        self.open()
        self.open_add_lead()
        self.page.get_by_role("button", name="Create Lead").click()
        expect(self.page.get_by_placeholder("John Doe")).to_be_visible()
        expect(self.page.get_by_role("button", name="Create Lead")).to_be_visible()

    def expect_search_empty_state(self, value: str) -> None:
        """Search with a missing value and assert the empty-state message appears."""
        self.open()
        self.search(value)
        expect(self.page.get_by_text("No leads found", exact=False).first).to_be_visible()

    def toast(self):
        """Return the current toast/status/alert locator for lead workflow assertions."""
        return self.page.locator("[data-sonner-toast], [role='status'], [role='alert']").first
