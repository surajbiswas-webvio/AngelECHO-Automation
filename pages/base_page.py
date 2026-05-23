from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings
from utils.logger import get_logger
from utils.screenshot import capture_screenshot


class BasePage:
    def __init__(self, page: Page, settings: Settings) -> None:
        self.page = page
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self.page.set_default_timeout(settings.default_timeout_ms)

    def goto(self, path: str = "") -> None:
        url = f"{self.settings.base_url.rstrip('/')}/{path.lstrip('/')}"
        self.logger.info("Navigating to %s", url)
        self.page.goto(url, wait_until="domcontentloaded")
        self.wait_for_page_ready()

    def wait_for_page_ready(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, target: str | Locator) -> None:
        locator = target if isinstance(target, Locator) else self.page.locator(target)
        expect(locator.first).to_be_visible()
        expect(locator.first).to_be_enabled()
        locator.first.click()

    def fill(self, selector: str, value: str) -> None:
        field = self.page.locator(selector).first
        expect(field).to_be_visible()
        field.fill(value)

    def select_option(self, selector: str, value: str) -> None:
        field = self.page.locator(selector).first
        expect(field).to_be_visible()
        field.select_option(value=value)

    def click_button(self, name: str) -> None:
        self.click(self.page.get_by_role("button", name=name))

    def visible_text(self, text: str) -> Locator:
        return self.page.get_by_text(text, exact=False)

    def expect_visible(self, target: str | Locator) -> None:
        locator = target if isinstance(target, Locator) else self.page.locator(target)
        expect(locator.first).to_be_visible()

    def expect_not_visible(self, target: str | Locator) -> None:
        locator = target if isinstance(target, Locator) else self.page.locator(target)
        expect(locator.first).not_to_be_visible()

    def capture(self, name: str) -> Path:
        return capture_screenshot(self.page, name)

