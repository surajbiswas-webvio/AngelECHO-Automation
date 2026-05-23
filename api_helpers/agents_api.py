from __future__ import annotations

from typing import Any

from api_helpers.base_client import BaseApiClient


class AgentsApi(BaseApiClient):
    def list_agents(self) -> list[dict[str, Any]]:
        response = self.get("/agents")
        body = response.json()
        return body.get("data", body if isinstance(body, list) else [])

    def create_agent(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.post("/agents", json=payload).json()

    def update_agent(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.put(f"/agents/{agent_id}", json=payload).json()

    def delete_agent(self, agent_id: str) -> None:
        self.delete(f"/agents/{agent_id}")

