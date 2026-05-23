from __future__ import annotations

from copy import deepcopy
from datetime import datetime

import pytest

from pages.ai_agents_page import AIAgentsPage
from utils.data_loader import get_data_group


def _agent_payload() -> dict[str, str]:
    run_id = datetime.now().strftime("%Y%m%d%H%M%S")
    payload = deepcopy(get_data_group("agents.json", "valid_agent"))
    payload["name"] = payload["name"].replace("${RUN_ID}", run_id)
    return payload


@pytest.mark.e2e
@pytest.mark.regression
def test_create_search_update_and_delete_ai_agent(page, settings) -> None:
    agent = _agent_payload()
    agents_page = AIAgentsPage(page, settings)

    agents_page.create_agent(agent)
    agents_page.expect_agent_visible(agent["name"])

    updated_prompt = get_data_group("agents.json", "updated_prompt")
    agents_page.update_prompt(agent["name"], updated_prompt)

    agents_page.delete_agent(agent["name"])


@pytest.mark.negative
@pytest.mark.regression
def test_agent_creation_requires_mandatory_fields(page, settings) -> None:
    agents_page = AIAgentsPage(page, settings)
    agents_page.open()
    agents_page.start_create_agent()
    agents_page.save()
    agents_page.expect_validation_error()

