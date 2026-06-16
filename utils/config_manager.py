from __future__ import annotations

"""Configuration loading and URL normalization helpers.

The ConfigManager isolates `.env` loading, YAML environment defaults, required
setting validation, and URL joining so higher-level fixtures can stay focused
on test orchestration.
"""

import os
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml
from dotenv import load_dotenv


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


class ConfigManager:
    """
    Purpose:
        Loads runtime configuration from project-level files and environment
        variables.

    Why Needed:
        Centralizes validation rules for environment names, required values,
        and URL formatting.

    Args:
        root_dir: Repository root used to locate `.env` and YAML config files.

    Returns:
        ConfigManager instances expose helper methods; construction returns no
        direct data.

    Notes:
        The class is intentionally filesystem-light after initialization.
    """

    def __init__(self, root_dir: Path) -> None:
        """
        Purpose:
            Stores project paths required for configuration lookup.

        Why Needed:
            All settings resolution needs a stable repository root.

        Args:
            root_dir: Absolute or relative repository root path.

        Returns:
            None.

        Notes:
            The environment YAML path is derived once for reuse.
        """
        self.root_dir = root_dir
        self.environments_path = root_dir / "config" / "environments.yaml"

    def load_dotenv_files(self) -> str:
        """
        Purpose:
            Loads base and environment-specific dotenv files.

        Why Needed:
            Allows local secrets and environment overrides without committing
            sensitive values to source control.

        Args:
            None.

        Returns:
            Active environment name, defaulting to `staging`.

        Notes:
            Existing process variables take precedence because dotenv loading
            uses `override=False`.
        """
        load_dotenv(self.root_dir / ".env", override=False)
        env = os.getenv("ENV", "staging").strip() or "staging"
        load_dotenv(self.root_dir / f".env.{env}", override=False)
        return env

    def load_environment_defaults(self, env: str) -> dict[str, Any]:
        """
        Purpose:
            Reads YAML defaults for the selected environment.

        Why Needed:
            Keeps shared non-secret defaults, such as URLs and timeouts, under
            version control.

        Args:
            env: Environment key to load from `config/environments.yaml`.

        Returns:
            Dictionary of defaults for the requested environment.

        Notes:
            Raises ConfigurationError when the environment is not configured.
        """
        with self.environments_path.open("r", encoding="utf-8") as file:
            environments = yaml.safe_load(file) or {}
        if env not in environments:
            configured = ", ".join(sorted(environments)) or "none"
            raise ConfigurationError(
                f"Environment '{env}' is not configured in {self.environments_path}. "
                f"Configured environments: {configured}"
            )
        return environments[env] or {}

    @staticmethod
    def get_value(name: str, defaults: dict[str, Any], *, required: bool = False) -> str | None:
        """
        Purpose:
            Resolves a setting from environment variables or YAML defaults.

        Why Needed:
            Provides a predictable override order for runtime configuration.

        Args:
            name: Environment-variable style setting name.
            defaults: YAML defaults for the active environment.
            required: Whether missing or empty values should fail the run.

        Returns:
            String value when present; otherwise None.

        Notes:
            YAML keys are expected to use lowercase names.
        """
        value = os.getenv(name)
        if value is None:
            value = defaults.get(name.lower())
        if isinstance(value, str):
            value = value.strip()
        if required and not value:
            raise ConfigurationError(f"Required environment setting '{name}' is missing or empty.")
        return str(value) if value is not None and value != "" else None

    @staticmethod
    def normalize_base_url(value: str, *, name: str = "BASE_URL") -> str:
        """
        Purpose:
            Validates and normalizes an absolute base URL.

        Why Needed:
            UI and API URL construction depends on base URLs having a scheme,
            host, and trailing slash.

        Args:
            value: Raw URL value to validate.
            name: Setting name used in error messages.

        Returns:
            Absolute URL with exactly one trailing slash.

        Notes:
            Only http and https schemes are accepted.
        """
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ConfigurationError(f"{name} must be an absolute http(s) URL. Received: {value!r}")
        return value.rstrip("/") + "/"

    @staticmethod
    def join_url(base_url: str, path: str = "") -> str:
        """
        Purpose:
            Joins a normalized base URL with a route or endpoint path.

        Why Needed:
            Prevents duplicated slash handling throughout page objects and API
            clients.

        Args:
            base_url: Absolute base URL.
            path: Optional path fragment.

        Returns:
            Absolute joined URL.

        Notes:
            Handles both leading-slash and relative path inputs.
        """
        normalized_base = base_url.rstrip("/") + "/"
        return urljoin(normalized_base, path.lstrip("/"))
