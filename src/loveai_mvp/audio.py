from __future__ import annotations

import os
import random

from typing import Any

import pyaudio
import sounddevice as sd
import speech_recognition as sr
import wave

import edge_tts

from edge_tts import VoicesManager
from openai import OpenAI

from loveai_mvp.utils.text import markdown_to_plain_text


# Audio configuration
SAMPLE_RATE = 44100
CHANNELS = 1
WAVE_OUTPUT_FILENAME = "/tmp/output.wav"
FORMAT = pyaudio.paInt16
CHUNK = 1024


class AudioAi:
    def __init__(
        self,
        user_profile: dict[str, Any],
        ai_profile: dict[str, Any],
        user_audio_path: str = WAVE_OUTPUT_FILENAME,
        ai_audio_path: str = WAVE_OUTPUT_FILENAME,
    ) -> None:
        self.user_profile = user_profile
        self.ai_profile = ai_profile
        self.user_audio_path = user_audio_path
        self.ai_audio_path = ai_audio_path

        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = None
        self.frames = []

    def read_from_audio(self) -> str:
        user_lang = self.user_profile.get("language", {}).get(
            "locale", "en-US"
        )

        recognizer = sr.Recognizer()

        with sr.AudioFile(self.user_audio_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(
                    audio_data, language=user_lang
                )
                print(f"Recognized Text: {text}")
                return text
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return ""
            except sr.RequestError as e:
                print(
                    f"Could not request results from Google Speech Recognition service; {e}"
                )
                return ""

    async def text_to_speech(self, text: str):
        ai_lang = self.ai_profile.get("language", {}).get("locale", "en-US")
        ai_gender = self.ai_profile.get("gender", "female")

        rate = "+5%"
        volume = "+0%"
        pitch = "+0Hz"

        params = (
            {"Locale": ai_lang} if "-" in ai_lang else {"Language": ai_lang}
        )
        voices = await VoicesManager.create()
        voice_options = voices.find(Gender=ai_gender.title(), **params)
        # voice = random.choice(voice_options)["Name"]
        voice = voice_options[0]["Name"]

        communicate = edge_tts.Communicate(
            text=markdown_to_plain_text(text),
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
        await communicate.save(self.ai_audio_path)

    def start_recording(self) -> None:
        self.frames = []
        self.stream = self.pyaudio_instance.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.audio_callback,
        )
        self.stream.start_stream()

    def stop_recording(self) -> None:
        self.stream.stop_stream()
        self.stream.close()

        wf = wave.open(self.user_audio_path, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.pyaudio_instance.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(self.frames))
        wf.close()

    def audio_callback(self, in_data, frame_count, time_info, status):
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)
