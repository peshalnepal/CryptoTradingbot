from adapters import GoogleNewsAdapter
from apis import Provider, INewsAPI
from db.models import News
from gnews import GNews


class GoogleNews(Provider, INewsAPI):

    __client__: GNews = None
    __adapter__ = GoogleNewsAdapter()
    __key_map__: dict[str, str] = {
        "BTC-USDT": "bitcoin",
        "ETH-USDT": "ethereum",
        "LTC-USDT": "litecoin",
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def news(self, **kwargs) -> News:
        key = self.__key_map__[kwargs.get("symbol", "BTC-USDT")]
        self.__client__ = GNews(
            "en",
            start_date=kwargs.get("from_param", None),
            end_date=kwargs.get("to", None),
        )
        response = self.__client__.get_news(key)
        news = self.__adapter__.parse(response)
        print(news)
