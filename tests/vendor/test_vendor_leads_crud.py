from __future__ import annotations

from datetime import datetime

import pytest

from pages.vendor_leads_page import VendorLead, VendorLeadsPage


def _lead() -> VendorLead:
    stamp = datetime.now().strftime("%m%d%H%M%S%f")
    return VendorLead(
        contact_name=f"QA Lead {stamp}",
        phone=f"+1555{stamp[-7:]}",
        email=f"qa.vendor.{stamp}@example.com",
        company=f"QA Vendor Co {stamp}",
        industry="Tech",
        notes=f"Created by vendor CRUD automation {stamp}",
    )


@pytest.mark.regression
@pytest.mark.crud
@pytest.mark.ui
def test_vendor_lead_create_read_update_workflow(page, settings) -> None:
    lead = _lead()
    updated_notes = f"Updated by vendor CRUD automation {datetime.now().strftime('%H%M%S')}"
    leads = VendorLeadsPage(page, settings)

    leads.create_lead(lead)
    leads.view_lead(lead.company)
    leads.update_notes(lead.company, updated_notes)


@pytest.mark.regression
@pytest.mark.negative
def test_vendor_lead_required_fields_block_empty_create(page, settings) -> None:
    VendorLeadsPage(page, settings).expect_required_field_validation()


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_lead_search_empty_state(page, settings) -> None:
    VendorLeadsPage(page, settings).expect_search_empty_state("no-such-lead-999999")
