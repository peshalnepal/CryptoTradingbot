from typing import Any
from adapters import SentimentAdapter
from google.cloud.firestore import DocumentReference, CollectionReference, FieldFilter, Query
from db import FirestoreDB
from db.models import SentimentBatch
from uuid import uuid4
from json import dumps
from time import time


class SentimentService:

    __adapter__ = SentimentAdapter()
    __batch_slugs__: dict[str, dict[str, SentimentBatch]] = {
        "earliest": {},
        "intermediary": {},
        "target": {}
    }

    def write(self, **kwargs) -> dict[str, Any]:
        db: FirestoreDB = kwargs.get("db")
        nlp_df = kwargs.get("nlp_df")
        symbol = kwargs.get("symbol", "BTC-USDT")
        is_intermediary = kwargs.get("is_intermediary", False)
        id = str(uuid4())

        sentiment_batch = self.__adapter__.parse_df(nlp_df=nlp_df, id=id)
        sentiment_batch.set_asset(symbol)
        sentiment_batch.set_is_intermediary(is_intermediary)
        sentiment_data = sentiment_batch.build()
        sentiment_data["batch"] = dumps(sentiment_data["batch"])
        
        doc: DocumentReference = db.get_doc(SentimentBatch(id=symbol))
        coll: CollectionReference = doc.collection(f"{symbol}_batches")
        coll.add(sentiment_data, id)
        
        print(f"[{self}] write: Wrote Sentiment(id={id}) to firestore")
        return {**kwargs, "sentiment_batches": [sentiment_batch]}

    def set_target_slug(self, **kwargs):
        targets = kwargs.get("sentiment_targets", [])
        symbol = kwargs.get("symbol", "BTC-USDT")
        sentiment_target = self.__set_slug__("target", sentiment_batches=targets, symbol=symbol)
        return {**kwargs, "sentiment_targets": [sentiment_target]}

    def set_earliest_slug(self, **kwargs):
        sentiment_batch = self.__set_slug__("earliest", **kwargs)
        return {**kwargs, "sentiment_batches": [sentiment_batch]}

    def get_earliest_slug(self, **kwargs):       
        slug = self.__get_slug__("earliest", **kwargs)

        if slug != None:
            slug_age = int(time()) - slug.earliest_ts()

            if slug_age > (60 * 60 * 24 * 30):
                return {**kwargs, "engine_terminate": True}

            return {**kwargs, "sentiment_batches": [slug]}
        else:
            return {**kwargs, "sentiment_batches": []}

    def set_intermediary_slug(self, **kwargs):
        sentiment_batch = self.__set_slug__("intermediary", **kwargs)
        return {**kwargs, "sentiment_batches": [sentiment_batch]}

    def get_intermediary_slug(self, **kwargs):
        slug = self.__get_slug__("intermediary", **kwargs)

        if slug != None:
            return {**kwargs, "sentiment_batches": [slug]}
        else:
            return {**kwargs, "sentiment_batches": []}
        
    def get_target_slug(self, **kwargs):
        slug = self.__get_slug__("target", **kwargs)
        
        if slug != None:
            return {**kwargs, "sentiment_targets": [slug]}
        else:
            return {**kwargs, "sentiment_targets": []}


    def get_latest(self, **kwargs):
        print(f"[{self}] Running get latest function")
        db: FirestoreDB = kwargs.get("db")
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        
        batch_doc: DocumentReference = db.get_doc(SentimentBatch(id=symbol))
        batch_coll: CollectionReference = batch_doc.collection(f"{symbol}_batches")
        
        batch_query: Query = batch_coll.order_by(
                field_path="latest_ts",
                direction=kwargs.get("sort_by_direction", "DESCENDING")
            )
        batch_query = self._add_limit(batch_query, **kwargs)
        
        sentiment = []
        for snap in batch_query.get():
            data = snap.get(kwargs.get("sentiment_path", ""))
            sentiment = [*sentiment, *self.__adapter__.parse_batch(data)]
            
        return {
            **kwargs,
            "sentiment": sentiment
        }

    def get_earliest(self, **kwargs):
        print(f"[{self}] Running get earliest function")
        db: FirestoreDB = kwargs.get("db")
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        sentiment_batches = kwargs.get("sentiment_batches", [])

        if len(sentiment_batches) > 0:
            print(f"[{self}] Sentiment batches located, not querying database.")
            return {**kwargs, "sentiment_batches": sentiment_batches}

        # Real
        batch_doc: DocumentReference = db.get_doc(SentimentBatch(id=symbol))
        batch_coll: CollectionReference = batch_doc.collection(f"{symbol}_batches")

        aggregate_query = batch_coll.count().get()[0]
        if aggregate_query[0].value >= 50:
            print(
                f"[{self}] \n get_earliest signaling engine to stop. \n - {symbol}_batches already contains 50 batches."
            )
            return {
                **kwargs,
                "engine_terminate": True,
            }

        batch_query = batch_coll.order_by(
            field_path="earliest_ts",
            direction=kwargs.get("sort_by_direction", "DESCENDING"),
        ).limit_to_last(1)

        sentiment_batches = []
        for snap in batch_query.get():
            data = snap.get(kwargs.get("sentiment_path", ""))
            data["id"] = snap.id
            sentiment_batches.append(self.__adapter__.parse(data))

        return {**kwargs, "sentiment_batches": sentiment_batches}

    def get_intermediary(self, **kwargs):
        db: FirestoreDB = kwargs.get("db")
        symbol: str = kwargs.get("symbol", "BTC-USDT")

        sentiment_batches: list[SentimentBatch] = kwargs.get("sentiment_batches", [])
        sentiment_targets: list[SentimentBatch] = kwargs.get("sentiment_targets", [])
        
        batch_doc: DocumentReference = db.get_doc(SentimentBatch(id=symbol))
        batch_coll: CollectionReference = batch_doc.collection(f"{symbol}_batches")

        # Check if sentiment_batches contains any objs
        if len(sentiment_batches) == 0:
            print(f"[{self}] New intermediary fetch job detected, assigning target.")
            target_query = batch_coll.order_by(
                field_path="latest_ts", 
                direction=kwargs.get("sort_by_direction", "DESCENDING")
            ).limit(1)
            
            for snap in target_query.get():
                batch = snap.get(kwargs.get("sentiment_target_path", ""))
                batch["id"] = snap.id
                batch = self.__adapter__.parse(batch)
                self.set_target_slug(sentiment_targets=[batch], symbol=symbol)
                sentiment_targets.append(batch)
                
            return {**kwargs, "sentiment_batches": sentiment_batches, "sentiment_targets": sentiment_targets}
        
        # If a slug is found, it is the intermediary. Return it, and the target sentiment to stop fetching towards.
        intermediary_query = batch_coll.where(filter=FieldFilter("is_intermediary", "==", True))
        for snap in intermediary_query.get():
            batch = snap.get(kwargs.get("sentiment_batch_path", ""))
            batch["id"] = snap.id
            batch = self.__adapter__.parse(batch)
            sentiment_batches = [batch]
            
        return {**kwargs, "sentiment_batches": sentiment_batches, "sentiment_targets": sentiment_targets}
    
    def update_intermediary(self, **kwargs) -> dict[str, Any]:
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        db: FirestoreDB = kwargs.get("db")
        new_slug: list[SentimentBatch] = kwargs.get("sentiment_batches")
        
        if not self.__has_slug__("intermediary"):
            print(f"[{self}] update_intermediary: has_slug() == false, no previous intermediary slug.")
            self.set_intermediary_slug(sentiment_batches=new_slug, symbol=symbol)
            return kwargs
    
        # get prev slug (exists) and update prev slug in database, set is_intermediary to False
        prev_slug: SentimentBatch = self.__get_slug__("intermediary", symbol=symbol)
        db.update(prev_slug, field="is_intermediary", value=False, symbol=symbol)
        
        # update memory slug to new sentiment batch
        if len(new_slug) > 0:
            self.set_intermediary_slug(sentiment_batches=new_slug, symbol=symbol)
            
        return kwargs
    
    def _add_limit(self, query: Query, **kwargs) -> Query:
        if "sentiment_limit" not in kwargs:
            return query
        return query.limit(kwargs.get("sentiment_limit", 2))
    
    def __set_slug__(self, slug_key, **kwargs):
        batches = kwargs.get("sentiment_batches")
        batch = batches[0]
        symbol = kwargs.get("symbol", "BTC-USDT")
        self.__batch_slugs__[slug_key][symbol] = batch
        return batch
    
    def __get_slug__(self, slug_key, **kwargs):
        symbol = kwargs.get("symbol", "BTC-USDT")
        if self.__has_slug__(slug_key, symbol=symbol):
            return self.__batch_slugs__[slug_key][symbol]
    
    def __has_slug__(self, slug_key, **kwargs):
        symbol = kwargs.get("symbol", "BTC-USDT")
        if symbol in self.__batch_slugs__[slug_key]:
            return self.__batch_slugs__[slug_key][symbol] != None
        else:
            return False
    
        
