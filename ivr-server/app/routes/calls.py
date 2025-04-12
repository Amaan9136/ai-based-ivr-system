import os
import wave
from fastapi import APIRouter, Request, Response
import requests
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.constant import LANG_MAP
from app.helpers import transcribe_audio_bytes
import numpy as np
import audioop
import noisereduce as nr
from requests.auth import HTTPBasicAuth
import time

call_router = APIRouter()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


@call_router.post("/call/incoming")
def incoming_call():
    response = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action="/options/language",  # Where to POST the result (user's key press)
        method="POST",
        timeout=10,
    )

    response.say(
        "Thank you for calling SAAS. Press 1 for Kannada, 2 for Hindi and 3 for English"
    )
    response.append(gather)

    response.say("We didn't receive any input. Goodbye.")
    response.hangup()

    return Response(content=str(response), media_type="application/xml")


@call_router.post("/stream/start")
async def start_stream(
    request: Request,
):
    form_data = await request.form()
    print(form_data.keys())
    url = form_data.get("RecordingUrl")
    wav_url = f"{url}.wav"
    print(wav_url)

    time.sleep(2)

    response = requests.get(
        wav_url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID or "", TWILIO_AUTH_TOKEN or "")
    )
    print(f"\n\n\nRESPONSE CODE: {response.status_code}\n\n\n")
    recording_bytes = response.content  # The raw bytes of the audio file

    output_filename = "raw_audio.wav"

    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 2 bytes = 16 bits
        wf.setframerate(8000)  # Sample rate in Hz
        wf.writeframes(recording_bytes)

    pcm_data = audioop.ulaw2lin(recording_bytes, 2)
    print("🔄 Converted raw ulaw to PCM format.")

    audio_np = np.frombuffer(pcm_data, dtype=np.int16)
    print(f"📊 Converted PCM data to numpy array, shape: {audio_np.shape}")

    print("🔊 Reducing noise from the audio...")
    reduced_noise = nr.reduce_noise(y=audio_np, sr=8000)
    print("🎧 Noise reduction applied.")

    clean_audio_bytes = reduced_noise.astype(np.int16).tobytes()
    print(f"📥 Cleaned audio ready. Size: {len(clean_audio_bytes)} bytes.")

    output_filename = "clean_audio.wav"

    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 2 bytes = 16 bits
        wf.setframerate(8000)  # Sample rate in Hz
        wf.writeframes(recording_bytes)

    language = request.app.state.language

    prompt = transcribe_audio_bytes(recording_bytes, LANG_MAP[language])

    request.app.state.prompt = prompt

    response = VoiceResponse()
    response.redirect("/service")

    return Response(content=str(response), media_type="application/xml")
