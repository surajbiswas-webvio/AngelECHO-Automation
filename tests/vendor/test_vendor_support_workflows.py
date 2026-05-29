from __future__ import annotations

from datetime import datetime

import pytest

from pages.vendor_support_page import VendorSupportPage


@pytest.mark.regression
@pytest.mark.negative
def test_vendor_support_ticket_requires_subject(page, settings) -> None:
    VendorSupportPage(page, settings).expect_required_validation()


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_support_ticket_form_supports_required_fields_and_upload(page, settings, tmp_path) -> None:
    attachment = tmp_path / "support-note.txt"
    attachment.write_text("QA support attachment", encoding="utf-8")
    support = VendorSupportPage(page, settings)

    support.open()
    support.open_new_ticket()
    support.fill_ticket(
        f"QA ticket validation {datetime.now().strftime('%H%M%S')}",
        "Automation verifies ticket fields and file upload control before submission.",
    )
    support.attach_file(attachment)
    support.expect_submit_ready()


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_support_search_and_details_are_available(page, settings) -> None:
    support = VendorSupportPage(page, settings)

    support.open()
    support.search("TKT")
    support.open_first_ticket_details()
