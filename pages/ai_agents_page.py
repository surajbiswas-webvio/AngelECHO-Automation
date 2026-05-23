from __future__ import annotations

from typing import Any

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.locators import AGENT


class AIAgentsPage(BasePage):
    def open(self) -> None:
        self.goto("/agents")

    def start_create_agent(self) -> None:
        self.page.get_by_role("button", name=AGENT.create_button_name).click()

    def fill_agent_details(self, agent: dict[str, Any]) -> None:
        self.fill(AGENT.name_input, agent["name"])
        if agent.get("description"):
            self.fill(AGENT.description_input, agent["description"])
        if agent.get("language"):
            self.select_option(AGENT.language_select, agent["language"])
        if agent.get("prompt"):
            self.fill(AGENT.prompt_textarea, agent["prompt"])

    def configure_stt(self, provider: str) -> None:
        self.select_option(AGENT.stt_provider, provider)

    def configure_tts(self, provider: str, voice: str | None = None) -> None:
        self.select_option(AGENT.tts_provider, provider)
        if voice:
            self.select_option(AGENT.voice_select, voice)

    def save(self) -> None:
        save_button = self.page.get_by_role("button", name=AGENT.save_button_name).or_(
            self.page.get_by_role("button", name=AGENT.update_button_name)
        )
        expect(save_button.first).to_be_enabled()
        save_button.first.click()
        self.wait_for_page_ready()

    def create_agent(self, agent: dict[str, Any]) -> None:
        self.open()
        self.start_create_agent()
        self.fill_agent_details(agent)
        if agent.get("stt_provider"):
            self.configure_stt(agent["stt_provider"])
        if agent.get("tts_provider"):
            self.configure_tts(agent["tts_provider"], agent.get("voice"))
        self.save()

    def search_agent(self, name: str) -> None:
        self.fill(AGENT.search_input, name)
        self.page.keyboard.press("Enter")
        self.wait_for_page_ready()

    def open_agent(self, name: str) -> None:
        self.search_agent(name)
        self.page.get_by_text(name, exact=False).first.click()
        self.wait_for_page_ready()

    def update_prompt(self, name: str, prompt: str) -> None:
        self.open_agent(name)
        self.fill(AGENT.prompt_textarea, prompt)
        self.save()

    def delete_agent(self, name: str) -> None:
        self.open_agent(name)
        self.page.get_by_role("button", name=AGENT.delete_button_name).click()
        self.page.get_by_role("button", name=AGENT.confirm_button_name).click()
        self.wait_for_page_ready()

    def expect_agent_visible(self, name: str) -> None:
        self.search_agent(name)
        expect(self.page.get_by_text(name, exact=False).first).to_be_visible()

    def expect_validation_error(self, message: str | None = None) -> None:
        error = self.page.locator("[role='alert'], .invalid-feedback, .text-danger, [data-testid*='error']").first
        expect(error).to_be_visible()
        if message:
            expect(error).to_contain_text(message)

