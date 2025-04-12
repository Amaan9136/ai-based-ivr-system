import base64
import asyncio
import random
from io import BytesIO
import edge_tts

# Proper VOICE_OPTIONS structure
VOICE_OPTIONS = {
    'en': {
        'female': ['en-IN-NeerjaNeural'],
    },
    'hi': {
        'female': ['hi-IN-SwaraNeural'],
    },
    'kn': {
        'female': ['kn-IN-SapnaNeural'],
    }
}

# Simulate session (if not using Flask's session)
session = {}

def generate_tts_audio(text, lang='en', gender='female'):
    text = text.strip()
    if not text:
        return ""

    lang = lang.lower()
    gender = gender.lower()

    if lang not in VOICE_OPTIONS:
        lang = 'en'
    if gender not in VOICE_OPTIONS[lang]:
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
        return asyncio.run(_synthesize_tts(text, selected_voice))
    except Exception as e:
        print(f"[TTS Error] {e}")
        return ""


async def _synthesize_tts(text, voice):
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+0%")
        stream = BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                stream.write(chunk["data"])
        stream.seek(0)
        return base64.b64encode(stream.read()).decode('utf-8')
    except Exception as e:
        print(f"[TTS Streaming Error] {e}")
        return ""

# 🔊 Generate and save TTS audio
msg = "Please Select a valid digit."
audio_base64 = generate_tts_audio(msg, lang='kn')

if audio_base64:
    with open("enter_valid_digit.mp3", "wb") as f:
        f.write(base64.b64decode(audio_base64))
    print("enter_valid_digit.mp3 ✅")
else:
    print("Failed to generate audio.")
