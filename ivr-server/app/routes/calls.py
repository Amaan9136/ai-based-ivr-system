from fastapi import APIRouter, Response
from twilio.twiml.voice_response import VoiceResponse, Start, Gather
from app.constant import NGROK_URL

call_router = APIRouter()


@call_router.post("/call/incoming")
def incoming_call():
    response = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action="/options/language",  # Where to POST the result (user's key press)
        method="POST",
        timeout=10
    )

    response.say("Thank you for calling SAAS. Press 1 for Kannada, 2 for Hindi and 3 for English")
    response.append(gather)

    response.say("We didn't receive any input. Goodbye.")
    response.hangup()

    return Response(content=str(response), media_type="application/xml")


@call_router.post("/stream/start")
def start_stream():
    response = VoiceResponse()
    start = Start()
    print("\n\nBefore my life was good\n\n")
    start.stream(url=f"wss://{NGROK_URL}/stream/audio")
    response.append(start)
    response.pause(length=10)  # Adjust time to collect speech

    print("\n\after my life is bad\n\n")

    response.redirect("/service")

    return Response(content=str(response), media_type="application/xml")
