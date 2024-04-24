from .model import Model


class OHLCV(Model):

    a: str = None
    o: float = None
    h: float = None
    l: float = None
    c: float = None
    v: float = None
    ts: int = None

    def __init__(
        self,
        **kwargs,
    ) -> None:
        super().__init__(coll="Ohlcv", **kwargs)
        self.a = kwargs.get("a")
        self.o = kwargs.get("o")
        self.h = kwargs.get("h")
        self.l = kwargs.get("l")
        self.c = kwargs.get("c")
        self.v = kwargs.get("v")
        self.ts = kwargs.get("ts")

    def set(self):
        self.get_db().set(self)

    def get(self) -> "OHLCV":
        value = self.get_db().get(self)
        self = value

    def build(self) -> dict:
        return {
            "o": float(self["o"]),
            "h": float(self["h"]),
            "l": float(self["l"]),
            "c": float(self["c"]),
            "v": float(self["v"]),
            "ts": int(self["ts"]),
        }
