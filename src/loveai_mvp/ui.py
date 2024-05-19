from __future__ import annotations

import asyncio
import os
import re

from datetime import datetime

import kivy

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from loveai_mvp import __version__
from loveai_mvp.audio import AudioAi
from loveai_mvp.db import init_db, save_conversation
from loveai_mvp.gpt_models import setup
from loveai_mvp.gpt_models.simple import get_gpt_response
from loveai_mvp.profiles import get_ai_profile, get_user_profile


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


class LoveAIApp(App):
    def build(self):
        self.username = "ivan"  # Set this to the actual username
        self.conversation_history, self.user_id = setup(self.username)

        self.layout = BoxLayout(orientation="vertical")
        self.label = Label(text="LoveAI", size_hint_y=None, height=40)
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.messages = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.messages.bind(minimum_height=self.messages.setter("height"))
        self.scroll_view.add_widget(self.messages)

        self.record_button = Button(
            text="Hold to Record", size_hint_y=None, height=50
        )
        self.record_button.bind(on_press=self.start_recording)
        self.record_button.bind(on_release=self.stop_recording)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.record_button)

        self.audio = AudioAi(
            user_profile=get_user_profile(username=self.username),
            ai_profile=get_ai_profile(),
        )

        return self.layout

    def start_recording(self, instance) -> None:
        self.label.text = "Listening..."
        self.audio.start_recording()

    def stop_recording(self, instance) -> None:
        self.label.text = "Processing..."
        self.audio.stop_recording()
        self.process_audio(instance)

    def process_audio(self, instance) -> None:
        user_input = self.audio.read_from_audio()
        if (
            "goodbye" in user_input.lower().replace(" ", "")
            or user_input == ""
        ):
            self.display_message("See you later!")
            self.stop()
            return

        self.display_message(f"ME: {user_input}")
        print("=" * 80)
        print(user_input)

        response, self.conversation_history = get_gpt_response(
            user_input, self.conversation_history
        )
        print("=" * 80)
        print(response)
        response_fragments = split_text_by_emoji(response)

        ai_message = ". ".join([msg for (msg, em) in response_fragments])
        self.display_message(f"AI: {ai_message}")

        for fragment, em in response_fragments:
            if em:
                self.display_message(em, is_emoji=True)

        asyncio.run(self.speak_and_save(user_input, ai_message))

    def display_message(self, message: str, is_emoji: bool = False) -> None:
        if is_emoji:
            message_label = Label(
                text=message,
                markup=True,
                size_hint_y=None,
                height=30,
                font_size="20sp",
            )
        else:
            message_label = Label(
                text=message, size_hint_y=None, height=30, font_size="20sp"
            )
        self.messages.add_widget(message_label)
        self.scroll_view.scroll_to(message_label)

    async def speak_and_save(self, user_input: str, ai_message: str) -> None:
        await self.audio.text_to_speech(ai_message)
        self.play_audio()

        # sentiment = get_sentiment(user_input)
        # emotions = get_emotions(user_input)

        save_conversation(
            self.user_id,
            user_input,
            ai_message,  # sentiment, str(emotions)
        )

    def play_audio(self) -> None:
        self.sound = SoundLoader.load(self.audio.ai_audio_path)
        if self.sound:
            self.sound.play()
            Clock.schedule_interval(self.check_audio_state, 0.1)

    def check_audio_state(self, dt) -> None:
        if not self.sound.state == "play":
            self.sound.stop()
            os.remove(self.audio.ai_audio_path)
            Clock.unschedule(self.check_audio_state)


def start_ui() -> None:
    init_db()
    LoveAIApp().run()
