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

    request.app.state.wav_url = wav_url

    response = VoiceResponse()
    response.redirect("/service")

    return Response(content=str(response), media_type="application/xml")
