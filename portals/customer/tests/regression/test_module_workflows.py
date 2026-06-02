from __future__ import annotations

import pytest

from portals.customer.pages.billing_page import BillingPage
from portals.customer.pages.compliance_page import CompliancePage
from portals.customer.pages.members_page import MembersPage
from portals.customer.pages.outbound_page import OutboundPage
from portals.customer.pages.phone_numbers_page import PhoneNumbersPage
from portals.customer.pages.pricing_page import PricingPage
from portals.customer.pages.support_page import SupportPage


@pytest.mark.regression
def test_phone_number_purchase_dialog_requires_selection(page, settings) -> None:
    phone_numbers = PhoneNumbersPage(page, settings)
    phone_numbers.open()
    phone_numbers.search_numbers("000000")
    phone_numbers.open_buy_number_dialog()
    phone_numbers.expect_purchase_requires_selection()


@pytest.mark.regression
@pytest.mark.negative
def test_campaign_creation_requires_lead_recipients(page, settings) -> None:
    outbound = OutboundPage(page, settings)
    outbound.open()
    outbound.search_campaigns("qa-campaign")
    outbound.open_new_campaign_dialog()
    outbound.expect_campaign_blocked_without_recipients()


@pytest.mark.regression
@pytest.mark.negative
def test_compliance_upload_dialog_exposes_required_document_controls(page, settings) -> None:
    compliance = CompliancePage(page, settings)
    compliance.open()
    compliance.expect_documents_empty_state()
    compliance.open_upload_document_dialog()
    compliance.expect_upload_form_fields()


@pytest.mark.regression
@pytest.mark.negative
def test_member_invitation_requires_valid_email(page, settings) -> None:
    members = MembersPage(page, settings)
    members.open()
    members.search_members(settings.customer_email)
    members.expect_owner_visible(settings.customer_email)
    members.open_invite_dialog()
    members.expect_invite_requires_valid_email()


@pytest.mark.regression
def test_support_ticket_form_accepts_required_fields_without_submission(page, settings) -> None:
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
    billing = BillingPage(page, settings)
    billing.open()
    billing.expect_usage_metrics()
    billing.switch_to_plans()
    billing.switch_to_payments()

    pricing = PricingPage(page, settings)
    pricing.open()
    pricing.expect_calculator_loaded()
    pricing.open_detailed_pricing()
