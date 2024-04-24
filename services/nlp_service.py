from db import Database
from db.models import Sentiment
from nlp import NLPModel, NLPTokenizer, NLPPostProcessor, NLPDataFrame
from typing import Any


class NLPService:

    __model__: NLPModel = None
    __tokenizer__: NLPTokenizer = None
    __postprocessor__: NLPPostProcessor = None

    def __init__(self, model=None, tokenizer=None, postprocessor=None):
        if isinstance(model, NLPModel):
            self.__model__ = model

        if isinstance(tokenizer, NLPTokenizer):
            self.__tokenizer__ = tokenizer

        if isinstance(postprocessor, NLPPostProcessor):
            self.__postprocessor__ = postprocessor

    def tokenize(self, **kwargs) -> dict[str, Any]:
        tensors = None
        try:
            tensors = self.__tokenizer__(**kwargs)
            return {**kwargs, "tensors": tensors}
        except Exception as e:
            print(e)
            return {**kwargs, "engine_stop": True}

    def predict(self, **kwargs) -> dict[str, Any]:
        predictions = None
        try:
            predictions = self.__model__(**kwargs)
            return {**kwargs, "predictions": predictions}
        except Exception as e:
            print(e)
            return {**kwargs, "engine_stop": True}

    def postprocess(self, **kwargs) -> dict[str, Any]:
        try:
            self.__postprocessor__(**kwargs)
            del kwargs["predictions"]
            return kwargs
        except Exception as e:
            print(e)
            return {**kwargs, "engine_stop": True}

    def store_predictions(self, **kwargs) -> dict[str, Any]:
        nlp_df: NLPDataFrame = kwargs.get("nlp_df")
        db: Database = kwargs.get("db")
        for _, row in nlp_df.data.iterrows():
            db.set(
                Sentiment(
                    **{
                        "ts": row["Timestamp"],
                        "asset": "bitcoin",
                        "prediction": row["Prediction"],
                    }
                )
            )

        return kwargs
