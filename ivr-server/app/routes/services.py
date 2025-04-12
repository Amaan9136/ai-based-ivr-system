from fastapi import APIRouter, Request, Response
import requests
from app.constant import FLASK_URL
import base64
from twilio.twiml.voice_response import VoiceResponse

service_router = APIRouter()


@service_router.post("/service")
def get_service(request: Request):
    print("🔍 Retrieving prompt and endpoint values from app state...")
    wav_url = request.app.state.wav_url
    endpoint = request.app.state.endpoint

    url = f"{FLASK_URL}{endpoint}"
    data = {"audio_url": wav_url}
    print(f"🌐 Sending POST request to Flask service: {url} with data: {data}")

    res = requests.post(
        url, json=data, headers={"Content-Type": "application/json"}
    ).json()
    print("✅ Successfully received response from Flask service.", res)

    audio_b64 = res.get("audio")
    if not audio_b64:
        print("❌ No audio data returned from Flask service.")
        return Response(content="No audio returned from the service.", status_code=500)

    print("🎶 Base64 audio received. Decoding and saving to file...")

    audio_path = "static/tts.mp3"
    with open(audio_path, "wb") as f:
        f.write(base64.b64decode(audio_b64))

    print(f"💾 Audio saved to {audio_path}.")

    print("📞 Creating Twilio VoiceResponse...")

    response = VoiceResponse()
    response.play(f"{request.base_url}static/tts.mp3")

    print("🎤 Waiting for speech input from the user...")
    response.say("Please continue your chat!")
    response.record(
        action="/stream/start",
        method="POST",
        max_length=10,
        timeout=10,
        play_beep=True,
    )

    response.say("We did not hear anything. Goodbye.")

    return Response(content=str(response), media_type="application/xml")
