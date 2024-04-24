from typing import Any
from flask import Flask
from reactivex import Observable
from http import HTTPMethod
from .endpoint import Endpoint

class TSEndpoints(Endpoint):
    def __init__(
        self, 
        app: Flask, 
        ctx: dict[str, Any]
    ) -> None:
        self.set_ctx(ctx)
        app.route("/ts_predictions", methods=[HTTPMethod.POST])(self.ts_predictions)
            
    def ts_predictions(self):
        ts_predictions = self.ctx("ts_predictions")
        return ts_predictions