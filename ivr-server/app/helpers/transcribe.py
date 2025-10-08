import os
from transformers.pipelines import pipeline
from app.constant import MODEL_MAP
import numpy as np
import speech_recognition as sr

def transcribe_audio_bytes(audio_bytes: bytes, language: str) -> str:
    if language not in MODEL_MAP:
        raise ValueError(
            f"Unsupported language '{language}'. Choose from: {list(MODEL_MAP.keys())}"
        )

    print(f"🧠 Using model {MODEL_MAP[language]} for language {language}")

    audio_filename = "temp_audio.wav"
    with open(audio_filename, "wb") as f:
        f.write(audio_bytes)

    r = sr.Recognizer()
    with sr.AudioFile(audio_filename) as source:
        audio_data = r.record(source)

    prompt = r.recognize_google(audio_data, language=f"en-IN")

    print("[USER:]", prompt)

    os.remove(audio_filename)

    return prompt