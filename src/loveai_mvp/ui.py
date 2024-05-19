from __future__ import annotations

import asyncio
import os
import re

from datetime import datetime
from functools import partial

import kivy

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from loveai_mvp import __version__
from loveai_mvp.audio import AudioAi
from loveai_mvp.db import init_db, save_conversation
from loveai_mvp.gpt_models import setup
from loveai_mvp.gpt_models.simple import get_gpt_response
from loveai_mvp.profiles import get_ai_profile, get_user_profile
from loveai_mvp.utils.text import split_text_by_emoji


class LoveAIApp(App):
    def __init__(self, **kwargs):
        super(LoveAIApp, self).__init__(**kwargs)
        self.message_labels = []  # To keep track of message labels

    def build(self) -> BoxLayout:
        self.username = "ivan"  # Set this to the actual username
        self.conversation_history, self.user_id = setup(self.username)

        self.layout = BoxLayout(orientation="vertical")
        self.label = Label(text="LoveAI", size_hint_y=None, height=40)
        self.scroll_view = ScrollView(
            size_hint=(1, None), size=(Window.width, Window.height * 0.8)
        )
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

        Window.bind(on_resize=self.on_window_resize)

        return self.layout

    def display_message_callback(
        self, message: str, callback: partial
    ) -> None:
        self.display_message(message)
        Clock.schedule_once(callback, 0)

    def display_message(self, message: str) -> None:
        message_label = Label(
            text=message,
            size_hint_y=None,
            markup=True,
            height=30,
            text_size=(Window.width * 0.8, None),
            font_size="20sp",
        )
        message_label.bind(
            texture_size=lambda instance, value: setattr(
                instance, "height", value[1]
            )
        )
        self.messages.add_widget(message_label)
        self.message_labels.append(message_label)
        self.scroll_view.scroll_to(message_label)

    def start_recording(self, instance) -> None:
        self.label.text = "Listening..."
        self.audio.start_recording()

    def stop_recording(self, instance) -> None:
        self.label.text = "Processing..."
        self.audio.stop_recording()
        Clock.schedule_once(self.process_audio, 0)

    def process_audio(self, *args) -> None:
        user_input = self.audio.read_from_audio()
        if (
            "goodbye" in user_input.lower().replace(" ", "")
            or user_input == ""
        ):
            self.display_message("See you later!")
            self.stop()
            return

        callback = partial(self.get_ai_response, user_input)
        self.display_message_callback(f"ME: {user_input}", callback=callback)

    def get_ai_response(self, user_input: str, *args) -> None:
        response, self.conversation_history = get_gpt_response(
            user_input, self.conversation_history
        )
        response_fragments = split_text_by_emoji(response)

        ai_message = ". ".join([msg for (msg, em) in response_fragments])

        callback = partial(self.speak_and_save, user_input, ai_message)
        self.display_message_callback(f"AI: {ai_message}", callback=callback)

    def speak_and_save(self, user_input: str, ai_message: str, *args) -> None:
        asyncio.run(self.audio.text_to_speech(ai_message))

        # sentiment = get_sentiment(user_input)
        # emotions = get_emotions(user_input)

        save_conversation(
            self.user_id,
            user_input,
            ai_message,  # sentiment, str(emotions)
        )
        self.play_audio()
        self.label.text = "Ready..."

    def play_audio(self) -> None:
        print(" play audio ".center(80, "="))
        self.sound = SoundLoader.load(self.audio.ai_audio_path)
        if self.sound:
            self.sound.play()
            Clock.schedule_interval(self.check_audio_state, 0.1)

    def check_audio_state(self, dt) -> None:
        if not self.sound.state == "play":
            self.sound.stop()
            os.remove(self.audio.ai_audio_path)
            Clock.unschedule(self.check_audio_state)

    def on_window_resize(self, window, width, height):
        self.scroll_view.size = (width, height * 0.8)
        self.update_message_text_sizes()

    def update_message_text_sizes(self):
        for label in self.message_labels:
            label.text_size = (Window.width * 0.8, None)
            label.height = label.texture_size[
                1
            ]  # Update height based on new text size


def start_ui() -> None:
    init_db()
    LoveAIApp().run()
