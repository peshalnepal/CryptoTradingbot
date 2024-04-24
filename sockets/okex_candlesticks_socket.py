from concurrent.futures import ThreadPoolExecutor
from websocket import WebSocketApp
import json

subscribe = {
    "op": "subscribe",
    "args": [{"channel": "candle1m", "instId": "BTC-USDT"}],
}

unsubscribe = {
    "op": "unsubscribe",
    "args": [{"channel": "candle1m", "instId": "BTC-USDT"}],
}


class OKEXCandlestickSocket:
    __context__ = None
    __socket_server__ = None
    __ws__ = None

    def on_message(self, ws, message):
        parsed = json.loads(message)

        if "data" in parsed.keys():
            data = parsed["data"][0]

            self.__socket_server__.emit(
                "message",
                {
                    "time": int(data[0]) / 1000,
                    "open": float(data[1]),
                    "high": float(data[2]),
                    "low": float(data[3]),
                    "close": float(data[4]),
                },
            )
        print(message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        ws.send(json.dumps(unsubscribe))

    def on_open(self, ws: WebSocketApp):
        print("Opened connection", ws)
        ws.send(json.dumps(subscribe))

    def __init__(self) -> None:
        pass

    def __call__(self, **kwargs):
        if self.__socket_server__ is None:
            self.__socket_server__ = kwargs.get("socket_server")
        threads: ThreadPoolExecutor = kwargs.get("threads")

        ws = WebSocketApp(
            "wss://ws.okx.com:8443/ws/v5/business",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        threads.submit(ws.run_forever)
