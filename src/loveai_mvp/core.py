import os
import random

import pyaudio
import pygame
import speech_recognition as sr
import wave

import edge_tts

from edge_tts import VoicesManager
from openai import OpenAI

from loveai_mvp.profiles import get_ai_profile, get_user_profile


# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "/tmp/output.wav"


def record_audio():
    try:
        os.remove(WAVE_OUTPUT_FILENAME)
    except Exception:
        ...

    audio = pyaudio.PyAudio()

    # Start Recording
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )
    print("recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("finished recording")

    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b"".join(frames))
    waveFile.close()


def read_from_audio(filename: str = WAVE_OUTPUT_FILENAME) -> str:
    user_profile = get_user_profile()
    user_lang = user_profile.get("language", {}).get("locale", "en-US")

    recognizer = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language=user_lang)
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


def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # wait for music to finish playing
        pygame.time.Clock().tick(10)


async def text_to_speech(text, filename="response.mp3"):
    ai_profile = get_ai_profile()

    ai_lang = ai_profile.get("language", {}).get("locale", "en-US")
    ai_gender = ai_profile.get("gender", "female")

    rate = "+0%"  # +10%
    volume = "+0%"
    pitch = "+0Hz"

    params = {"Locale": ai_lang} if "-" in ai_lang else {"Language": ai_lang}
    voices = await VoicesManager.create()
    voice_options = voices.find(Gender=ai_gender.title(), **params)
    # voice = random.choice(voice_options)["Name"]
    voice = voice_options[0]["Name"]

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    await communicate.save(filename)
