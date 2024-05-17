from __future__ import annotations

import asyncio
import os
import pygame

from loveai_mvp import __version__
from loveai_mvp.audio import (
    play_audio,
    read_from_audio,
    record_audio,
    text_to_speech,
)

# from loveai_mvp.gpt_models.standalone import get_gpt_response
from loveai_mvp.gpt_models import setup
from loveai_mvp.gpt_models.simple import get_gpt_response


# Pygame configuration
pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoveAI")
FONT = pygame.font.Font(None, 36)


def draw_text(text, font, color, surface, x, y) -> None:
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


def print_text(text: str) -> None:
    screen.fill(WHITE)
    draw_text(
        text,
        FONT,
        BLACK,
        screen,
        WIDTH // 2,
        HEIGHT // 2,
    )
    pygame.display.flip()


async def main() -> None:
    print("LoveAI Version:", "1.0")
    tts_filename = "response.mp3"
    conversation_history = []

    running = True
    recording = False

    while running:
        screen.fill(WHITE)
        print_text(
            "Press and hold SPACE to record, release to stop",
        )
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                recording = True
                record_audio()
                user_input = read_from_audio()

                if "goodbye" in user_input.lower().replace(" ", ""):
                    print_text("See you later!")
                    running = False
                    break

                response, conversation_history = get_gpt_response(
                    user_input, conversation_history
                )
                print_text(
                    f"ME: {user_input}\n"
                    f"AI: {response}\n"
                )

                await text_to_speech(response, tts_filename)
                play_audio(tts_filename)
                os.remove(tts_filename)
                recording = False


def start_ui():
    asyncio.run(main())
    pygame.quit()
