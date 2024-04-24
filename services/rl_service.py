

# Contain functions that take information from the firestore database, and then run your RL model
from typing import Any
from db import FirestoreDB
from db.models import SentimentBatch
from adapters import RLAdapter

from rl import train_rl_model

class RLService:
    
    __adapter__ = RLAdapter()
    
    def preprocess(self, **kwargs) -> dict[str, Any]:
        
        if "ohlcv" not in kwargs:
            raise KeyError(f"[{self}].preprocess: ohlcv key not found in kwargs")
        if "sentiment" not in kwargs:
            raise KeyError(f"[{self}].preprocess: sentiment key not found in kwargs")
        
        rl_data = self.__adapter__.parse(**kwargs)
        
        return {
            **kwargs,
            "rl_data": rl_data
        }

    def train(self, **kwargs):
        
        ## INC Data
        rl_data = kwargs.get("rl_data")
        rl_shape = train_rl_model(rl_data)
        
        return {
            **kwargs,
            "rl_data": rl_data,
            "rl_shape": rl_shape,
        }