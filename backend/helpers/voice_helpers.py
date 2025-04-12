import asyncio
import edge_tts
import base64
from io import BytesIO
import random
from flask import request, jsonify, session
from deep_translator import GoogleTranslator

VOICE_OPTIONS = {
    'en': {
        'male': ['en-IN-PrabhatNeural'],
        'female': ['en-IN-NeerjaNeural']
    },
    'hi': {
        'male': ['hi-IN-MukeshNeural', 'hi-IN-RaviNeural'],
        'female': ['hi-IN-SwaraNeural']
    },
    'kn': {
        'male': ['kn-IN-GaganNeural'],
        'female': ['kn-IN-SapnaNeural']
    }
}


def translate_text_to_english(text: str, language: str = 'english') -> str:
    language = language.lower()
    if language == 'english':
        return text
    try:
        return GoogleTranslator(source=language, target='english').translate(text)
    except Exception as e:
        print(f"[Translation Error] {e}")
        return text


def translate_text_to_session_language(text: str, session_lang: str) -> str:
    session_lang = session_lang.lower()
    if session_lang == "english":
        return text
    try:
        return GoogleTranslator(source='english', target=session_lang).translate(text)
    except Exception as e:
        print(f"[Translation Error] {e}")
        return text


def generate_tts_audio(text, lang='en', gender='female'):
    text = text.strip()
    if not text:
        print("[TTS Error] Empty text provided.")
        return None

    lang = lang.lower()
    gender = gender.lower()

    if lang not in VOICE_OPTIONS:
        print(f"[TTS Warning] Unsupported language '{lang}', falling back to 'en'")
        lang = 'en'
    if gender not in VOICE_OPTIONS[lang]:
        print(f"[TTS Warning] Unsupported gender '{gender}' for language '{lang}', defaulting to 'female'")
        gender = 'female'

    session_key = f'bot_voice_{lang}'
    session_gender_key = f'bot_voice_gender_{lang}'

    if session.get(session_key) and session.get(session_gender_key) == gender:
        selected_voice = session[session_key]
    else:
        selected_voice = random.choice(VOICE_OPTIONS[lang][gender])
        session[session_key] = selected_voice
        session[session_gender_key] = gender

    print(f"Generating TTS for: '{text}' using voice: {selected_voice}")

    try:
        audio_base64 = asyncio.run(_synthesize_tts(text, selected_voice))
        if not audio_base64:
            print("[TTS Error] Audio synthesis returned empty result.")
            return None
        return audio_base64
    except Exception as e:
        print(f"[TTS Error] {e}")
        return None


async def _synthesize_tts(text, voice):
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+20%")
        stream = BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                stream.write(chunk["data"])
        stream.seek(0)
        return base64.b64encode(stream.read()).decode('utf-8')
    except Exception as e:
        print(f"[TTS Streaming Error] {e}")
        return None
