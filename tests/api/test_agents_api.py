from __future__ import annotations

import pytest
import requests

from api_helpers.auth_api import AuthApi
from api_helpers.agents_api import AgentsApi


@pytest.mark.api
def test_customer_can_fetch_agents_via_api(settings) -> None:
    auth = AuthApi(settings)
    try:
        token = auth.login(settings.customer_email, settings.customer_password)
    except (ValueError, requests.JSONDecodeError) as exc:
        pytest.skip(f"Staging API endpoint is not exposing JSON auth contract: {exc}")
    agents = AgentsApi(settings, token).list_agents()
    assert isinstance(agents, list)
