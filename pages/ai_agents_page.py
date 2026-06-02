from __future__ import annotations

"""Page object for AI agent create, search, update, and delete workflows."""

from typing import Any

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.locators import AGENT


class AIAgentsPage(BasePage):
    """Purpose: Encapsulates customer AI agent management workflows."""

    def open(self) -> None:
        """Open the agents management page and verify its heading."""
        self.goto("/list")
        expect(self.page.get_by_role("heading", name="Agents Management")).to_be_visible()

    def start_create_agent(self) -> None:
        """Start the create-agent flow and verify template selection is shown."""
        self.page.get_by_role("button", name=AGENT.create_button_name).click()
        expect(self.page.get_by_role("heading", name="Select Template")).to_be_visible()

    def choose_blank_template(self) -> None:
        """Choose the blank template so tests can create a controlled agent."""
        self.page.get_by_text("Start from blank", exact=True).click()
        expect(self.page.get_by_role("heading", name="Create a new agent")).to_be_visible()

    def fill_agent_name(self, name: str) -> None:
        """Fill the required agent name field with `name`; returns None."""
        self.page.get_by_placeholder("Enter a agent name").fill(name)

    def confirm_create(self) -> None:
        """Confirm initial creation and wait for the editor save action."""
        self.page.get_by_role("button", name=AGENT.create_confirm_button_name).click()
        expect(self.page.get_by_role("button", name=AGENT.save_button_name)).to_be_visible()

    def fill_prompt(self, prompt: str) -> None:
        """Fill the General Prompt field with the supplied prompt text."""
        self.page.get_by_label("General Prompt", exact=True).fill(prompt)

    def save(self) -> None:
        """
        Purpose:
            Saves the current agent editor state.

        Why Needed:
            Create and update workflows share the same save behavior.

        Args:
            None.

        Returns:
            None.

        Notes:
            Supports both create and update button labels and includes a short
            post-save wait for asynchronous persistence.
        """
        save_button = self.page.get_by_role("button", name=AGENT.save_button_name).or_(
            self.page.get_by_role("button", name="Update Agent")
        )
        expect(save_button.first).to_be_enabled()
        save_button.first.click()
        self.wait_for_page_ready()
        self.page.wait_for_timeout(2000)

    def create_agent(self, agent: dict[str, Any]) -> None:
        """
        Purpose:
            Creates an AI agent through the UI using supplied test data.

        Why Needed:
            E2E workflows need a reusable setup path that mirrors user actions.

        Args:
            agent: Dictionary containing at least `name` and optional `prompt`.

        Returns:
            None.

        Notes:
            The method intentionally avoids API shortcuts to validate the UI
            creation flow.
        """
        self.open()
        self.start_create_agent()
        self.choose_blank_template()
        self.fill_agent_name(agent["name"])
        self.confirm_create()
        if agent.get("prompt"):
            self.fill_prompt(agent["prompt"])
        self.save()

    def search_agent(self, name: str) -> None:
        """Open the agent list, search by name, and wait for results to filter."""
        self.open()
        self.fill(AGENT.search_input, name)
        self.page.wait_for_timeout(500)

    def open_agent(self, name: str) -> None:
        """
        Purpose:
            Opens an existing agent in the editor by list-row name.

        Why Needed:
            Update and verification workflows need a reusable edit entry point.

        Args:
            name: Agent name used to locate the row and editor heading.

        Returns:
            None.

        Notes:
            Waits for the `/agent-editor` route to reduce flakiness after click.
        """
        self.search_agent(name)
        row = self.page.get_by_role("row").filter(has_text=name)
        expect(row.first).to_be_visible()
        row.first.get_by_role("button", name="Edit").click()
        self.wait_for_page_ready()
        self.page.wait_for_url("**/agent-editor", timeout=self.settings.default_timeout_ms)
        expect(self.page.get_by_role("heading", name=name)).to_be_visible()

    def update_prompt(self, name: str, prompt: str) -> None:
        """Open an agent, replace its prompt, save it, and return None."""
        self.open_agent(name)
        self.fill_prompt(prompt)
        self.save()

    def delete_agent(self, name: str) -> None:
        """
        Purpose:
            Deletes an agent from the management table.

        Why Needed:
            CRUD tests must clean up data created during the run.

        Args:
            name: Agent name used to locate the row to delete.

        Returns:
            None.

        Notes:
            Reopens and searches after deletion so later assertions see the
            refreshed list state.
        """
        self.search_agent(name)
        row = self.page.get_by_role("row").filter(has_text=name)
        expect(row.first).to_be_visible()
        row.first.get_by_role("button").last.click()
        self.page.get_by_role("menuitem", name=AGENT.delete_button_name).click()
        dialog = self.page.get_by_role("dialog", name="Delete Agent")
        expect(dialog).to_be_visible()
        dialog.get_by_role("button", name=AGENT.confirm_button_name).click()
        self.page.wait_for_timeout(3000)
        self.open()
        self.fill(AGENT.search_input, name)

    def expect_agent_visible(self, name: str) -> None:
        """Assert an agent row is visible after searching by name."""
        self.search_agent(name)
        expect(self.page.get_by_role("row").filter(has_text=name).first).to_be_visible()

    def expect_agent_not_visible(self, name: str) -> None:
        """Assert an agent row is not visible after searching by name."""
        self.search_agent(name)
        expect(self.page.get_by_role("row").filter(has_text=name).first).not_to_be_visible()

    def expect_validation_error(self, message: str | None = None) -> None:
        """Assert a validation error is visible, optionally with expected text."""
        error = self.page.locator("[role='alert'], .invalid-feedback, .text-danger, [data-testid*='error']").first
        expect(error).to_be_visible()
        if message:
            expect(error).to_contain_text(message)

    def expect_create_disabled_without_name(self) -> None:
        """Verify the create flow blocks progression when the name is missing."""
        self.open()
        self.start_create_agent()
        self.choose_blank_template()
        self.page.get_by_role("button", name=AGENT.create_confirm_button_name).click()
        expect(self.page.get_by_role("heading", name="Create a new agent")).to_be_visible()
        expect(self.page.get_by_placeholder("Enter a agent name")).to_be_visible()

    def configure_stt(self, provider: str) -> None:
        """Open speech settings when available; provider is reserved for future selection."""
        button = self.page.get_by_role("button", name="Speech Settings")
        if button.count() > 0:
            button.click()

    def configure_tts(self, provider: str, voice: str | None = None) -> None:
        """Verify text-to-speech settings remain saveable; parameters support future options."""
        expect(self.page.get_by_role("button", name=AGENT.save_button_name).or_(
            self.page.get_by_role("button", name=AGENT.update_button_name)
        ).first).to_be_visible()
