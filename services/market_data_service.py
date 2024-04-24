from db import FirestoreDB
from apis import okex
from adapters import OHLCVAdapter
from json import loads
from uuid import uuid4
from datetime import datetime

from db.models import OHLCV, OHLCVBatch
from google.cloud.firestore import CollectionReference, DocumentReference


class MarketDataService:
    __adapter__: OHLCVAdapter = OHLCVAdapter()
    __batch_slugs__: dict[str, dict[str, OHLCVBatch]] = {"earliest": {}, "latest": {}}

    def __init__(self, **kwargs):
        pass

    def get_earliest(self, **kwargs):
        print(f"[{self}] Running get_earliest function")
        
        db: FirestoreDB = kwargs.get("db")
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        
        if symbol in self.__batch_slugs__["earliest"]:
            return {
                **kwargs,
                "ohlcv_batches": [self.__batch_slugs__["earliest"][symbol]],
            }
            
        batch_doc: DocumentReference = db.get_doc(OHLCVBatch(id=symbol))
        batch_coll: CollectionReference = batch_doc.collection(f"{symbol}_batches")
        
        aggregate = batch_coll.count().get()[0]
        if aggregate[0].value >= 50:
            print(
                f"[{self}] \n - get_earliest signaling engine stop. \n - {symbol}_batchs already contains 50 batches."
            )
            return {**kwargs, "engine_terminate": True}
        batch_query = batch_coll.order_by(
            field_path="earliest_ts",
            direction=kwargs.get("sort_by_direction", "DESCENDING"),
        ).limit_to_last(1)
        ohlcv_batches = []
        for snap in batch_query.get():
            ohlcv_batches.append(snap.get(kwargs.get("ohlcv_batch_path", "")))
        return {
            **kwargs,
            "ohlcv_batches": ohlcv_batches,
        }

    def fetch_earliest(self, **kwargs):
        ohlcv_batches: list = kwargs.get("ohlcv_batches", [])
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        print(f"[{self}] Running fetch_earliest function, symbol={symbol}")
        if len(ohlcv_batches) == 0:
            ohlcv_result = okex.ohlcv(instId=symbol)
            ohlcv_data = ohlcv_result["data"]
            ohlcv_objs = [self.__adapter__.parse(data) for data in ohlcv_data]
            return {**kwargs, "ohlcv_objs": ohlcv_objs}
        else:
            earliest_batch: OHLCVBatch = ohlcv_batches[0]
            ohlcv_result = okex.history(
                instId=symbol, after=earliest_batch["earliest_ts"]
            )
            ohlcv_data = ohlcv_result["data"]
            ohlcv_objs = [self.__adapter__.parse(data) for data in ohlcv_data]
            ohlcv_temp = (
                loads(earliest_batch["batch"])
                if isinstance(earliest_batch["batch"], str)
                else earliest_batch["batch"]
            )
            return {
                **kwargs,
                "ohlcv_objs": ohlcv_objs,
                "ohlcv_temp": self.__adapter__.parse_batch(ohlcv_temp),
            }

    def get_latest(self, **kwargs):
        db: FirestoreDB = kwargs.get("db")
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        print(f"[{self}] Running get_latest function symbol={symbol}")
        if symbol in self.__batch_slugs__["latest"]:
            return {**kwargs, "ohlcv_batches": [self.__batch_slugs__["latest"][symbol]]}
        batch_doc: DocumentReference = db.get_doc(OHLCVBatch(id=symbol))
        batch_coll: CollectionReference = batch_doc.collection(f"{symbol}_batches")
        batch_query = batch_coll.order_by(
            field_path="latest_ts",
            direction=kwargs.get("sort_by_direction", "ASCENDING"),
        ).limit_to_last(1)
        ohlcv_batches = []
        for snap in batch_query.get():
            data = snap.get(kwargs.get("ohlcv_batch_path", ""))
            ohlcv_batches.append(data)
        return {
            **kwargs,
            "ohlcv_batches": ohlcv_batches,
        }

    def fetch_latest(self, **kwargs):
        ohlcv_batches: list = kwargs.get("ohlcv_batches", [])
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        print(f"[{self}] Running fetch_latest function symbol={symbol}")
        if len(ohlcv_batches) == 0:
            ohlcv_result = okex.ohlcv(instId=symbol)
            ohlcv_data = ohlcv_result["data"]
            ohlcv_objs = [self.__adapter__.parse(data) for data in ohlcv_data]
            return {**kwargs, "ohlcv_objs": ohlcv_objs}
        else:
            latest_batch: OHLCVBatch = ohlcv_batches[0]
            latest_ts = int(latest_batch["latest_ts"])
            now = int(datetime.now().timestamp() * 1000)
            diff_milli = now - latest_ts
            ts_limit = 1000 * 60 * 100
            if diff_milli < ts_limit:
                print(
                    f"[{self}] \n- fetch_latest signaling engine stop. \n- Data is up to date enough."
                )
                return {**kwargs, "engine_stop": True}
            ohlcv_result = okex.history(
                instId=symbol,
                after=latest_ts + ts_limit,
                before=latest_ts,
            )
            ohlcv_data = ohlcv_result["data"]
            ohlcv_objs = [self.__adapter__.parse(data) for data in ohlcv_data]
            ohlcv_temp = (
                loads(latest_batch["batch"])
                if isinstance(latest_batch["batch"], str)
                else latest_batch["batch"]
            )
            return {
                **kwargs,
                "ohlcv_objs": ohlcv_objs,
                "ohlcv_temp": self.__adapter__.parse_batch(ohlcv_temp),
            }

    def filter(self, **kwargs):
        print(f"[{self}] Running filter function")
        ohlcv_temp: list[OHLCV] = kwargs.get("ohlcv_temp", [])
        ohlcv_objs: list[OHLCV] = kwargs.get("ohlcv_objs", [])
        timestamps = set()
        ohlcv: list[OHLCV] = []
        for obj in ohlcv_temp + ohlcv_objs:
            ts = obj["ts"]
            if ts not in timestamps:
                timestamps.add(ts)
                ohlcv.append(obj)
        return {**kwargs, "ohlcv": ohlcv}

    def batch_latest(self, **kwargs):
        print(f"[{self}] Running batch_latest function")
        symbol = kwargs.get("symbol", "BTC-USDT")
        batch = OHLCVBatch(**{**kwargs, "adapter": self.__adapter__})
        if symbol not in self.__batch_slugs__["latest"]:
            self.__batch_slugs__["latest"] = {}
        self.__batch_slugs__["latest"][symbol] = batch
        return {
            **kwargs,
            "ohlcv_batch": batch,
        }

    def batch_earliest(self, **kwargs):
        print(f"[{self}] Running batch_earliest function")
        symbol = kwargs.get("symbol", "BTC-USDT")
        batch = OHLCVBatch(**{**kwargs, "adapter": self.__adapter__})
        if symbol not in self.__batch_slugs__["earliest"]:
            self.__batch_slugs__["earliest"] = {}
        self.__batch_slugs__["earliest"][symbol] = batch
        return {
            **kwargs,
            "ohlcv_batch": batch,
        }

    def write(self, **kwargs):
        print(f"[{self}] Running store function")
        db: FirestoreDB = kwargs.get("db")
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        batch: OHLCVBatch = kwargs.get("ohlcv_batch")
        batch_doc: DocumentReference = db.get_doc(OHLCVBatch(id=symbol))
        batch_coll: CollectionReference = batch_doc.collection(f"{symbol}_batches")
        batch_coll.add(batch.build(), str(uuid4()))
        return kwargs
