from __future__ import annotations

from copy import deepcopy
from datetime import datetime

import pytest

from pages.ai_agents_page import AIAgentsPage
from utils.data_loader import get_data_group


@pytest.mark.regression
def test_stt_tts_and_voice_settings_can_be_saved(page, settings) -> None:
    agent = deepcopy(get_data_group("agents.json", "valid_agent"))
    agent["name"] = f"Settings Validation Agent {datetime.now().strftime('%Y%m%d%H%M%S')}"
    agents_page = AIAgentsPage(page, settings)
    agents_page.create_agent(agent)
    agents_page.open_agent(agent["name"])
    agents_page.configure_stt(agent["stt_provider"])
    agents_page.configure_tts(agent["tts_provider"], agent["voice"])
    agents_page.save()
