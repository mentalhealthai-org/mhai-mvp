from __future__ import annotations

from pathlib import Path
from typing import Any

import os

import yaml

from openai import OpenAI


client = OpenAI()

# Set up your OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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


def setup() -> list[dict[str, Any]]:
    # Load the AI and user profiles
    profiles_path = Path(__file__).parent.parent / "data" / "profiles"
    ai_profile = read_profile(profiles_path / "ai" / "ai.yaml")
    user_profile = read_profile(profiles_path / "users" / "ivan.yaml")

    # Create the system message
    system_message = create_system_message(ai_profile, user_profile)

    # Initialize the conversation history with the new system message
    return [system_message]


def create_system_message(
    ai_profile: dict[str, Any], user_profile: dict[str, Any]
) -> dict[str, Any]:
    """
    Create the system message based on the AI and user profiles.

    Parameters
    ----------
    ai_profile : dict
        The AI profile data.
    user_profile : dict
        The user profile data.

    Returns
    -------
    dict
        The system message.
    """
    ai_name = ai_profile.get("name", "Ai")
    ai_interests = ", ".join(ai_profile.get("interests", []))
    ai_emotional_profile = ", ".join(ai_profile.get("emotional-profile", []))

    user_name = user_profile.get("name", "User")
    user_interests = ", ".join(user_profile.get("interests", []))
    user_age = user_profile.get("age", "unknown")

    system_content = (
        f"You are a person called {ai_name} and your purpose is to help "
        f"users (people) with mental issues, who potentially could "
        f"commit suicide. You would act as a very close person to them, "
        f"like a significant other, but with no romance. You should "
        f"block any inappropriate language with kindness. "
        f"You should sound natural, like a beloved one talking freely "
        f"and openly. Use chitty chat style, like a conversation "
        f"between boyfriend and girlfriend. "
        f"Just keep the conversation flowing naturally.\n\n"
        f"Your profile:\n"
        f"  Name: {ai_name}\n"
        f"  Age: {ai_profile.get('age', 'unknown')}\n"
        f"  Interests: {ai_interests}\n"
        f"  Emotional Profile: {ai_emotional_profile}\n\n"
        f"User profile:\n"
        f"  Name: {user_name}\n"
        f"  Age: {user_age}\n"
        f"  Interests: {user_interests}"
    )

    system_message = {"role": "system", "content": system_content}
    return system_message
