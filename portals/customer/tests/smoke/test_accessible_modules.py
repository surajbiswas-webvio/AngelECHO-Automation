from __future__ import annotations

import pytest

from portals.customer.pages.module_page import MODULES, ModulePage


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.parametrize("module", MODULES, ids=[module.name for module in MODULES])
def test_authenticated_user_can_open_accessible_modules(page, settings, module) -> None:
    ModulePage(page, settings).expect_module_loaded(module)


@pytest.mark.smoke
def test_core_data_tables_render_expected_headers(page, settings) -> None:
    modules = ModulePage(page, settings)

    modules.open_module(next(module for module in MODULES if module.name == "All Agents"))
    modules.expect_table_headers("Agent Name", "Mode", "Type", "Language", "Actions")

    modules.open_module(next(module for module in MODULES if module.name == "Members"))
    modules.expect_table_headers("Member", "Email Address", "Role", "Actions")

    modules.open_module(next(module for module in MODULES if module.name == "Support"))
    modules.expect_table_headers("Ticket ID", "Subject", "Category", "Priority", "Status", "Created", "Actions")
