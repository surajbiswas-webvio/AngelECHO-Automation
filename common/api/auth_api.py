from __future__ import annotations

from common.api.base_client import BaseApiClient


class AuthApi(BaseApiClient):
    def login(self, email: str, password: str) -> str:
        response = self.post("/login", json={"email": email, "password": password, "app_role": "customer"})
        body = response.json()
        token = body.get("token") or body.get("access_token") or body.get("data", {}).get("token")
        if not token:
            raise ValueError("Login response did not include an access token")
        self.set_token(token)
        return token
