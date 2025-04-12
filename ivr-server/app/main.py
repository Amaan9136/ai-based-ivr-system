from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.sockets import socket_router
from app.routes import call_router, service_router, option_router


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(socket_router)
app.include_router(call_router)
app.include_router(service_router)
app.include_router(option_router)
