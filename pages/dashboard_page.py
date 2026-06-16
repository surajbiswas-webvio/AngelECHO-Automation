from __future__ import annotations

"""Page object for customer dashboard checks."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Purpose: Encapsulates dashboard navigation and metric assertions."""

    def open(self) -> None:
        """Purpose: Opens the dashboard root route for the active environment."""
        self.goto("")

    def expect_loaded(self) -> None:
        """
        Purpose:
            Verifies that the dashboard's primary content is available.

        Why Needed:
            Smoke tests and login flows use the dashboard as an authenticated
            landing-page signal.

        Args:
            None.

        Returns:
            None.

        Notes:
            Supports heading and text fallback selectors for UI resilience.
        """
        dashboard_text = self.page.get_by_role("heading", name="Live Calls").or_(
            self.page.get_by_text("Live Calls", exact=False)
        )
        expect(dashboard_text.first).to_be_visible()

    def get_metric_value(self, metric_label: str) -> str:
        """
        Purpose:
            Reads the text content for a dashboard metric card.

        Why Needed:
            Future metric assertions can reuse card lookup by visible label.

        Args:
            metric_label: Label text identifying the metric card.

        Returns:
            Full text content of the metric container.

        Notes:
            Uses an ancestor lookup so both label and value are returned.
        """
        metric = self.page.get_by_text(metric_label, exact=False).locator("xpath=ancestor::*[self::div or self::section][1]")
        expect(metric.first).to_be_visible()
        return metric.first.inner_text()
