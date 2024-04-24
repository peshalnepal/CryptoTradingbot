from typing import Any, TypeVar
from config import Config
from flask_socketio import SocketIO, send
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler


class SocketServer(SocketIO):     
    def __init__(
        self,
        app: Flask,
        config: Config,
        *args,
        **kwargs,
    ) -> None:
        print("[INITIALIZATION]: Socket Server")
        super().__init__(app=app, cors_allowed_origins=config.origin(), *args, **kwargs)
        self.on("message")(self.handle_message)
        self.on("connect")(self.connect)
         
    def handle_message(self, data):
        print("Recieved message", data)
        
    def connect(self):
        print("Connected", request)
        
        