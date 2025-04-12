import base64
import json
from fastapi import APIRouter, WebSocket
import audioop
import numpy as np
import noisereduce as nr
from twilio.twiml.voice_response import VoiceResponse

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
        print(
            f"🔇 Closing WebSocket connection. Total audio frames received: {len(audio_frames)}"
        )

        raw_ulaw = b"".join(audio_frames)
        print(f"🎧 Combined {len(raw_ulaw)} bytes of raw audio from frames.")

        pcm_data = audioop.ulaw2lin(raw_ulaw, 2)
        print("🔄 Converted raw ulaw to PCM format.")

        audio_np = np.frombuffer(pcm_data, dtype=np.int16)
        print(f"📊 Converted PCM data to numpy array, shape: {audio_np.shape}")

        print("🔊 Reducing noise from the audio...")
        reduced_noise = nr.reduce_noise(y=audio_np, sr=8000)
        print("🎧 Noise reduction applied.")

        clean_audio_bytes = reduced_noise.astype(np.int16).tobytes()
        print(f"📥 Cleaned audio ready. Size: {len(clean_audio_bytes)} bytes.")

        websocket.app.state.audio_bytes = clean_audio_bytes

        print("🔌 Closing WebSocket connection...")
        await websocket.close()
        print("🔌 WebSocket connection closed")