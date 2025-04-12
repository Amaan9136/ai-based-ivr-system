from fastapi import APIRouter, Request, Response
import requests
from twilio.twiml.voice_response import VoiceResponse, Gather

from app.constant import FLASK_URL


option_router = APIRouter(prefix="/options")


@option_router.post("/language")
async def handle_language_selection(request: Request):
    form = await request.form()

    response = VoiceResponse()

    digit = form.get("Digits")

    if digit not in ["1", "2", "3"]:
        response.say("Invalid Input. Goodbye.")
        return Response(content=str(response), media_type="application/xml")

    lang_mapper = {"1": "kannada", "2": "hindi", "3": "english"}

    language = lang_mapper[digit]

    request.app.state.language = language

    url = f"{FLASK_URL}/language/set-language"
    data = {"language": language}

    requests.post(url, json=data)

    gather = Gather(
        num_digits=1,
        action="/options/requirements",  # Where to POST the result (user's key press)
        method="POST",
        timeout=10,
    )

    audio = str(request.base_url) + f"static/{language}.mp3"

    response.play(audio)

    response.append(gather)

    response.say("We didn't receive any input. Goodbye.")
    response.hangup()

    return Response(content=str(response), media_type="application/xml")


@option_router.post("/requirements")
async def handle_requirements_selection(request: Request):
    form = await request.form()
    digit = form.get("Digits")

    response = VoiceResponse()

    if digit not in ["1", "2", "3", "4"]:
        response.say("Invalid Input. Goodbye.")
        return Response(content=str(response), media_type="application/xml")

    route_mapper = {
        "1": "/nearby-schools/ask",
        "2": "/ncert-questions/ask",
        "3": "/scholarships/ask",
        "4": "",
    }

    request.app.state.endpoint = route_mapper[digit]

    language = request.app.state.language

    response.play(str(request.base_url) + f'static/query_share_{language}.mp3')

    response.record(
        action="/stream/start",
        method="POST",
        max_length=10,
        timeout=10,
        play_beep=True,
    )

    return Response(content=str(response), media_type="application/xml")
