from __future__ import annotations

from types import SimpleNamespace

from pages.vendor_base_page import VendorBasePage


def _vendor_page_for(base_url: str) -> VendorBasePage:
    page = object.__new__(VendorBasePage)
    page.settings = SimpleNamespace(base_url=base_url)
    return page


def test_vendor_page_routes_regular_staging_to_vendor_host() -> None:
    page = _vendor_page_for("https://staging-app.webvio.in/")

    assert page._vendor_url_for("/vendor/leads") == "https://staging-vendor.webvio.in/vendor/leads"


def test_vendor_page_keeps_vendor_staging_host() -> None:
    page = _vendor_page_for("https://staging-vendor.webvio.in/")

    assert page._vendor_url_for("/vendor/leads") == "https://staging-vendor.webvio.in/vendor/leads"
