from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from config.settings import ROOT_DIR
from utils.exceptions import TestDataError


DATA_DIR = ROOT_DIR / "data"


def load_json(file_name: str) -> dict[str, Any]:
    path = DATA_DIR / file_name
    if not path.exists():
        raise TestDataError(f"Test data file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_yaml(file_name: str) -> dict[str, Any]:
    path = DATA_DIR / file_name
    if not path.exists():
        raise TestDataError(f"Test data file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_data_group(file_name: str, group: str) -> Any:
    data = load_json(file_name) if file_name.endswith(".json") else load_yaml(file_name)
    if group not in data:
        raise TestDataError(f"Group '{group}' not found in {file_name}")
    return data[group]

