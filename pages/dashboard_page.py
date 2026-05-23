from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class DashboardPage(BasePage):
    def open(self) -> None:
        self.goto("/dashboard")

    def expect_loaded(self) -> None:
        dashboard_text = self.page.get_by_role("heading", name="Dashboard").or_(
            self.page.get_by_text("Dashboard", exact=False)
        )
        expect(dashboard_text.first).to_be_visible()

    def get_metric_value(self, metric_label: str) -> str:
        metric = self.page.get_by_text(metric_label, exact=False).locator("xpath=ancestor::*[self::div or self::section][1]")
        expect(metric.first).to_be_visible()
        return metric.first.inner_text()
