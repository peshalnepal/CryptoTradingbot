from db.models import Model
from .sentiment import Sentiment


class SentimentBatch(Model):

    __batch__: list[Sentiment] = []
    __asset__: str = None
    __is_intermediary__: bool = False
    __earliest_ts__: int = None
    __latest_ts__: int = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, coll="Batch_SENTIMENT")
        self.__batch__ = kwargs.get("batch", [])
        self.__asset__ = kwargs.get("asset")
        self.__is_intermediary__ = kwargs.get("is_intermediary")
        self.set_timestamps(**kwargs)

    def set_timestamps(self, **kwargs):
        batches = [sentiment.build() for sentiment in self.batch()]
        earliest_ts = kwargs.get("earliest_ts", None)
        latest_ts = kwargs.get("latest_ts", None)
        
        if len(batches) > 0:
            earliest_ts = batches[len(batches) - 1]["ts"]
            latest_ts = batches[0]["ts"]
 
        self.__earliest_ts__ = earliest_ts
        self.__latest_ts__ = latest_ts

    def set_batch(self, batch):
        self["__batch__"] = batch

    def set_asset(self, asset):
        self["__asset__"] = asset
        
    def set_is_intermediary(self, is_intermediary):
        self["__is_intermediary__"] = is_intermediary

    def earliest_ts(self):
        return self["__earliest_ts__"]

    def latest_ts(self):
        return self["__latest_ts__"]
    
    def batch(self) -> list[Sentiment]:
        return self["__batch__"]

    def build(self):
        batches = [sentiment.build() for sentiment in self.batch()]
        return {
            "batch": batches,
            "asset": self["__asset__"],
            "is_intermediary": self["__is_intermediary__"],
            "earliest_ts": self["__earliest_ts__"],
            "latest_ts": self["__latest_ts__"],
        }
    
    def remove_before(self, ts):
        self.set_batch([sentiment for sentiment in self.batch() if sentiment.ts() > ts])
        self.set_timestamps()
        return self.batch()
        