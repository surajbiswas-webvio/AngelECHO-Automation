from __future__ import annotations

import pytest

from common.api.auth_api import AuthApi
from common.api.agents_api import AgentsApi


@pytest.mark.api
def test_customer_can_fetch_agents_via_api(settings) -> None:
    auth = AuthApi(settings)
    token = auth.login(settings.customer_email, settings.customer_password)
    agents = AgentsApi(settings, token).list_agents()
    assert isinstance(agents, list)
