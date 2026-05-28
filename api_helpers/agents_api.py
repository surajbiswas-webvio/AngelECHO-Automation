from __future__ import annotations

from typing import Any

from api_helpers.base_client import BaseApiClient


class AgentsApi(BaseApiClient):
    def list_agents(self, workspace_id: int | str | None = None) -> list[dict[str, Any]]:
        resolved_workspace_id = workspace_id or self._get_default_workspace_id()
        response = self.get(f"/all-agents/{resolved_workspace_id}")
        body = response.json()
        return body.get("data", body if isinstance(body, list) else [])

    def _get_default_workspace_id(self) -> int | str:
        response = self.get("/workspaces")
        body = response.json()
        workspaces = body.get("data", body if isinstance(body, list) else [])
        if not workspaces:
            raise ValueError("No workspace is available for the authenticated customer.")
        return workspaces[0]["id"]

    def create_agent(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.post("/agents", json=payload).json()

    def update_agent(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.put(f"/agents/{agent_id}", json=payload).json()

    def delete_agent(self, agent_id: str) -> None:
        self.delete(f"/agents/{agent_id}")
