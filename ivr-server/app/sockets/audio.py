import base64
import json
from fastapi import APIRouter, WebSocket
import audioop
import wave
import numpy as np
import noisereduce as nr

socket_router = APIRouter()


@socket_router.websocket("/stream/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 Twilio connected")

    audio_frames = []

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data.get("event") == "media":
                audio_chunk = base64.b64decode(data["media"]["payload"])
                print(f"🎧 Received {len(audio_chunk)} bytes")
                audio_frames.append(audio_chunk)
                # Here you could buffer, save, or stream to STT

            elif data.get("event") == "start":
                print("🚀 Stream started")
            elif data.get("event") == "stop":
                print("🛑 Stream stopped")
                break
    except Exception as e:
        print("❌ WebSocket error:", e)
    finally:
        await websocket.close()

        raw_ulaw = b"".join(audio_frames)
        pcm_data = audioop.ulaw2lin(raw_ulaw, 2)
        audio_np = np.frombuffer(pcm_data, dtype=np.int16)
        reduced_noise = nr.reduce_noise(y=audio_np, sr=8000)
        clean_audio_bytes = reduced_noise.astype(np.int16).tobytes()

        filename = "static/recorded_audio.wav"

        with wave.open(filename, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(8000)
            wav_file.writeframes(clean_audio_bytes)

        print(f"💾 Audio saved to {filename}")
