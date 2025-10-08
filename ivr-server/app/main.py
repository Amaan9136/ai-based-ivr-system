from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import call_router, service_router, option_router
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.audio_bytes = bytes()
app.include_router(call_router)
app.include_router(service_router)
app.include_router(option_router)
