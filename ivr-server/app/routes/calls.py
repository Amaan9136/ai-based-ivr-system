from fastapi import APIRouter, Response
from twilio.twiml.voice_response import VoiceResponse, Start


call_router = APIRouter()


@call_router.post("/call/incoming")
def incoming_call():
    response = VoiceResponse()
    response.say("Welcome to the SAAS. Start speaking after the beep.")
    response.play("https://033a-103-213-211-149.ngrok-free.app/static/beep.mp3")
    response.redirect("/stream/start")

    return Response(content=str(response), media_type="application/xml")


@call_router.post("/stream/start")
def start_stream():
    response = VoiceResponse()
    start = Start()
    start.stream(url="wss://033a-103-213-211-149.ngrok-free.app/audio-stream")
    response.append(start)
    response.pause(length=10)  # Adjust time to collect speech
    return Response(content=str(response), media_type="application/xml")
