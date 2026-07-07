from __future__ import annotations

"""AI agents API helper methods used by API-level tests."""

from typing import Any

from api_helpers.base_client import BaseApiClient


class AgentsApi(BaseApiClient):
    """
    Purpose:
        Provides business-level API operations for AI agents.

    Why Needed:
        Tests can create, list, update, and delete agents without duplicating
        endpoint paths or workspace lookup logic.

    Args:
        Inherits Settings and optional token arguments from BaseApiClient.

    Returns:
        AgentsApi instance with agent-specific helper methods.

    Notes:
        Methods return parsed response data where the API response contains a
        JSON body.
    """

    def list_agents(self, workspace_id: int | str | None = None) -> list[dict[str, Any]]:
        """
        Purpose:
            Fetches agents for a workspace.

        Why Needed:
            API smoke coverage needs to validate that authenticated customers
            can read their agent inventory.

        Args:
            workspace_id: Optional workspace id; defaults to the first
                available workspace for the authenticated user.

        Returns:
            List of agent dictionaries.

        Notes:
            Handles both wrapped `{data: [...]}` and raw list response shapes.
        """
        resolved_workspace_id = workspace_id or self._get_default_workspace_id()
        response = self.get(f"/all-agents/{resolved_workspace_id}")
        body = response.json()
        return body.get("data", body if isinstance(body, list) else [])

    def _get_default_workspace_id(self) -> int | str:
        """
        Purpose:
            Resolves the first workspace id for the authenticated customer.

        Why Needed:
            Agent list endpoints require a workspace id, but tests generally
            should not hardcode environment-specific workspace values.

        Args:
            None.

        Returns:
            Workspace id as returned by the API.

        Notes:
            Raises ValueError when no workspace is available.
        """
        response = self.get("/workspaces")
        body = response.json()
        workspaces = body.get("data", body if isinstance(body, list) else [])
        if not workspaces:
            raise ValueError("No workspace is available for the authenticated customer.")
        return workspaces[0]["id"]

    def create_agent(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Purpose:
            Creates an agent using the supplied API payload.

        Why Needed:
            CRUD and setup workflows need a reusable create operation.

        Args:
            payload: JSON-serializable agent request body.

        Returns:
            Parsed JSON response from the create request.

        Notes:
            Validation errors are surfaced by BaseApiClient through HTTPError.
        """
        return self.post("/agents", json=payload).json()

    def update_agent(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Purpose:
            Updates an existing agent by id.

        Why Needed:
            Regression tests need to validate edit workflows through the API.

        Args:
            agent_id: Identifier of the agent to update.
            payload: JSON-serializable update request body.

        Returns:
            Parsed JSON response from the update request.

        Notes:
            The method does not mutate the input payload.
        """
        return self.put(f"/agents/{agent_id}", json=payload).json()

    def delete_agent(self, agent_id: str) -> None:
        """
        Purpose:
            Deletes an agent by id.

        Why Needed:
            Test cleanup should remove API-created data to keep environments
            reusable.

        Args:
            agent_id: Identifier of the agent to delete.

        Returns:
            None.

        Notes:
            Any API failure is raised by the shared DELETE helper.
        """
        self.delete(f"/agents/{agent_id}")
