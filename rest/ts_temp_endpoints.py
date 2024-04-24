
from .endpoint import Endpoint
from http import HTTPMethod
from typing import Any
from flask import Flask


class TimeseriesTempEndpoints(Endpoint):
    def __init__(
        self, 
        app: Flask, 
        ctx: dict[str, Any]
    ) -> None:
        self.set_ctx(ctx)
        app.route("/timeseries_predictions", methods=[HTTPMethod.POST])(self.timeseries_predictions)
            
    def timeseries_predictions(self):
        ts_predictions = self.ctx("ts_predictions")
        return ts_predictions