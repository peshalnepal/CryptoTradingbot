from typing import Any
from .adapter import Adapter
from db.models import SentimentBatch, Sentiment, News
from nlp import NLPDataFrame
from json import loads


class SentimentAdapter(Adapter):

    def parse(self, data: dict[str, Any]) -> SentimentBatch:
        sentiment = []
        for batch in loads(data["batch"]):
            sentiment.append(Sentiment(ts=batch["ts"], prediction=batch["prediction"]))
        return SentimentBatch(
            batch=sentiment,
            id=data["id"],
            asset=data["asset"],
            earliest_ts=data["earliest_ts"],
            latest_ts=data["latest_ts"],
            is_intermediary=data["is_intermediary"]
        )

    def parse_batch(self, data: dict[str, Any]) -> list[Sentiment]:
        batch_data = loads(data["batch"])
        batches = []
        for batch in batch_data:
            timestamp = batch["ts"]
            prediction = batch["prediction"]
            # For RL adapter, helps match sentiment timestamps with ohlcv timestamps
            batches.append(Sentiment(ts=timestamp - (timestamp % 60), prediction=prediction))
        return batches

    def parse_df(self, **kwargs) -> SentimentBatch:
        data: NLPDataFrame = kwargs.get("nlp_df")
        id: str = kwargs.get("id")
        sentiment = []
        for prediction, timestamp in zip(
            data.data["Prediction"], data.data["Timestamp"]
        ):
            sentiment.append(Sentiment(ts=timestamp - (timestamp%10), prediction=prediction))
        return SentimentBatch(id=id, batch=sentiment)
    
    def parse_light(self, data: Any):
        pass 
    
    def parse_ts(self, entry: Sentiment):
        pass

