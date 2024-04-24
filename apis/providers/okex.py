from http import HTTPMethod
from https import RequestHandler
from datetime import datetime

from apis import CryptoAPI, Provider


class OKEX(Provider, CryptoAPI):
    __base_url__ = "https://www.okx.com"
    __api_key__ = "-1"
    __request_handler__ = ModuleNotFoundError()

    __time_map__ = {"1m": 60}

    def __init__(self) -> None:
        super().__init__()
        self.__request_handler__ = RequestHandler(self)

    def base_url(self) -> str:
        return self.__base_url__

    def api_key(self) -> str:
        return self.__api_key__

    def symbols(
        self,
        instType: str = ["SWAP", "SPOT", "MARGIN", "FUTURES", "OPTION"][0],
        uly: str | None = None,
        instFamily: str | None = None,
        instId: str | None = None,
    ):
        return self.__request_handler__(
            endpoint="/api/v5/public/instruments",
            method=HTTPMethod.GET,
            params={
                "instType": instType,
                "uly": uly,
                "instFamily": instFamily,
                "instId": instId,
            },
        )

    def history(
        self,
        instId: str = "BTC-USDT",
        after: str | None = f"{int(datetime.now().timestamp())*1000}",
        before: str = None,
        bar: str | None = "1m",
        limit: str | None = "300",
    ):
        if before is not None:
            return self.__request_handler__(
                endpoint="/api/v5/market/history-candles",
                method=HTTPMethod.GET,
                params={
                    "instId": instId,
                    "bar": bar,
                    "before": before,
                    "after": after,
                    "limit": limit,
                },
            )
        return self.__request_handler__(
            endpoint="/api/v5/market/history-candles",
            method=HTTPMethod.GET,
            params={
                "instId": instId,
                "bar": bar,
                "after": after,
                "limit": limit,
            },
        )

    def ohlcv(
        self,
        instId: str = "BTC-USDT",
        bar: str = "1m",
        after: int = int(datetime.now().timestamp() * 1000),
        before: int = None,
        limit: str = "300",
    ):
        """Only accepts after parameter, as we either want most recent data
        or the data after the requested timestamp.

        Args:
            instId (str, optional): _description_. Defaults to "BTC-USDT".
            bar (str, optional): _description_. Defaults to "1m".
            after (int, optional): _description_. Defaults to int(datetime.now().timestamp() * 1000).
            limit (str, optional): _description_. Defaults to "300".

        Returns:
            dict[str, Any]: a JSON string representing the candles
        """
        if isinstance(before, int):
            return self.__request_handler__(
                endpoint="/api/v5/market/candles",
                method=HTTPMethod.GET,
                params={
                    "instId": instId,
                    "bar": bar,
                    "after": str(after),
                    "before": str(before),
                    "limit": limit,
                },
            )
        return self.__request_handler__(
            endpoint="/api/v5/market/candles",
            method=HTTPMethod.GET,
            params={
                "instId": instId,
                "bar": bar,
                "after": str(after),
                "limit": limit,
            },
        )


okex = OKEX()
