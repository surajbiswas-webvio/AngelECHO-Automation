from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
import os


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


def _as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _as_int(value: str | int | None, default: int) -> int:
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    env: str
    base_url: str
    api_base_url: str
    browser: str
    headless: bool
    default_timeout_ms: int
    slow_mo_ms: int
    trace_on_failure: bool
    video_on_failure: bool
    customer_email: str
    customer_password: str
    admin_email: str | None
    admin_password: str | None
    root_dir: Path = ROOT_DIR


def _load_environment_defaults(env: str) -> dict[str, Any]:
    path = ROOT_DIR / "config" / "environments.yaml"
    with path.open("r", encoding="utf-8") as file:
        environments = yaml.safe_load(file) or {}
    if env not in environments:
        raise ValueError(f"Environment '{env}' is not configured in {path}")
    return environments[env]


def get_settings() -> Settings:
    env = os.getenv("ENV", "qa")
    defaults = _load_environment_defaults(env)
    return Settings(
        env=env,
        base_url=os.getenv("BASE_URL", defaults["base_url"]),
        api_base_url=os.getenv("API_BASE_URL", defaults["api_base_url"]),
        browser=os.getenv("BROWSER", defaults.get("browser", "chromium")),
        headless=_as_bool(os.getenv("HEADLESS"), defaults.get("headless", True)),
        default_timeout_ms=_as_int(os.getenv("DEFAULT_TIMEOUT_MS"), defaults.get("default_timeout_ms", 15000)),
        slow_mo_ms=_as_int(os.getenv("SLOW_MO_MS"), defaults.get("slow_mo_ms", 0)),
        trace_on_failure=_as_bool(os.getenv("TRACE_ON_FAILURE"), True),
        video_on_failure=_as_bool(os.getenv("VIDEO_ON_FAILURE"), False),
        customer_email=os.getenv("CUSTOMER_EMAIL", "new_customer@yopmail.com"),
        customer_password=os.getenv("CUSTOMER_PASSWORD", "Test@123"),
        admin_email=os.getenv("ADMIN_EMAIL") or None,
        admin_password=os.getenv("ADMIN_PASSWORD") or None,
    )

