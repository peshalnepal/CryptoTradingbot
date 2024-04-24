import pandas as pd
from .sentiment_adapter import SentimentAdapter
from .adapter import Adapter
from db.models import OHLCV, Sentiment
import numpy as np
from copy import copy
class RLAdapter(Adapter):
    
    def __init__(self) -> None:
        super().__init__()
    
    __sentiment_adapter__ = SentimentAdapter()
    
    def parse(self, **kwargs):
        """
        Optionally parse list[OHLCV] and list[Sentiment] to state vectors for RL
        
        Expects named arguments:
            - ohlcv: 1 month of ohlcv data
            - sentiment: 1 month of sentiment data
        """
        if "ohlcv" not in kwargs:
            raise KeyError("Could not find ohlcv in kwargs.")
        if "sentiment" not in kwargs:
            raise KeyError("Could not find sentiment in kwargs.")
            
        ohlcv_data: list[OHLCV] = copy(kwargs.get("ohlcv"))
        sentiment_data: list[Sentiment] = copy(kwargs.get("sentiment"))
        state_vectors: np.ndarray = np.empty(shape=(len(ohlcv_data), 7), dtype=np.float32)
        ohlcv_index = 0
        
        rl_data = {
            "Timestamp": [],
            "Open": [],
            "High": [],
            "Low": [],
            "Close": [],
            "Volume": [],
            "Sentiment": []
        }  
        
        while ohlcv_index < len(ohlcv_data):
            
            ohlcv = ohlcv_data[ohlcv_index]
            ohlcv_ts = ohlcv["ts"]
            sentiment_vectors = []

            
            while True:
                
                if len(sentiment_data) == 0:
                    break
                
                sentiment = sentiment_data[0]
                sentiment_ts = sentiment.ts()
                
                if sentiment_ts > ohlcv_ts:
                    sentiment_vectors.append(sentiment.prediction())
                    del sentiment_data[0]
                else:
                    break
            
            if len(sentiment_vectors) > 1:
                sentiment_vector_sorted = sorted(sentiment_vectors)
                sentiment_vectors = self._determine_sentiment_vector(sentiment_vector_sorted)
            elif len(sentiment_vectors) < 1:
                sentiment_vectors.append(0)
                
            rl_data["Timestamp"].append(ohlcv["ts"])
            rl_data["Open"].append(ohlcv["o"])
            rl_data["High"].append(ohlcv["h"])
            rl_data["Low"].append(ohlcv["l"])
            rl_data["Close"].append(ohlcv["c"])
            rl_data["Volume"].append(ohlcv["v"])
            rl_data["Sentiment"].append(sentiment_vectors[0])
             
            ohlcv_index += 1
            
        return pd.DataFrame(rl_data)
        
    def _determine_sentiment_vector(self, sentiment_vector_sorted: list):
        # Get the counts of each sentiment.
        counts = [0, 0, 0]
        for vector in sentiment_vector_sorted:
            vector = int(vector)
            counts[vector] += 1
        
        # Determine the highest count for each sentiment (sentiment, count)
        highest_vals = [(0, 0)]
        for i, count in enumerate(counts):
            prev_count = highest_vals[0][1]
            if count > prev_count:
                highest_vals.clear()
                highest_vals.append((i, count))
            elif count == prev_count:
                highest_vals.append((i, count))
        
        # If 2 or more sentiments have the same count, create a set and check subsets
        if len(highest_vals) > 1:
            highest_vals = set([v[0] for v in highest_vals])
            neutral_subsets = [{0, 1}, {0, 1, 2}]
            positive_subsets = [{1, 2}]
            negative_subsets = [{0, 2}]
            
            for subset in neutral_subsets:
                if highest_vals.issubset(subset):
                    return [2]
                
            for subset in positive_subsets:
                if highest_vals.issubset(subset):
                    return [1]
                
            for subset in negative_subsets:
                if highest_vals.issubset(subset):
                    return [0]
            
            raise LookupError(f"[{self}] _determine_sentiment: unable to determine subset of sentiment_vector_u")
        
        else:
            return [highest_vals[0][0]]
            
        
    # def _determine_sentiment(self, sentiment_vector_u: set):
        
            
    #     