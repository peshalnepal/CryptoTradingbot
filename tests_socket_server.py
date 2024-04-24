from flask import Flask
from sockets import SocketServer
from engine import Engine
from pipelines import Pipeline
from rest import TestEndpoints
from services import TSService
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler

config = Config()
service = TSService()

class TestSocketServer(Flask):
    __config__: Config = Config()
    __socket_server__: SocketServer = None
    __scheduler__ = BackgroundScheduler() 
    
    def __init__(self, *args, **kwargs):
        super(TestSocketServer, self).__init__(*args, **kwargs)
        self.__socket_server__ = SocketServer(
                self,
                # Intentional to avoid circular reference.
                self.__config__,
            )
        
        context = {
            "symbol": "BTC-USDT",
            "socket_server": self.__socket_server__
        }
        
        engine = Engine(
            context=context.copy(),
            pipelines=[
                Pipeline(service.fetch, "ts_fetch"),
                Pipeline(service.preprocess, "ts_preprocess"),
                Pipeline(service.predict, "ts_predict"),
                Pipeline(service.emit_predictions, "ts_emit")
            ]
        )
        
        self.__scheduler__.add_job(
            engine.run_sequential,
            "interval",
            seconds=30
        )
        
        self.__scheduler__.start()
        
        TestEndpoints(self)        
        
    def init_socket_server(self):
        server = self.__socket_server__
        server.on("message")(lambda x: print(x))
        server.emit("message_response", {"response": "Noice"})
        
tests_socket_server = TestSocketServer(__name__)