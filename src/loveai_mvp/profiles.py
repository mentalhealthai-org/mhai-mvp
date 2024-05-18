from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROFILES_PATH = Path(__file__).parent / "data" / "profiles"


def read_profile(file_path) -> dict[str, Any]:
    """
    Read the profile data from a YAML file.

    Parameters
    ----------
    file_path : str
        The path to the YAML file.

    Returns
    -------
    dict
        The profile data.
    """
    with open(file_path, "r") as file:
        profile_data = yaml.safe_load(file)
    return profile_data


def get_ai_profile() -> dict[str, Any]:
    return read_profile(PROFILES_PATH / "ai" / "ai.yaml")


def get_user_profile(username) -> dict[str, Any]:
    return read_profile(PROFILES_PATH / "users" / f"{username}.yaml")
