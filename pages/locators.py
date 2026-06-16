from __future__ import annotations

"""Centralized locator constants for shared UI areas.

Locator dataclasses group resilient selectors by feature so page objects can
reuse names instead of duplicating selector strings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginLocators:
    """Purpose: Defines reusable selectors for authentication workflows."""
    email_input: str = "input[type='email'], input[name='email'], input[placeholder*='Email' i]"
    password_input: str = "input[type='password'], input[name='password'], input[placeholder*='Password' i]"
    submit_button_name: str = "Sign In"
    logout_menu_text: str = "Log out"
    error_message: str = "[role='alert'], .error, .invalid-feedback, .text-danger, [data-sonner-toast], [data-testid*='toast']"


@dataclass(frozen=True)
class NavigationLocators:
    """Purpose: Defines reusable selectors and labels for primary navigation."""
    sidebar: str = "aside, nav, [data-testid='sidebar']"
    dashboard_link_name: str = "Dashboard"
    agents_link_name: str = "All Agents"
    settings_link_name: str = "Settings"
    profile_menu: str = "[data-testid='profile-menu'], button[aria-haspopup='menu']"


@dataclass(frozen=True)
class AgentLocators:
    """Purpose: Defines reusable selectors and control labels for agent workflows."""
    create_button_name: str = "Create Agent"
    create_confirm_button_name: str = "Create"
    save_button_name: str = "Save Agent"
    update_button_name: str = "Update Agent"
    delete_button_name: str = "Delete"
    confirm_button_name: str = "Delete"
    search_input: str = "input[type='search'], input[placeholder*='Search' i]"
    name_input: str = "input[name='name'], input[placeholder*='Agent' i], input[placeholder='Enter a agent name']"
    description_input: str = "textarea[name='description'], textarea[placeholder*='Description' i]"
    language_select: str = "select[name='language'], [data-testid='language-select']"
    prompt_textarea: str = "textarea[name='prompt'], textarea[placeholder*='Prompt' i], textarea[aria-label='General Prompt']"
    stt_provider: str = "select[name*='stt' i], [data-testid='stt-provider']"
    tts_provider: str = "select[name*='tts' i], [data-testid='tts-provider']"
    voice_select: str = "select[name*='voice' i], [data-testid='voice-select']"
    empty_state: str = "[data-testid='empty-state'], .empty-state"


LOGIN = LoginLocators()
NAVIGATION = NavigationLocators()
AGENT = AgentLocators()
