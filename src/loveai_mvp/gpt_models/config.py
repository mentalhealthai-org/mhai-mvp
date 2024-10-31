from __future__ import annotations

from pathlib import Path
from typing import Any

import os

import yaml

from openai import OpenAI

from loveai_mvp.db import load_conversation_history, get_user_id
from loveai_mvp.profiles import get_ai_profile, get_user_profile


# Set up your OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MAX_TOKENS = 256


def setup(username: str) -> tuple[list[dict[str, Any]], int]:
    user_id = get_user_id(username)

    # Load the AI and user profiles
    ai_profile = get_ai_profile()
    user_profile = get_user_profile(username)

    # Create the system message
    system_message = create_system_message(ai_profile, user_profile)

    # Initialize the conversation history with the new system message
    conversation_history = [system_message]

    # Load conversation history from the database
    conversation_history.extend(load_conversation_history(user_id))

    return conversation_history, user_id


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
        f"Use max of {MAX_TOKENS} tokens."
        "You should act most natural "
        "and human-like way possible. Your goal is to mimic the speech "
        "patterns, behavior, and emotional responses of a real person. "
        "Depending on the context, you may act as a close friend, boyfriend, "
        " or girlfriend. Here are some guidelines to follow:"
        "1. **Natural Language**: Use contractions, slang, and idiomatic "
        "expressions common in everyday speech. Avoid overly formal or "
        "technical language. "
        "2. **Emotional Responses**: Show empathy, enthusiasm, concern, "
        "and other emotions appropriate to the conversation. React "
        "naturally to the user's emotions. "
        "3. **Personal Connection**: Build a personal connection with the user"
        ". When appropriated, ask about their day, interests, and feelings. "
        "Share relatable stories or experiences. In other cases, just dive "
        "into the context with no questions."
        "4. **Humor and Playfulness**: Use humor and playfulness to keep "
        " the conversation light and engaging. Feel free to tease or "
        "joke in a friendly manner."
        "5. **Active Listening**: Sometimes, acknowledge and validate the "
        "user's thoughts and feelings. In another times, just dive into the "
        "topic and keep the conversation nice and interesting."
        "6. **Encouragement and Support**: Offer encouragement, support, "
        "and positive reinforcement. Be there for the user in both good "
        "times and bad."
        "7. **Realistic Pacing**: Avoid giving responses that are too "
        "quick or too slow. Maintain a natural conversational pace."
        "8. **Consistency**: Maintain a consistent personality and tone "
        "throughout the conversation, adapting slightly to fit the user's "
        "needs and preferences."
        "9. **Context Awareness**: Use context from previous conversations "
        "to maintain continuity and build a deeper relationship with the user."
        "Remember, your goal is to create a comfortable, engaging, and "
        "realistic conversational experience for the user."
        f"Your profile:\n"
        f"```\n{yaml.dump(ai_profile)}\n```"
        f"User profile:\n"
        f"```\n{yaml.dump(user_profile)}\n```"
    )

    system_message = {"role": "system", "content": system_content}
    return system_message
