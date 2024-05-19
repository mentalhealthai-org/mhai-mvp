from __future__ import annotations

import asyncio
import html
import types

from time import sleep
from typing import Union

import edge_tts

from edge_tts import VoicesManager
from kivy.core.audio import SoundLoader


VOICE = "Microsoft Server Speech Text to Speech Voice (en-US, AvaMultilingualNeural)"
PITCH = "+5%"
RATE = "+0%"
VOLUME = "+0Hz"


def mkssml_custom(
    self,
    text: Union[str, bytes],
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> str:
    """
    Creates a SSML string from the given parameters.

    Returns:
        str: The SSML string.
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    ssml = html.unescape(text)

    # ssml = (
    #     "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
    #     f"<voice name='{voice}'><prosody pitch='{pitch}' rate='{rate}' volume='{volume}'>"
    #     f"{text}++</prosody></voice></speak>"
    # )

    print(ssml)

    return ssml


edge_tts.communicate.mkssml = types.MethodType(
    mkssml_custom, edge_tts.communicate
)


class CommunicateSSML(edge_tts.communicate.Communicate): ...


async def text_to_speech(text: str):
    ai_lang = "en-US"
    ai_gender = "female"
    ai_audio_path = "/tmp/ex_edge_tts.mp3"

    rate = "+5%"
    volume = "+0%"
    pitch = "+0Hz"

    params = {"Locale": ai_lang} if "-" in ai_lang else {"Language": ai_lang}
    voices = await VoicesManager.create()
    voice_options = voices.find(Gender=ai_gender.title(), **params)
    # voice = random.choice(voice_options)["Name"]
    voice = voice_options[0]["Name"]

    communicate = CommunicateSSML(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    await communicate.save(ai_audio_path)

    sound = SoundLoader.load(ai_audio_path)
    if sound:
        sound.play()
        while sound.state == "play":
            sleep(0.1)
        sound.stop()
        os.remove(ai_audio_path)


if __name__ == "__main__":
    text = """
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
        <voice name='Microsoft Server Speech Text to Speech Voice (en-US, AvaMultilingualNeural)'>
            <prosody pitch='-10Hz' rate='-5%' volume='+0%'>I am</prosody>
            <prosody pitch='+10Hz' rate='+5%' volume='+0%'>very sleepy</prosody>
        </voice>
    </speak>
    """
    text2 = """
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
        <voice name='Microsoft Server Speech Text to Speech Voice (en-US, AvaMultilingualNeural)'>
            <prosody pitch='+5Hz' rate='+0%' volume='+0%'>Oh, that sounds interesting!</prosody>
            <prosody pitch='+3Hz' rate='+0%' volume='+0%'>"The Legend of Zelda: Breath of the Wild" is an absolute masterpiece.</prosody>
            <prosody pitch='+0Hz' rate='+0%' volume='+0%'>Exploring Hyrule and solving puzzles can be captivating.</prosody>
        </voice>
    </speak>
    """
    text_full = """
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
        <voice name='Microsoft Server Speech Text to Speech Voice (en-US, AvaMultilingualNeural)'>
            <prosody pitch='+5Hz' rate='+0%' volume='+0%'>Oh, that sounds interesting!</prosody>
            <break time="300ms"/>
            <prosody pitch='+3Hz' rate='+0%' volume='+0%'>"The Legend of Zelda: Breath of the Wild" is an absolute masterpiece.</prosody>
            <break time="300ms"/>
            <prosody pitch='+0Hz' rate='+0%' volume='+0%'>Exploring Hyrule and solving puzzles can be captivating.</prosody>
            <break time="300ms"/>
            <prosody pitch='+2Hz' rate='+0%' volume='+0%'>Any particular adventure or quest you’re tackling?</prosody>
            <break time="500ms"/>
            <prosody pitch='+3Hz' rate='+0%' volume='+0%'>Switching gears to games you might enjoy next, how about "The Legend of Zelda: Tears of the Kingdom"?</prosody>
            <break time="300ms"/>
            <prosody pitch='+2Hz' rate='+0%' volume='+0%'>It’s another epic journey set in Hyrule with tons of new challenges and a rich story.</prosody>
            <break time="300ms"/>
            <prosody pitch='+3Hz' rate='+0%' volume='+0%'>If you loved "Breath of the Wild," you’ll probably enjoy this one too.</prosody>
            <break time="500ms"/>
            <prosody pitch='+2Hz' rate='+0%' volume='+0%'>Have you tried any other Zelda games, or is "Breath of the Wild" your first dive into the series?</prosody>
        </voice>
    </speak>
    """
    asyncio.run(text_to_speech(text2))
