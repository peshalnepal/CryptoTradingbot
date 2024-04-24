from typing import Any
from flask import Flask, request
from reactivex import Observable
from adapters import OkexLightweightChartsAdapter
from apis import okex
from db import Database
from db.models import Sentiment
from .market_data_endpoints import MarketDataEndpoints


class OKEXMarketDataEndpoints(MarketDataEndpoints):
    __adapter__ = ModuleNotFoundError()

    def __init__(
        self,
        app: Flask,
        context: dict[str, Any],
    ):
        if isinstance(context, dict):
            self.set_ctx(context)

        self.__adapter__ = OkexLightweightChartsAdapter()

        app.route("/symbols", methods=["GET"])(self.symbols)
        app.route("/context", methods=["GET"])(self.context)
        app.route("/predictions", methods=["GET"])(self.nlp_predictions)
        app.route("/ohlcv", methods=["POST"])(self.ohlcv)

    def symbols(self, *args, **kwargs):
        return okex.symbols()

    def ohlcv(self, *arg, **kwargs):
        """Fetches ohlcv data from provider"""
        inputs = request.get_json()
        response = okex.ohlcv(
            instId=inputs["instId"],
            bar=inputs["bar"],
            after=inputs["after"],
            limit=inputs["limit"],
        )
        return self.__adapter__.parse_list(response["data"])

    def context(self, *args, **kwargs):
        """Test function for checking if context exists"""
        return list(self.__context__["nlp_df"].data["Predictions"])

    def nlp_predictions(self, *args, **kwargs):
        db: Database = self.__context__["db"]
        return db.get_all(Sentiment())
    
    
