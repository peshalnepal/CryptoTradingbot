from http import HTTPMethod
from reactivex import Observable
from flask import Flask, request
from typing import Any
from db import Database, FirestoreDB
from db.models import OHLCVBatch
from json import loads
from adapters import AdapterProvider, OHLCVAdapter
from google.cloud.firestore import DocumentReference, CollectionReference, Query
from .endpoint import Endpoint

class MarketDataHistoricalEndpoints(Endpoint):
    __adapter__ = OHLCVAdapter()

    def __init__(
        self,
        app: Flask,
        ctx: dict[str, Any],
    ) -> None:
        self.set_ctx(ctx)
        app.route("/history", methods=[HTTPMethod.POST])(self.history)

    def history(self):
        """The forward facing history endpoint, should not be the same as the
        historical endpoint from okex. This endpoint tries to fetch ohlcv batches from cache (mem) initially
            - If the cached ohlcv's data last candles timestamp exceeds fn, invalidate cache:
                int(datetime.now().timestamp() * 1000) - (maximum number of fetchable candles * the bar frequency)
            - (ideal) Return only the datapoints necessary for the bar frequency, so we're not always sending the lowest
                frequency of stored data.
        batches from instantiated db, converts with adapter and sends to client."""

        db: FirestoreDB = self.ctx("db")

        json_data = request.json
        instId = "BTC-USDT"
        if "instId" in json_data:
            instId = json_data["instId"]

        batch_doc: DocumentReference = db.get_doc(OHLCVBatch(id=instId))
        batch_coll: CollectionReference = batch_doc.collection(f"{instId}_batches")
        batch_query: Query = batch_coll.order_by(
            field_path="latest_ts",
            direction="DESCENDING",
        )

        filtered_batches = []
        for batch_snap in batch_query.get():
            batch = batch_snap.get("")
            if batch["symbol"] == instId:
                obj = loads(batch["batch"])
                filtered_batches = [*obj, *filtered_batches]

        parsed_batches = []
        for filtered_batch in filtered_batches:
            parsed_batches.append(self.__adapter__.parse_chart(filtered_batch))

        return parsed_batches

    def __batch__(self, batch):
        return batch["batch"]
