from __future__ import annotations

"""Base HTTP client for AngelECHO API automation.

The client wraps requests.Session with environment-aware URL construction,
common JSON headers, bearer-token support, logging, and status validation.
"""

from typing import Any

import requests
from requests import Response, Session

from config.settings import Settings
from utils.logger import get_logger


class BaseApiClient:
    """
    Purpose:
        Provides shared request behavior for specialized API helper classes.

    Why Needed:
        Keeps authentication headers, base URL handling, logging, and response
        status validation consistent across API tests.

    Args:
        settings: Runtime API configuration.
        token: Optional bearer token applied during construction.

    Returns:
        Client instances return requests.Response objects from request methods.

    Notes:
        Subclasses should expose business-specific methods and delegate HTTP
        mechanics to this base class.
    """

    def __init__(self, settings: Settings, token: str | None = None) -> None:
        """
        Purpose:
            Initializes a reusable requests session for the target API.

        Why Needed:
            Sessions keep default headers and authorization state in one place.

        Args:
            settings: Runtime API settings.
            token: Optional authentication token.

        Returns:
            None.

        Notes:
            JSON accept/content headers are applied to every request.
        """
        self.settings = settings
        self.session: Session = requests.Session()
        self.logger = get_logger(self.__class__.__name__)
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        if token:
            self.set_token(token)

    def set_token(self, token: str) -> None:
        """
        Purpose:
            Adds or replaces the Authorization header for API calls.

        Why Needed:
            Authenticated endpoints require a bearer token after login.

        Args:
            token: Raw token or already-prefixed bearer token.

        Returns:
            None.

        Notes:
            The method preserves tokens that already include `Bearer`.
        """
        authorization = token if token.lower().startswith("bearer ") else f"Bearer {token}"
        self.session.headers.update({"Authorization": authorization})

    def request(self, method: str, path: str, **kwargs: Any) -> Response:
        """
        Purpose:
            Sends an HTTP request to an environment-relative API path.

        Why Needed:
            Provides shared timeout, logging, URL joining, and status handling
            for all specialized API helpers.

        Args:
            method: HTTP method such as GET, POST, PUT, or DELETE.
            path: API endpoint path relative to `api_base_url`.
            **kwargs: Additional requests arguments such as `json` or params.

        Returns:
            requests.Response after `raise_for_status` succeeds.

        Notes:
            HTTP 4xx/5xx responses raise requests.HTTPError immediately.
        """
        url = self.settings.api_url_for(path)
        response = self.session.request(method=method, url=url, timeout=30, **kwargs)
        self.logger.info("%s %s -> %s", method.upper(), url, response.status_code)
        response.raise_for_status()
        return response

    def get(self, path: str, **kwargs: Any) -> Response:
        """
        Purpose:
            Sends a GET request through the shared request pipeline.

        Why Needed:
            Keeps call sites concise while preserving common validation.

        Args:
            path: API endpoint path.
            **kwargs: Optional requests keyword arguments.

        Returns:
            requests.Response for the GET call.

        Notes:
            Delegates all mechanics to `request`.
        """
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        """
        Purpose:
            Sends a POST request through the shared request pipeline.

        Why Needed:
            Supports create/login workflows with consistent logging and errors.

        Args:
            path: API endpoint path.
            **kwargs: Optional requests keyword arguments.

        Returns:
            requests.Response for the POST call.

        Notes:
            Payloads are usually supplied with the `json` keyword.
        """
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Response:
        """
        Purpose:
            Sends a PUT request through the shared request pipeline.

        Why Needed:
            Supports update workflows with consistent behavior.

        Args:
            path: API endpoint path.
            **kwargs: Optional requests keyword arguments.

        Returns:
            requests.Response for the PUT call.

        Notes:
            Delegates all mechanics to `request`.
        """
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Response:
        """
        Purpose:
            Sends a DELETE request through the shared request pipeline.

        Why Needed:
            Supports cleanup workflows while preserving common status handling.

        Args:
            path: API endpoint path.
            **kwargs: Optional requests keyword arguments.

        Returns:
            requests.Response for the DELETE call.

        Notes:
            Delegates all mechanics to `request`.
        """
        return self.request("DELETE", path, **kwargs)
