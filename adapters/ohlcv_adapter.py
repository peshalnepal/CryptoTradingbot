from typing import Any
from .adapter import Adapter
from db.models import OHLCV


class OHLCVAdapter(Adapter):

    def parse_chart(self, batch: list) -> dict[str, Any]:
        return {
            "time": int(batch[0]) / 1000,
            "open": float(batch[1]),
            "high": float(batch[2]),
            "low": float(batch[3]),
            "close": float(batch[4]),
        }

    def parse(self, data: list, symbol: str = "BTC-USDT") -> OHLCV:
        return OHLCV(
            a=symbol,
            o=data[1],
            h=data[2],
            l=data[3],
            c=data[4],
            v=data[5],
            ts=data[0],
        )

    def parse_batch(self, data: list[list]) -> list[OHLCV]:
        objs = []
        for ohlcv in data:
            objs.append(self.parse(ohlcv))
        return objs

    def parse_light(self, data: list[OHLCV]) -> list:
        objs: list = []
        for obj in data:
            objs.append(
                [
                    obj["ts"],
                    obj["o"],
                    obj["h"],
                    obj["l"],
                    obj["c"],
                    obj["v"],
                    obj["a"],
                ]
            )
        objs.reverse()
        return objs
