from typing import Any
from apis import NewsAPI
from adapters import NewsApiAdapter
from db.models import SentimentBatch
from datetime import datetime
from time import time

class NewsService:
    """uses https://newsapi.org/docs,
    due to subscription restrictions, we need to account for the 24 hour document delay, and the 1 month
    document history limitation.

    Returns:
        NewsService: A service that provides functions to pipelines.
    """

    __api__ = NewsAPI()
    __adapter__ = NewsApiAdapter()
    __running_count__: int = 10
    
    def __init__(self) -> None:
        pass

    def under_count(self) -> bool:
        return self.__running_count__ < 100

    def fetch_earliest(self, **kwargs) -> dict[str, Any]:
        print(f"[{self}] Running get function")
        sentiment_batches: list[SentimentBatch] = kwargs.get("sentiment_batches", [])
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        
        three_days = 60 * 60 * 24 * 3
        now = int(time())

        if (len(sentiment_batches)) == 0:
            try:
                to_date = datetime.fromtimestamp(now)
                from_date = datetime.fromtimestamp(now - three_days)
                news_data = self.__api__.news(
                    **kwargs,
                    to=to_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    from_param=from_date.strftime("%Y-%m-%dT%H:%M:%S"),
                )
                self.__running_count__ += 1
                print(f"[NEWS SERVICE]: Running count - {self.__running_count__}")
                return {**kwargs, "nlp_df": self.__adapter__.parse(news_data), "news_data": news_data}
            except Exception as e:
                print(f"[{self}] EXCEPTION: \n\n", e)
                return {**kwargs, "engine_terminate": True}

        else:
            earliest_ts = sentiment_batches[0].earliest_ts()
            slug_age = int(time()) - earliest_ts
            if slug_age > (60 * 60 * 24 * 30):
                print(
                    f"[{self}] News slug a month or older detected \nAge (seconds) - {slug_age}"
                )
                return {**kwargs, "engine_terminate": True}

            try:
                to_date = datetime.fromtimestamp(earliest_ts)
                from_date = datetime.fromtimestamp(earliest_ts - three_days)
                news_data = self.__api__.news(
                    asset=symbol,
                    to=to_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    from_param=from_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    page=1,
                )
                self.__running_count__ += 1
                print(f"[NEWS SERVICE]: Running count - {self.__running_count__}")
                
                return {**kwargs, "nlp_df": self.__adapter__.parse(news_data), "news_data": news_data}
            except Exception as e:
                print(f"[{self}] EXCEPTION: \n\n", e)
                return {**kwargs, "engine_terminate": True}


    def fetch_intermediary(self, **kwargs) -> dict[str, Any]:
        sentiment_batches: list[SentimentBatch] = kwargs.get("sentiment_batches", [])
        sentiment_targets: list[SentimentBatch] = kwargs.get("sentiment_targets", [])
        symbol = kwargs.get("symbol", "BTC-USDT")
        
        from_date = None
        to_date = None
        three_days = 60 * 60 * 24 * 3
        now = int(time())

        if len(sentiment_batches) == 0:

            from_date = from_date if from_date != None else datetime.fromtimestamp(now - three_days)
            to_date = to_date if to_date != None else datetime.fromtimestamp(now)

            try:
                news_data = self.__api__.news(
                    asset=symbol,
                    from_param=from_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    to=to_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    page=1,
                )
                self.__running_count__ += 1
                print(f"[NEWS SERVICE]: Running count - {self.__running_count__}")
                
                nlp_df = self.__adapter__.parse(news_data)
                return {**kwargs, "nlp_df": nlp_df, "is_intermediary": True, "news_data": news_data}
            
            except Exception as e:
                print(f"[{self}] EXCEPTION: \n\n", e)
                return {**kwargs, "engine_stop": True}
            
        # Check if the target exists, and if the slugs earliest_ts overlaps with targets latest_ts
        if len(sentiment_targets) > 0:
            target = sentiment_targets[0]
            batch = sentiment_batches[0]
            
            if target.latest_ts() > batch.earliest_ts():
                batch.remove_before(target.latest_ts())
            
            # If no sentiment obj's remain after removing before target.latest_ts, no articles exist between intermediary and target.
            if len(batch.batch()) <= 0:
                print(f"[{self}] fetch_intermediary: Failed to fetch any new articles between intermediary and target. Terminating Job.")
                return { **kwargs, "engine_terminate": True }
            
            from_date = datetime.fromtimestamp(target.latest_ts())
            to_date = datetime.fromtimestamp(batch.earliest_ts())
                
        # Get news up to the earliest_ts of the latest batch_slug
        # Get news from db that's timestamp is earlier than earliest_ts
        try:
            from_date = from_date if from_date != None else datetime.fromtimestamp(now - three_days)
            to_date = to_date if to_date != None else datetime.fromtimestamp(now)
            
            news_data = self.__api__.news(
                asset=symbol,
                from_param=from_date.strftime("%Y-%m-%dT%H:%M:%S"),
                to=to_date.strftime("%Y-%m-%dT%H:%M:%S"),
                page=1,
            )
            self.__running_count__ += 1
            print(f"[NEWS SERVICE]: Running count - {self.__running_count__}")
                
            nlp_df = self.__adapter__.parse(news_data)
            return {**kwargs, "nlp_df": nlp_df, "is_intermediary": True, "news_data": news_data}
            
        except Exception as e:
            print(f"[{self}] EXCEPTION: \n\n", e)
            return {**kwargs, "engine_terminate": True}

    def __get_latest_date__(self) -> int:
        pass
