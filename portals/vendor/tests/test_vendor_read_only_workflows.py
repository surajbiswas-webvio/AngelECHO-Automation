from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_dashboard_cards_and_recent_leads_navigate(page, settings) -> None:
    page.goto(settings.url_for("/vendor/dashboard"), wait_until="domcontentloaded")
    expect(page.get_by_text("TOTAL LEADS", exact=False).first).to_be_visible()
    expect(page.get_by_text("PIPELINE VALUE", exact=False).first).to_be_visible()
    page.get_by_role("button", name="View All Leads").click()
    expect(page).to_have_url(re.compile(".*/vendor/leads.*"))


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_demo_agents_search_and_manage_action_are_available(page, settings) -> None:
    page.goto(settings.url_for("/vendor/demo-agents"), wait_until="domcontentloaded")
    page.get_by_placeholder("Search by company, lead name, email").fill("Tester")
    expect(page.get_by_role("button", name="Manage").first).to_be_visible()


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_earnings_status_filters_are_available(page, settings) -> None:
    page.goto(settings.url_for("/vendor/earnings"), wait_until="domcontentloaded")
    for status in ("All", "Pending", "Paid", "Cancelled"):
        page.get_by_role("button", name=status).click()
        expect(page.get_by_role("button", name=status)).to_be_visible()


@pytest.mark.regression
@pytest.mark.ui
def test_vendor_plans_copy_and_preview_controls_are_available(page, settings) -> None:
    page.goto(settings.url_for("/vendor/plans"), wait_until="domcontentloaded")
    expect(page.get_by_role("button", name="Copy Link").first).to_be_visible()
    expect(page.get_by_role("button", name="Preview").first).to_be_visible()


@pytest.mark.regression
@pytest.mark.session
def test_vendor_protected_route_redirects_unauthenticated_user(unauthenticated_page, settings) -> None:
    unauthenticated_page.goto(settings.url_for("/vendor/dashboard"), wait_until="domcontentloaded")
    unauthenticated_page.wait_for_load_state("domcontentloaded")
    expect(unauthenticated_page).to_have_url(re.compile(".*/sign-in.*"))
