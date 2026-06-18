from __future__ import annotations

"""Base page-object utilities for vendor portal workflows."""

from urllib.parse import urlparse, urlunparse

from utils.config_manager import ConfigManager
from pages.base_page import BasePage


class VendorBasePage(BasePage):
    """Purpose: Routes vendor page objects through the vendor web host."""

    def goto(self, path: str = "") -> None:
        """
        Navigate to a vendor portal route using the vendor-side staging host.

        The regular staging environment points at the customer app host. Vendor
        workflows must instead exercise the vendor host while keeping the same
        route and settings contract.
        """
        url = self._vendor_url_for(path)
        self.logger.info("Navigating to %s", url)
        self.page.goto(url, wait_until="domcontentloaded")
        self.wait_for_page_ready()

    def _vendor_url_for(self, path: str = "") -> str:
        base_url = self.settings.base_url
        parsed = urlparse(base_url)
        if parsed.netloc.startswith("staging-app."):
            parsed = parsed._replace(netloc=parsed.netloc.replace("staging-app.", "staging-vendor.", 1))
            base_url = urlunparse(parsed)
        return ConfigManager.join_url(base_url, path)
