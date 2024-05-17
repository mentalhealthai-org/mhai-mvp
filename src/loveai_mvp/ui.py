from __future__ import annotations

import asyncio
import os
import re

import pygame
import pygame_emojis

from loveai_mvp import __version__
from loveai_mvp.audio import (
    play_audio,
    read_from_audio,
    record_audio,
    text_to_speech,
)
from loveai_mvp.gpt_models import setup
from loveai_mvp.gpt_models.simple import get_gpt_response


# Pygame configuration
pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

EMOJI_SIZE = (200, 200)
FONT_SIZE = 36

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoveAI")
FONT = pygame.font.Font(None, FONT_SIZE)


def draw_text(text, font, color, surface, x, y) -> None:
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


def print_text(text: str, font=FONT, max_line_length: int = 50) -> None:
    screen.fill(WHITE)
    lines = []

    # Split text by '\n' first to handle manual line breaks
    paragraphs = text.split("\n")

    for paragraph in paragraphs:
        words = paragraph.split(" ")
        current_line = []

        for word in words:
            # Add the word to the current line
            current_line.append(word)
            # Check the width of the current line
            line_width = FONT.size(" ".join(current_line))[0]
            if (
                line_width > WIDTH - 40
            ):  # Add a margin of 20 pixels on each side
                # Remove the last word and start a new line
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]

        # Add the last line of the paragraph
        lines.append(" ".join(current_line))

    # Draw the text lines on the screen
    y_offset = HEIGHT // 2 - len(lines) * font.get_height() // 2
    for i, line in enumerate(lines):
        draw_text(
            line,
            font,
            BLACK,
            screen,
            WIDTH // 2,
            y_offset + i * font.get_height(),
        )
    pygame.display.flip()


def draw_emoji(emoji_char: str, surface, x, y, size) -> None:
    emoji_surface = pygame_emojis.load_emoji(emoji_char, size)
    emoji_rect = emoji_surface.get_rect()
    emoji_rect.center = (x, y)
    surface.blit(emoji_surface, emoji_rect)
    pygame.display.update()


def split_text_by_emoji(text: str) -> list[str]:
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002500-\U00002bef"  # chinese char
        "\U00002702-\U000027b0"
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2b55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\u3030"
        "\u303d"
        "\ufe0f"  # dingbats
        "\u2069"
        "\u2066"
        "\u2068"
        "\u2067"
        "]+",
        flags=re.UNICODE,
    )
    parts = emoji_pattern.split(text)
    emojis = emoji_pattern.findall(text)
    result = []
    for part, em in zip(parts, emojis + [""]):
        result.append((part, em if em else None))
    return result


async def main() -> None:
    print("LoveAI Version:", "1.0")
    tts_filename = "response.mp3"
    conversation_history = setup()

    running = True
    recording = False
    message_press_space_key = (
        "[ Press and hold SPACE to record, release to stop ]"
    )
    display_message = message_press_space_key

    while running:
        screen.fill(WHITE)
        print_text(display_message)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                recording = True
                record_audio()
                user_input = read_from_audio()

                display_message = f"ME: {user_input}\n"
                print_text(display_message)

                if "goodbye" in user_input.lower().replace(" ", ""):
                    print_text("See you later!")
                    running = False
                    break

                response, conversation_history = get_gpt_response(
                    user_input, conversation_history
                )

                response_fragments = split_text_by_emoji(response)

                ai_message = ". ".join(
                    [msg for (msg, em) in response_fragments]
                )

                display_message = (
                    f"ME: {user_input}\n"
                    f"AI: {ai_message}\n\n\n"
                    f"{message_press_space_key}"
                )
                print_text(display_message)

                for fragment, em in response_fragments:
                    if em:
                        draw_emoji(em, screen, WIDTH // 2, 30, FONT_SIZE)

                await text_to_speech(ai_message, tts_filename)
                play_audio(tts_filename)
                os.remove(tts_filename)

                recording = False


def start_ui():
    asyncio.run(main())
    pygame.quit()
