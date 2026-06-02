from __future__ import annotations

"""Test-data loading helpers for JSON and YAML fixtures.

The helpers provide a small validation layer around files in `data/` so tests
fail with framework-specific errors when fixture files or groups are missing.
"""

import json
from pathlib import Path
from typing import Any

import yaml

from config.settings import ROOT_DIR
from utils.exceptions import TestDataError


DATA_DIR = ROOT_DIR / "data"


def load_json(file_name: str) -> dict[str, Any]:
    """
    Purpose:
        Loads a JSON data file from the project data directory.

    Why Needed:
        Centralizes file lookup and missing-file errors for JSON fixtures.

    Args:
        file_name: Name of the JSON file inside `data/`.

    Returns:
        Parsed JSON object as a dictionary.

    Notes:
        Raises TestDataError when the requested file does not exist.
    """
    path = DATA_DIR / file_name
    if not path.exists():
        raise TestDataError(f"Test data file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_yaml(file_name: str) -> dict[str, Any]:
    """
    Purpose:
        Loads a YAML data file from the project data directory.

    Why Needed:
        Supports structured test credentials or lookup data alongside JSON.

    Args:
        file_name: Name of the YAML file inside `data/`.

    Returns:
        Parsed YAML dictionary, or an empty dictionary for empty files.

    Notes:
        Raises TestDataError when the requested file does not exist.
    """
    path = DATA_DIR / file_name
    if not path.exists():
        raise TestDataError(f"Test data file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_data_group(file_name: str, group: str) -> Any:
    """
    Purpose:
        Retrieves a named data group from a JSON or YAML fixture file.

    Why Needed:
        Keeps tests focused on workflow intent instead of parsing fixture
        structures directly.

    Args:
        file_name: Data fixture file name.
        group: Top-level group key to retrieve.

    Returns:
        Data stored under the requested group key.

    Notes:
        Chooses JSON vs YAML loading based on the file extension.
    """
    data = load_json(file_name) if file_name.endswith(".json") else load_yaml(file_name)
    if group not in data:
        raise TestDataError(f"Group '{group}' not found in {file_name}")
    return data[group]
