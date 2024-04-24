
from http import HTTPMethod
from flask import Flask, request
from reactivex import Observable
from typing import Any
from json import loads
from google.cloud.firestore import CollectionReference, Query, FieldFilter
from db import FirestoreDB
from db.models import Article
from .endpoint import Endpoint

class ArticlesEndpoints(Endpoint):
    
    def __init__(
        self,
        app: Flask,
        ctx: dict[str, Any],
        ) -> None:
        self.set_ctx(ctx)
        app.route("/articles", methods=[HTTPMethod.POST])(self.articles)

    def articles(self):
        db: FirestoreDB = self.ctx("db")
        
        json_data = request.json
        instId = "BTC-USDT"
        if "instId" in json_data:
            instId = json_data["instId"]
            
        coll: CollectionReference = db.get_coll(Article(FieldFilter("symbol", "==", instId)))
        query: Query = coll.order_by("published_at", "ASCENDING")
        query: Query = query.limit(10)
        
        pass
