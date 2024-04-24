from apis import INewsAPI, Provider
from newsapi import NewsApiClient
from security import Credentials
from db.models import News
from adapters import NewsApiAdapter

class NewsAPI(Provider, INewsAPI):

    __client__: NewsApiClient
    __adapter__: NewsApiAdapter
    __instId_query_map__: dict[str, str] = {
        "BTC-USDT": "bitcoin OR btc OR btc-usdt OR btc-usd",
        "ETH-USDT": "ethereum OR eth OR eth-usdt OR eth-usd",
        "LTC-USDT": "litecoin OR ltc OR ltc-usdt OR ltc-usd",
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__client__ = NewsApiClient(Credentials("newsapi").load())
        self.__adapter__ = NewsApiAdapter()

    def news(self, **kwargs) -> News:
        response = self.__client__.get_everything(
            q=self.__instId_query_map__[kwargs.get("asset", "BTC-USDT")],
            from_param=kwargs.get("from_param", None),
            to=kwargs.get("to", None),
            language=kwargs.get("lang", "en"),
            sort_by=kwargs.get("sort", "publishedAt"),
            page=kwargs.get("page", 1),
        )
        if response["status"] == "ok":
            return News(response)
        else:
            print(f"Reponse status {response['status']}", response)
