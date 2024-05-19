from __future__ import annotations

import os
import random

from time import sleep
from typing import Any

import pyaudio
import sounddevice as sd
import speech_recognition as sr
import wave

import edge_tts

from edge_tts import VoicesManager

SAMPLE_RATE = 44100
CHANNELS = 1
WAVE_OUTPUT_FILENAME = "/tmp/sounddevice.wav"
FORMAT = pyaudio.paInt16
CHUNK = 1024


class AudioAi:
    def __init__(self) -> None:
        self.user_audio_path = WAVE_OUTPUT_FILENAME
        self.device = None  # Initialize device as None

    def set_device(self, device_index: int):
        self.device = device_index

    def record(self) -> None:
        self.set_device(14)
        self.start_recording()
        sleep(5)
        self.stop_recording()

    def start_recording(self) -> None:
        self.recording = True
        self.frames = []
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=self.audio_callback,
            device=self.device,
        )
        self.stream.start()

    def stop_recording(self) -> None:
        self.recording = False
        self.stream.stop()
        self.stream.close()

        wf = wave.open(self.user_audio_path, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(self.frames))
        wf.close()

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            data = indata.flatten().tobytes()
            print(data)
            self.frames.append(data)


print(sd.query_devices())

audio = AudioAi()
audio.record()
