from __future__ import annotations

"""Regression coverage for customer module validation and read-only workflows."""

import pytest

from pages.billing_page import BillingPage
from pages.compliance_page import CompliancePage
from pages.members_page import MembersPage
from pages.outbound_page import OutboundPage
from pages.phone_numbers_page import PhoneNumbersPage
from pages.pricing_page import PricingPage
from pages.support_page import SupportPage


@pytest.mark.regression
def test_phone_number_purchase_dialog_requires_selection(page, settings) -> None:
    """Verify phone-number purchase cannot proceed until a number is selected."""
    phone_numbers = PhoneNumbersPage(page, settings)
    phone_numbers.open()
    phone_numbers.search_numbers("000000")
    phone_numbers.open_buy_number_dialog()
    phone_numbers.expect_purchase_requires_selection()


@pytest.mark.regression
@pytest.mark.negative
def test_campaign_creation_requires_lead_recipients(page, settings) -> None:
    """Verify campaign creation is blocked when no lead recipients are available."""
    outbound = OutboundPage(page, settings)
    outbound.open()
    outbound.search_campaigns("qa-campaign")
    outbound.open_new_campaign_dialog()
    outbound.expect_campaign_blocked_without_recipients()


@pytest.mark.regression
@pytest.mark.negative
def test_compliance_upload_dialog_exposes_required_document_controls(page, settings) -> None:
    """Verify compliance upload exposes required document and file controls."""
    compliance = CompliancePage(page, settings)
    compliance.open()
    compliance.expect_documents_empty_state()
    compliance.open_upload_document_dialog()
    compliance.expect_upload_form_fields()


@pytest.mark.regression
@pytest.mark.negative
def test_member_invitation_requires_valid_email(page, settings) -> None:
    """Verify member invites require syntactically valid email addresses."""
    members = MembersPage(page, settings)
    members.open()
    members.search_members(settings.customer_email)
    members.expect_owner_visible(settings.customer_email)
    members.open_invite_dialog()
    members.expect_invite_requires_valid_email()


@pytest.mark.regression
def test_support_ticket_form_accepts_required_fields_without_submission(page, settings) -> None:
    """Verify support ticket required fields enable submission without submitting."""
    support = SupportPage(page, settings)
    support.open()
    support.search_tickets("qa-ticket")
    support.expect_empty_state()
    support.open_new_ticket_dialog()
    support.fill_ticket_summary(
        "QA automation validation",
        "Created by automation to verify required support ticket fields before submission.",
    )
    support.expect_ticket_ready_for_submission()


@pytest.mark.regression
def test_billing_and_pricing_surfaces_are_usable(page, settings) -> None:
    """Verify billing tabs and pricing details render without workflow submission."""
    billing = BillingPage(page, settings)
    billing.open()
    billing.expect_usage_metrics()
    billing.switch_to_plans()
    billing.switch_to_payments()

    pricing = PricingPage(page, settings)
    pricing.open()
    pricing.expect_calculator_loaded()
    pricing.open_detailed_pricing()
