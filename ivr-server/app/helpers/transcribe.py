from transformers.pipelines import pipeline
from app.constant import MODEL_MAP
import numpy as np

def transcribe_audio_bytes(audio_bytes: bytes, language: str) -> str:
    if language not in MODEL_MAP:
        raise ValueError(
            f"Unsupported language '{language}'. Choose from: {list(MODEL_MAP.keys())}"
        )

    print(f"🧠 Using model {MODEL_MAP[language]} for language {language}")

    pipe = pipeline(
        "automatic-speech-recognition",
        model=MODEL_MAP[language],
        framework="pt",
        device=0,
    )

    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
    if np.max(np.abs(audio_np)) > 1:
        audio_np = audio_np.astype(np.float32) / 32768.0
    # audio_stream = BytesIO(audio_bytes)
    print("📞 Starting transcription...")
    result = pipe(audio_np)
    print("✅ Transcription complete.")

    return result["text"]