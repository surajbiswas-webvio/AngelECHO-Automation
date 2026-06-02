from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import os

from common.utils.config_manager import ConfigManager, ConfigurationError

ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_MANAGER = ConfigManager(ROOT_DIR)


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
    portal: str
    base_url: str
    admin_base_url: str
    vendor_base_url: str
    customer_base_url: str
    api_base_url: str
    browser: str
    headless: bool
    default_timeout_ms: int
    slow_mo_ms: int
    trace_on_failure: bool
    video_on_failure: bool
    customer_email: str
    customer_password: str
    vendor_email: str
    vendor_password: str
    user_email: str
    user_password: str
    authenticated_shell_text: str
    admin_email: str | None
    admin_password: str | None
    root_dir: Path = ROOT_DIR

    def url_for(self, path: str = "") -> str:
        return ConfigManager.join_url(self.base_url, path)

    def api_url_for(self, path: str = "") -> str:
        return ConfigManager.join_url(self.api_base_url, path)


def get_settings() -> Settings:
    env = CONFIG_MANAGER.load_dotenv_files()
    defaults = CONFIG_MANAGER.load_environment_defaults(env)
    portal = (os.getenv("PORTAL") or defaults.get("portal") or "").strip().lower()
    if not portal:
        portal = "vendor" if env.startswith("vendor") else "customer"
    if portal not in {"admin", "vendor", "customer"}:
        raise ConfigurationError(f"PORTAL must be one of admin, vendor, or customer. Received: {portal!r}")

    customer_base_url = _get_portal_base_url("CUSTOMER", defaults)
    vendor_base_url = _get_portal_base_url("VENDOR", defaults)
    admin_base_url = _get_portal_base_url("ADMIN", defaults)
    portal_base_urls = {
        "admin": admin_base_url,
        "vendor": vendor_base_url,
        "customer": customer_base_url,
    }
    base_url = portal_base_urls[portal]

    api_base_url = CONFIG_MANAGER.get_value("API_BASE_URL", defaults)
    if api_base_url:
        api_base_url = CONFIG_MANAGER.normalize_base_url(api_base_url, name="API_BASE_URL")
    else:
        api_base_url = ConfigManager.join_url(base_url, "api/")

    customer_email = os.getenv("CUSTOMER_EMAIL", "new_customer@yopmail.com")
    customer_password = os.getenv("CUSTOMER_PASSWORD", "Test@123")
    vendor_email = os.getenv("VENDOR_EMAIL") or ""
    vendor_password = os.getenv("VENDOR_PASSWORD") or ""
    admin_email = os.getenv("ADMIN_EMAIL") or None
    admin_password = os.getenv("ADMIN_PASSWORD") or None
    portal_credentials = {
        "admin": (admin_email or "", admin_password or ""),
        "vendor": (vendor_email, vendor_password),
        "customer": (customer_email, customer_password),
    }
    user_email, user_password = portal_credentials[portal]
    if portal in {"admin", "vendor"} and (not user_email or not user_password):
        raise ConfigurationError(f"{portal.upper()}_EMAIL and {portal.upper()}_PASSWORD are required for {portal.title()} Portal runs.")

    return Settings(
        env=env,
        portal=portal,
        base_url=base_url,
        admin_base_url=admin_base_url,
        vendor_base_url=vendor_base_url,
        customer_base_url=customer_base_url,
        api_base_url=api_base_url,
        browser=os.getenv("BROWSER", defaults.get("browser", "chromium")),
        headless=_as_bool(os.getenv("HEADLESS"), defaults.get("headless", True)),
        default_timeout_ms=_as_int(os.getenv("DEFAULT_TIMEOUT_MS"), defaults.get("default_timeout_ms", 15000)),
        slow_mo_ms=_as_int(os.getenv("SLOW_MO_MS"), defaults.get("slow_mo_ms", 0)),
        trace_on_failure=_as_bool(os.getenv("TRACE_ON_FAILURE"), True),
        video_on_failure=_as_bool(os.getenv("VIDEO_ON_FAILURE"), False),
        customer_email=customer_email,
        customer_password=customer_password,
        vendor_email=vendor_email,
        vendor_password=vendor_password,
        user_email=user_email,
        user_password=user_password,
        authenticated_shell_text=CONFIG_MANAGER.get_value("AUTHENTICATED_SHELL_TEXT", defaults) or "",
        admin_email=admin_email,
        admin_password=admin_password,
    )


def _get_portal_base_url(portal_prefix: str, defaults: dict[str, object]) -> str:
    setting_name = f"{portal_prefix}_BASE_URL"
    raw_value = CONFIG_MANAGER.get_value(setting_name, defaults)
    if not raw_value:
        raise ConfigurationError(f"Required environment setting '{setting_name}' is missing or empty.")
    return CONFIG_MANAGER.normalize_base_url(raw_value, name=setting_name)
