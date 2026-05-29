from __future__ import annotations

import pytest

from pages.vendor_profile_page import VendorProfilePage
from pages.vendor_team_page import VendorTeamPage


@pytest.mark.regression
@pytest.mark.permissions
def test_vendor_owner_can_access_team_tabs_and_member_editor(page, settings) -> None:
    team = VendorTeamPage(page, settings)

    team.open()
    for tab in ("Members", "Teams", "Roles", "Settings"):
        team.open_tab(tab)
    team.open_tab("Members")
    team.open_first_member_editor()


@pytest.mark.regression
@pytest.mark.negative
def test_vendor_team_invite_requires_valid_email(page, settings) -> None:
    VendorTeamPage(page, settings).expect_invite_requires_valid_email()


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_team_add_direct_form_exposes_role_team_and_password_controls(page, settings) -> None:
    VendorTeamPage(page, settings).expect_add_direct_form_ready()


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_profile_edit_fields_are_available(page, settings) -> None:
    VendorProfilePage(page, settings).expect_profile_edit_fields()


@pytest.mark.regression
@pytest.mark.negative
def test_vendor_change_password_requires_matching_values(page, settings) -> None:
    VendorProfilePage(page, settings).expect_password_button_requires_matching_complete_fields()


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_change_password_can_be_enabled_without_submitting(page, settings) -> None:
    VendorProfilePage(page, settings).expect_password_button_enabled_for_matching_fields(settings.user_password)
