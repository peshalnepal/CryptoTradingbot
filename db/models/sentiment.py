from pandas import Timestamp
from .model import Model


# An example of a Type
class Sentiment(Model):

    __ts__: int = None
    __prediction__: int = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, coll="Sentiment")

        self.__ts__ = kwargs.get("ts", None)
        self.__prediction__ = kwargs.get("prediction", None)

    def from_df(self, **kwargs):
        pass

    def set(self):
        self.get_db().set(self)

    def get(self) -> "Sentiment":
        data = self.get_db().get(self)
        self.set_ts(data["ts"])
        self.set_prediction(data["prediction"])
        return self

    def get_all(self) -> list["Sentiment"]:
        return self.get_db().get_all(self)

    def delete(self) -> "Sentiment":
        data: tuple[Timestamp, Model] = self.get_db().delete(self)
        print(f"Document {self.get_coll()}:{data[1].get_id()} deleted [{data[0]}]")
        return data[1]

    def ts(self):
        return self["__ts__"]
    
    def prediction(self):
        return self["__prediction__"]

    def set_ts(self, ts: int) -> "Sentiment":
        self["__ts__"] = ts
        return self

    def set_prediction(self, prediction: int) -> "Sentiment":
        self["__prediction__"] = prediction
        return self

    # Return a version of the model compatible with the Database.
    def build(self) -> dict:
        return {
            "ts": self["__ts__"],
            "prediction": self["__prediction__"],
        }
