from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml
from dotenv import load_dotenv


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


class ConfigManager:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.environments_path = root_dir / "config" / "environments.yaml"

    def load_dotenv_files(self) -> str:
        load_dotenv(self.root_dir / ".env", override=False)
        env = os.getenv("ENV", "staging").strip() or "staging"
        load_dotenv(self.root_dir / f".env.{env}", override=False)
        return env

    def load_environment_defaults(self, env: str) -> dict[str, Any]:
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
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ConfigurationError(f"{name} must be an absolute http(s) URL. Received: {value!r}")
        return value.rstrip("/") + "/"

    @staticmethod
    def join_url(base_url: str, path: str = "") -> str:
        normalized_base = base_url.rstrip("/") + "/"
        return urljoin(normalized_base, path.lstrip("/"))
