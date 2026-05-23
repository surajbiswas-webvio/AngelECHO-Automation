from __future__ import annotations

from typing import Any

import requests
from requests import Response, Session

from config.settings import Settings
from utils.logger import get_logger


class BaseApiClient:
    def __init__(self, settings: Settings, token: str | None = None) -> None:
        self.settings = settings
        self.session: Session = requests.Session()
        self.logger = get_logger(self.__class__.__name__)
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        if token:
            self.set_token(token)

    def set_token(self, token: str) -> None:
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def request(self, method: str, path: str, **kwargs: Any) -> Response:
        url = f"{self.settings.api_base_url.rstrip('/')}/{path.lstrip('/')}"
        response = self.session.request(method=method, url=url, timeout=30, **kwargs)
        self.logger.info("%s %s -> %s", method.upper(), url, response.status_code)
        response.raise_for_status()
        return response

    def get(self, path: str, **kwargs: Any) -> Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Response:
        return self.request("DELETE", path, **kwargs)

