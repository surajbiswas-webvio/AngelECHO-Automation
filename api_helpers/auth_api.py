from __future__ import annotations

"""Authentication API helper for token-based test setup."""

from api_helpers.base_client import BaseApiClient


class AuthApi(BaseApiClient):
    """
    Purpose:
        Encapsulates API authentication behavior.

    Why Needed:
        API tests need a reusable way to exchange credentials for a bearer
        token before calling protected endpoints.

    Args:
        Inherits Settings and optional token arguments from BaseApiClient.

    Returns:
        AuthApi instance with BaseApiClient request methods.

    Notes:
        The helper updates its own session token after a successful login.
    """

    def login(self, email: str, password: str) -> str:
        """
        Purpose:
            Logs in through the API and stores the returned access token.

        Why Needed:
            Downstream API helpers require authorization for protected routes.

        Args:
            email: User email address.
            password: User password.

        Returns:
            Access token extracted from the login response.

        Notes:
            Supports multiple token response shapes used by backend versions.
        """
        response = self.post("/login", json={"email": email, "password": password, "app_role": "customer"})
        body = response.json()
        token = body.get("token") or body.get("access_token") or body.get("data", {}).get("token")
        if not token:
            raise ValueError("Login response did not include an access token")
        self.set_token(token)
        return token
