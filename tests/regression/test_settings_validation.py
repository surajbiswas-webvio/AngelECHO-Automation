from __future__ import annotations

from copy import deepcopy
from datetime import datetime

import pytest

from pages.ai_agents_page import AIAgentsPage
from utils.data_loader import get_data_group


@pytest.mark.regression
def test_stt_tts_and_voice_settings_can_be_saved(page, settings) -> None:
    agent = deepcopy(get_data_group("agents.json", "valid_agent"))
    agent["name"] = f"QA Settings {datetime.now().strftime('%H%M%S')}"
    agents_page = AIAgentsPage(page, settings)
    created = False
    try:
        agents_page.create_agent(agent)
        created = True
        agents_page.open_agent(agent["name"])
        agents_page.fill_prompt("Settings validation prompt updated by automation.")
        agents_page.save()
    finally:
        if created:
            agents_page.delete_agent(agent["name"])
