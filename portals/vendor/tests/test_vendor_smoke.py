from __future__ import annotations

import pytest

from portals.vendor.pages.vendor_module_page import VENDOR_MODULES, VendorModulePage


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.parametrize("module", VENDOR_MODULES, ids=[module.name for module in VENDOR_MODULES])
def test_vendor_user_can_open_accessible_modules(page, settings, module) -> None:
    VendorModulePage(page, settings).open_module(module)


@pytest.mark.smoke
@pytest.mark.ui
def test_vendor_core_tables_render_expected_headers(page, settings) -> None:
    modules = VendorModulePage(page, settings)

    modules.open_module(next(module for module in VENDOR_MODULES if module.name == "My Leads"))
    modules.expect_table_headers(
        "Business Name",
        "Contact",
        "Phone",
        "Business Type",
        "Plan",
        "Lead Type",
        "Payment",
        "Created by",
        "Created",
        "Actions",
    )

    modules.open_module(next(module for module in VENDOR_MODULES if module.name == "Earnings"))
    modules.expect_table_headers("DATE", "LEAD", "CUSTOMER PAID", "RATE", "YOUR SHARE", "STATUS", "PAID ON")

    modules.open_module(next(module for module in VENDOR_MODULES if module.name == "Performance"))
    modules.expect_table_headers("AGENT", "LEADS", "DEMOS", "CONVERSIONS", "CONV RATE", "COMMISSION")

    modules.open_module(next(module for module in VENDOR_MODULES if module.name == "Help & Support"))
    modules.expect_table_headers("Ticket ID", "Subject", "Category", "Priority", "Status", "Created", "Actions")
