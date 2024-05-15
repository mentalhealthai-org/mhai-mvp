"""Module with CLI functions."""

import os

from loveai_mvp import __version__
from loveai_mvp.core import (
    get_gpt3_response,
    play_audio,
    read_from_audio,
    record_audio,
    text_to_speech,
)


async def main():
    print("LoveAI Version:", __version__)
    tts_filename = "response.mp3"

    while True:
        print("Listening...")
        record_audio()

        user_input = read_from_audio()

        if user_input.lower().replace(" ", "") in ["goodbye"]:
            print("Conversation ended.")
            break

        response = get_gpt3_response(user_input)
        print(f"AI: {response}")

        await text_to_speech(response, tts_filename)

        play_audio(tts_filename)
        os.remove(tts_filename)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
