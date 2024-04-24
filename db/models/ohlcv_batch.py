from db.models import Model, OHLCV
from json import dumps


class OHLCVBatch(Model):

    batch: list
    symbol: str
    earliest_ts: int
    latest_ts: int

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, coll="Batch_OHLCV")

        self["batch"] = kwargs.get("batch")
        self["symbol"] = kwargs.get("symbol", "BTC-USDT")
        self["earliest_ts"] = int(kwargs.get("earliest_ts", 0))
        self["latest_ts"] = int(kwargs.get("latest_ts", 0))

        if "ohlcv_objs" in kwargs:
            self.parse_model(**kwargs)

    def build(self) -> dict:
        return {
            "batch": dumps(self["batch"]),
            "earliest_ts": int(self["earliest_ts"]),
            "latest_ts": int(self["latest_ts"]),
            "symbol": self["symbol"],
        }

    def parse_model(self, **kwargs):
        adapter = kwargs.get("adapter")
        data: list[OHLCV] = kwargs.get("ohlcv_objs")
        self.earliest_ts = data[len(data) - 1]["ts"]
        self.latest_ts = data[0]["ts"]
        self.batch = adapter.parse_light(data)
        self.symbol = kwargs.get("symbol", "BTC-USDT")
