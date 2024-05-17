from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from loveai_mvp.gpt_models.config import client


def generate_standalone_question(new_question, conversation_history):
    """
    Generate a standalone question based on the new question and chat history.

    Parameters
    ----------
    new_question : str
        The new user question.
    conversation_history : list
        The list of message dictionaries maintaining the conversation history.

    Returns
    -------
    str
        The standalone question.
    """
    instruction = (
        "Generate a standalone answer or comment which is based on the new "
        "input from the user plus the chat history. "
        "Remember that you should act as a real person. "
        "Be lovely and kind, remember you have a name and the user as well. "
        "Just create the standalone question without commentary. "
        "New input: " + new_question
    )

    history_with_instruction = conversation_history + [
        {"role": "user", "content": instruction}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.9,
        max_tokens=150,
        messages=history_with_instruction,
    )

    standalone_question = response.choices[0].message.content.strip()
    return standalone_question


def get_gpt_response(
    prompt: str, conversation_history: list[dict, Any]
) -> tuple[str, list[dict[str, Any]]]:
    """
    Get a response from the GPT-3 model for a given prompt, maintaining the conversation history.

    Parameters
    ----------
    prompt : str
        The user's input prompt.
    conversation_history : list
        The list of message dictionaries maintaining the conversation history.

    Returns
    -------
    str
        The response from the GPT-3 model.
    list[dict[str, Any]]
        conversation_history
    """
    # Generate the standalone question
    standalone_question = generate_standalone_question(
        prompt, conversation_history
    )

    # Prepare the message for the GPT-3 response
    messages = [{"role": "user", "content": standalone_question}]

    # Get the chat completion response
    chat_completion = client.chat.completions.create(
        model="gpt-4o", temperature=0.9, max_tokens=150, messages=messages
    )

    # Extract the assistant's message
    assistant_message = chat_completion.choices[0].message.content

    # Append the new user message and assistant message to the conversation history
    conversation_history.append({"role": "user", "content": prompt})
    conversation_history.append(
        {"role": "assistant", "content": assistant_message}
    )

    return assistant_message, conversation_history
