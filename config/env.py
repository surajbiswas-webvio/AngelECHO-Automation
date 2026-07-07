from __future__ import annotations

"""Compatibility exports for environment-aware settings access.

Importing this module resolves the active settings once and exposes the
Settings type, factory, and singleton-style `settings` value for older tests
or scripts that expect `config.env`.
"""

from config.settings import Settings, get_settings


settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
