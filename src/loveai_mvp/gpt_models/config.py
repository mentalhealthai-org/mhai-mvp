from __future__ import annotations

from pathlib import Path
from typing import Any

import os

import yaml

from openai import OpenAI

from loveai_mvp.profiles import get_ai_profile, get_user_profile


client = OpenAI()

# Set up your OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def setup() -> list[dict[str, Any]]:
    # Load the AI and user profiles
    ai_profile = get_ai_profile()
    user_profile = get_user_profile()

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
    user_name = user_profile.get("name", "User")

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
        f"```\n{yaml.dump(ai_profile)}\n```"
        f"User profile:\n"
        f"```\n{yaml.dump(user_profile)}\n```"
    )

    system_message = {"role": "system", "content": system_content}
    return system_message
