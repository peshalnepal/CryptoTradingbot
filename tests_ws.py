from websocket import WebSocketApp
import json

request_object = {
    "op": "subscribe",
    "args": [{"channel": "candle1m", "instId": "BTC-USDT"}],
}


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws: WebSocketApp):
    print("Opened connection", ws)
    ws.send(json.dumps(request_object))


if __name__ == "__main__":
    ws = WebSocketApp(
        "wss://ws.okx.com:8443/ws/v5/business",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()
