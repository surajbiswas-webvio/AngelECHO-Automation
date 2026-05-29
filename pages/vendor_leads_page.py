from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import expect

from pages.base_page import BasePage


@dataclass(frozen=True)
class VendorLead:
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


class VendorLeadsPage(BasePage):
    def open(self) -> None:
        self.goto("/vendor/leads")
        expect(self.page.get_by_text("My Leads", exact=True).first).to_be_visible()

    def open_add_lead(self) -> None:
        self.page.get_by_role("button", name="Add Lead").click()
        expect(self.page.get_by_placeholder("John Doe")).to_be_visible()

    def fill_lead_form(self, lead: VendorLead) -> None:
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
        self.open()
        self.open_add_lead()
        self.fill_lead_form(lead)
        self.page.get_by_role("button", name="Create Lead").click()
        expect(self.toast()).to_contain_text("Lead created")
        self.expect_lead_visible(lead.company)

    def search(self, value: str) -> None:
        self.page.get_by_placeholder("Search leads...").fill(value)
        self.page.wait_for_timeout(300)

    def row_for(self, company: str):
        return self.page.locator("tbody tr").filter(has_text=company).first

    def expect_lead_visible(self, company: str) -> None:
        self.search(company)
        expect(self.row_for(company)).to_be_visible()

    def open_row_menu(self, company: str) -> None:
        self.expect_lead_visible(company)
        self.row_for(company).locator("button").last.click()
        expect(self.page.get_by_role("menuitem", name="View Details").first).to_be_visible()

    def view_lead(self, company: str) -> None:
        self.open_row_menu(company)
        self.page.get_by_role("menuitem", name="View Details").first.click()
        expect(self.page.get_by_text(company, exact=False).first).to_be_visible()
        expect(self.page.get_by_role("button", name="Edit Lead")).to_be_visible()

    def edit_lead(self, company: str) -> None:
        self.open_row_menu(company)
        self.page.get_by_role("menuitem", name="Edit Lead").first.click()
        expect(self.page.get_by_role("button", name="Update Lead")).to_be_visible()

    def update_notes(self, company: str, notes: str) -> None:
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
        self.open()
        self.open_add_lead()
        self.page.get_by_role("button", name="Create Lead").click()
        expect(self.page.get_by_placeholder("John Doe")).to_be_visible()
        expect(self.page.get_by_role("button", name="Create Lead")).to_be_visible()

    def expect_search_empty_state(self, value: str) -> None:
        self.open()
        self.search(value)
        expect(self.page.get_by_text("No leads found", exact=False).first).to_be_visible()

    def toast(self):
        return self.page.locator("[data-sonner-toast], [role='status'], [role='alert']").first
