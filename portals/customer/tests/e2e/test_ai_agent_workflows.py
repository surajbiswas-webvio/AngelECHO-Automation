from __future__ import annotations

from copy import deepcopy
from datetime import datetime

import pytest

from portals.customer.pages.ai_agents_page import AIAgentsPage
from common.utils.data_loader import get_data_group


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
    created = False

    try:
        agents_page.create_agent(agent)
        created = True
        agents_page.expect_agent_visible(agent["name"])

        updated_prompt = get_data_group("agents.json", "updated_prompt")
        agents_page.update_prompt(agent["name"], updated_prompt)
        agents_page.open_agent(agent["name"])
        agents_page.expect_visible(page.get_by_label("General Prompt", exact=True))
    finally:
        if created:
            agents_page.delete_agent(agent["name"])

    agents_page.expect_agent_not_visible(agent["name"])


@pytest.mark.negative
@pytest.mark.regression
def test_agent_creation_requires_mandatory_fields(page, settings) -> None:
    agents_page = AIAgentsPage(page, settings)
    agents_page.expect_create_disabled_without_name()
