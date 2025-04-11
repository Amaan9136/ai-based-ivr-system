from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from sockets import socket_router
from routes import call_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(socket_router)
app.include_router(call_router)
