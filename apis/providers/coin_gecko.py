from http import HTTPMethod
from apis import CryptoAPI, Provider
from security import Credentials
from https import RequestHandler


# Prayge
class CoinGecko(Provider, CryptoAPI):
    __api_key = Credentials("cg").load()
    __base_url = "https://api.coingecko.com/api/v3"
    __request_handler = None

    def __init__(self) -> None:
        super().__init__()
        self.__request_handler = RequestHandler(self)

    def api_key(self):
        return self.__api_key

    def base_url(self):
        return self.__base_url

    def set_handler(self, handler: RequestHandler) -> None:
        self.__request_handler = handler

    def symbols(self, include_platform=False):
        return self.__request_handler(
            endpoint="/coins/list",
            method=HTTPMethod.GET,
            params={
                "include_platform": include_platform,
            },
        )

    def history(
        self,
        id: str,
        vs_currency: str = "usd",
        days: str = "1",
        precision: str = "2",
    ):
        return self.__request_handler(
            endpoint=f"/coins/{id}/ohlc",
            method=HTTPMethod.GET,
            params={
                "vs_currency": vs_currency,
                "days": days,
                "precision": precision,
            },
        )


coin_gecko = CoinGecko()
