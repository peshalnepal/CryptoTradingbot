import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import Any
from db.models import OHLCV
from json import loads
from .adapter import Adapter

class TSAdapter(Adapter):
    
    
    def parse_batch(self, **kwargs) -> Any:
        data=kwargs.get("ohlcv_batches",[])
        final_data={
            "Open":[],
            "High":[],
            "Low":[],
            "Close":[],
            "Volume":[],
            "Timestamp":[]
            
        }
        if len(data) <= 0:
            return
        for batch in data:
            open_=float(batch[1])
            high_=float(batch[2])
            low_=float(batch[3])
            close_=float(batch[4])
            volume=float(batch[5])
            timestamp=int(batch[0])
            final_data["Open"].append(open_)
            final_data["High"].append(high_)
            final_data["Low"].append(low_)
            final_data["Close"].append(close_)
            final_data["Volume"].append(volume)
            final_data["Timestamp"].append(timestamp)
        return final_data

    def parse_light(self, data: dict[str, Any]) -> list[OHLCV]:
        if "symbol" not in data:
            raise KeyError("Invalid Firebase Document: OHLCVBatch, no symbol field")
        if "batch" not in data:
            raise KeyError("Invalid Firebase Document: OHLCVBatch, no batch field")

        parsed = []
        for ohlcv in loads(data["batch"]):
            parsed.append(OHLCV(
                ts=int(int(ohlcv[0]) / 1000),
                o=float(ohlcv[1]),
                h=float(ohlcv[2]),
                l=float(ohlcv[3]),
                c=float(ohlcv[4]),
                v=float(ohlcv[5])
            ))
            
        return parsed
    
    def parse_df(self, **kwargs) -> pd.DataFrame:
        
        df: pd.DataFrame = kwargs.get("ts_df")
        n: int = kwargs.get("n", 14)
        d_period: int = kwargs.get("d_period", 3)
        rm_cols: list[str] = kwargs.get("remove_cols", ["Volume", "Timestamp", "%K"])
        
        # Calculate the difference between consecutive closing prices
        delta = df['Close'].diff()

        # Separate gains (up) and losses (down)
        up = delta.where(delta > 0, 0)
        down = -delta.where(delta < 0, 0)

        # Calculate the EMA of gains and losses
        ema_up = up.ewm(span=n).mean()
        ema_down = down.ewm(span=n).mean()

        # Calculate the relative strength (RS)
        rs = ema_up / ema_down

        # Calculate the ERI
        eri = 100 - (100 / (1 + rs))

        # Add the ERI column to the DataFrame
        df.loc[:,'ERI'] = eri
        df.loc[:,'%K'] = (df["Close"] - df["Low"].rolling(n).min()) / (df["High"].rolling(n).max() - df["Low"].rolling(n).min()) * 100

        # Calculate %D
        df.loc[:,'%D'] = df['%K'].rolling(d_period).mean()
        df = df.dropna()
        scaler = MinMaxScaler(feature_range=(0, 100))  # Set the desired range
        df.loc[:,'%D'] = scaler.fit_transform(df[['%D']])
        scaler = MinMaxScaler(feature_range=(0, 100))  # Set the desired range
        df.loc[:,'ERI'] = scaler.fit_transform(df[['ERI']])
        df.loc[:,"High"]=df["High"].pct_change()
        df.loc[:,"Open"]=df["Open"].pct_change()
        df.loc[:,"Low"]=df["Low"].pct_change()
        df.loc[:,"Close"]=df["Close"].pct_change()
        df=df.drop(columns=rm_cols, axis=1)
        
        return df