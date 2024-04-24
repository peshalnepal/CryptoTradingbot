from enum import Enum
from typing import Any
from apis import okex
from time import time
from json import loads
from adapters import OHLCVAdapter, TSAdapter
from db import FirestoreDB
from db.models import OHLCV, OHLCVBatch, Sentiment
from ts.torchtsmixer import TSMixer
from sockets import SocketServer

import pandas as pd
import numpy as np
import torch
import os

from google.cloud.firestore import DocumentReference, CollectionReference, Query, FieldFilter

class TSMode(Enum):
    EVAL="eval"

class TSService:
    
    __model_state_dir__: str = f"{os.getcwd()}/ts/model.pt"
    __model__: TSMixer = None
    __ohlcv_adapter__ = OHLCVAdapter()
    __adapter__ = TSAdapter()
    __device__ = "cuda:0" if torch.cuda.is_available() else "cpu"
    
    def __init__(self, **kwargs) -> None:
        self.__model__ = kwargs.get("model", self.create_ts_model(**kwargs))
        pass
    
    # fetch latest 100 candles
    def fetch(self, **kwargs) -> dict[str, Any]:
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        limit = kwargs.get("limit", "100")
        after = int(time()) * 1000
        try:
            ohlcv_result = okex.ohlcv(instId=symbol, limit=limit, after=after)
            ohlcv_data = ohlcv_result["data"]
            ohlcv_objs = self.__adapter__.parse_batch(ohlcv_batches=ohlcv_data)
            return {
                **kwargs,
                "ohlcv_objs": ohlcv_objs
            }
        except Exception as e:
            print(e)
            return {**kwargs,"engine_terminate": True}
        
    def get_latest(self, **kwargs) -> dict[str, Any]:
        db: FirestoreDB = kwargs.get("db")
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        print(f"[{self}] Running get_latest function symbol={symbol}")
        batch_doc: DocumentReference = db.get_doc(OHLCVBatch(id=symbol))
        batch_coll: CollectionReference = batch_doc.collection(f"{symbol}_batches")
        
        batch_query = self._get_latest_query(batch_coll, **kwargs)
        batch_query = self._add_limit(batch_query, **kwargs)
        
        ohlcv = []
        for snap in batch_query.get():
            data = snap.get(kwargs.get("ohlcv_path", ""))
            ohlcv = [*ohlcv, *self.__adapter__.parse_light(data)]
            
        return {
            **kwargs,
            "ohlcv": ohlcv
        }
        
    def _get_latest_query(self, coll: CollectionReference, **kwargs) -> Query:
        if "sentiment" in kwargs:
            sentiment_list: list[Sentiment] = kwargs.get("sentiment")
            sentiment = sentiment_list[0]
            return coll.where(filter=FieldFilter("latest_ts", "<", sentiment.ts()*1000))    \
                .order_by("latest_ts", "DESCENDING")                                        \
            
        return coll.order_by(
            field_path="latest_ts",
            direction=kwargs.get("sort_by_direction", "DESCENDING")
        )
    
    def preprocess(self, **kwargs) -> dict[str, Any]:
        if "ohlcv_objs" not in kwargs:
            return {
                **kwargs,
                "engine_terminate": True
            }
            
        ohlcv_objs: list[OHLCV] = kwargs.get("ohlcv_objs")
        df = self.__adapter__.parse_df(ts_df=pd.DataFrame(ohlcv_objs))  \
                .tail(70)                                               \
                .reset_index(drop=True)
        
        df_array = np.array(df, dtype=np.float32)
        X = torch.from_numpy(df_array)  \
            .unsqueeze(0)               \
            .to(device=self.__device__)
        
        return {
            **kwargs,
            "ohlcv_x": X
        }
    
    def predict(self, **kwargs) -> dict[str, Any]:
        if "ohlcv_objs" not in kwargs:
            return {
                **kwargs,
                "engine_terminate": True
            }
        if "ohlcv_x" not in kwargs:
            return {
                **kwargs,
                "engine_terminate": True
            }
        
        X = kwargs.get("ohlcv_x")
        objs = kwargs.get("ohlcv_objs")
        
        self.set_model_mode(TSMode.EVAL)
        predictions = self.__model__(X)
        
        res = []
        latest_ts = objs["Timestamp"][0]
        columns = [objs["Open"][0], objs["High"][0], objs["Low"][0], objs["Close"][0]]
        
        for tensor in predictions[0]:
            formatted = [latest_ts]
    
            percentages = tensor.tolist()
            for i, (percentage, col_val) in enumerate(zip(percentages[:4], columns)):
                next_val = col_val + (col_val*(percentage/100))
                formatted.append(next_val)
                columns[i] = next_val
                
            latest_ts += (60 * 1000) 
            res.append(formatted)
            
        return {
            **kwargs,
            "ts_predictions": res
        }
        
    def emit_predictions(self, **kwargs) -> dict[str, Any]:
        if "ts_predictions" not in kwargs:
            return {
                **kwargs,
                "engine_terminate": True
            }
            
        ts_predictions = kwargs.get("ts_predictions")
        socket_server: SocketServer = kwargs.get("socket_server")
        
        print("Emitting ts_predictions")
        socket_server.emit("ts_predictions", ts_predictions)
        return kwargs
        
    def device(self):
        return self.__device__
    
    def model_state_dir(self) -> str:
        return self.__model_state_dir__
    
    def model(self) -> TSMixer:
        return self.__model__
        
    def create_ts_model(self, **kwargs):
        sequence_length: int = kwargs.get("sequence_length", 70)
        prediction_length: int = kwargs.get("prediction_length", 10)
        input_channels: int = kwargs.get("input_channels", 6)
        output_channels: int = kwargs.get("output_channels", 6)
        model = TSMixer(sequence_length, prediction_length, input_channels, output_channels)
        return model.to(device=self.device())
    
    def set_model_mode(self, mode: TSMode):
        if mode == TSMode.EVAL:
            state_dict=torch.load(self.model_state_dir())
            self.__model__.load_state_dict(state_dict)
            self.__model__.eval()

    def _add_limit(self, query: Query, **kwargs) -> Query:
        if "ohlcv_limit" not in kwargs:
            return query
        return query.limit(kwargs.get("ohlcv_limit"))    
        
    