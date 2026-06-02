from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from config.settings import ROOT_DIR
from common.utils.exceptions import TestDataError


DEFAULT_PORTAL = "customer"
PORTALS_DIR = ROOT_DIR / "portals"


def _data_path(file_name: str, portal: str = DEFAULT_PORTAL) -> Path:
    candidate = PORTALS_DIR / portal / "data" / file_name
    if candidate.exists():
        return candidate
    return ROOT_DIR / "common" / "data" / file_name


def load_json(file_name: str, portal: str = DEFAULT_PORTAL) -> dict[str, Any]:
    path = _data_path(file_name, portal)
    if not path.exists():
        raise TestDataError(f"Test data file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_yaml(file_name: str, portal: str = DEFAULT_PORTAL) -> dict[str, Any]:
    path = _data_path(file_name, portal)
    if not path.exists():
        raise TestDataError(f"Test data file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_data_group(file_name: str, group: str, portal: str = DEFAULT_PORTAL) -> Any:
    data = load_json(file_name, portal) if file_name.endswith(".json") else load_yaml(file_name, portal)
    if group not in data:
        raise TestDataError(f"Group '{group}' not found in {file_name}")
    return data[group]

