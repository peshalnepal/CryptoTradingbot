from http import HTTPMethod
from flask import Flask, request
from reactivex import Observable
from typing import Any
from json import loads
from google.cloud.firestore import DocumentReference, CollectionReference, Query
from db import FirestoreDB
from db.models import SentimentBatch
from .endpoint import Endpoint

class SentimentEndpoints(Endpoint):

    def __init__(
        self,
        app: Flask,
        ctx: dict[str, Any],
    ) -> None:
        self.set_ctx(ctx)
        app.route("/sentiment", methods=[HTTPMethod.POST])(self.sentiment)

    def sentiment(self):

        db: FirestoreDB = self.ctx("db")

        json_data = request.json
        instId = "BTC-USDT"
        if "instId" in json_data:
            instId = json_data["instId"]

        batch_doc: DocumentReference = db.get_doc(SentimentBatch(id=instId))
        batch_coll: CollectionReference = batch_doc.collection(f"{instId}_batches")
        batch_query: Query = batch_coll.order_by(
            field_path="latest_ts", direction="DESCENDING"
        ).limit(20)

        parsed_batches = []
        for snap in batch_query.get():
            batch = snap.get("")
            batch["batch"] = loads(batch["batch"])
            parsed_batches.append(batch)

        return parsed_batches
