"""Module with CLI functions."""

import os

from loveai_mvp import __version__
from loveai_mvp.core import (
    play_audio,
    read_from_audio,
    record_audio,
    text_to_speech,
)

# from loveai_mvp.gpt_models.standalone import get_gpt_response
from loveai_mvp.gpt_models import setup
from loveai_mvp.gpt_models.simple import get_gpt_response


async def main():
    print("LoveAI Version:", __version__)
    tts_filename = "response.mp3"
    conversation_history = setup()

    while True:
        print("Listening...")
        record_audio()

        user_input = read_from_audio()

        if user_input.lower().replace(" ", "") in ["goodbye"]:
            print("Conversation ended.")
            break

        response, conversation_history = get_gpt_response(
            user_input, conversation_history
        )
        print(f"AI: {response}")

        await text_to_speech(response, tts_filename)

        play_audio(tts_filename)
        os.remove(tts_filename)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
