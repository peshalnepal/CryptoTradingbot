from typing import Any
from .service_provider import ServiceProvider
from .news_service import NewsService
from .nlp_service import NLPService
from .sentiment_service import SentimentService
from .market_data_service import MarketDataService
from .article_service import ArticleService
from .ts_service import TSService
from .rl_service import RLService
from pipelines import NLPPipeline, Pipeline
from engine import Engine

# We're going to want to write a pipeline service that we use here but it wont be important for now.

class EngineService:
    __service_provider__: ServiceProvider = None

    def __init__(self, **kwargs) -> None:
        self.__service_provider__ = kwargs.get("service_provider")

    def nlp_earliest_engine(self, **kwargs) -> Engine:
        context:dict[str, Any] = kwargs.get("context", {})
        return Engine(
            context=context.copy(),
            pipelines=[
                Pipeline(self.__service_provider__(SentimentService).get_earliest_slug, "nlp_sentiment_get_slug"),
                Pipeline(self.__service_provider__(SentimentService).get_earliest, "nlp_sentiment_get"),
                Pipeline(self.__service_provider__(NewsService).fetch_earliest, "nlp_news_fetch"),
                # Pipeline(self.__service_provider__(ArticleService).set_earliest_articles, "nlp_news_articles_set"),
                Pipeline(self.__service_provider__(NLPService).tokenize, "nlp_news_tokenizer"),
                Pipeline(self.__service_provider__(NLPService).predict, "nlp_news_predict"),
                Pipeline(self.__service_provider__(NLPService).postprocess, "nlp_news_postprocess"),
                Pipeline(self.__service_provider__(SentimentService).write, "nlp_sentiment_write"),
                Pipeline(self.__service_provider__(SentimentService).set_earliest_slug, "nlp_sentiment_set_slug"),
            ],
        )

    def nlp_intermediary_engine(self, **kwargs) -> Engine:
        context:dict[str, Any] = kwargs.get("context", {})
        return Engine(
            context=context.copy(),
            pipelines=[
                Pipeline(self.__service_provider__(SentimentService).get_intermediary_slug, "nlp_sentiment_get_intermediary_slug"),
                Pipeline(self.__service_provider__(SentimentService).get_target_slug, "nlp_sentiment_get_target_slug"),
                Pipeline(self.__service_provider__(SentimentService).get_intermediary, "nlp_sentiment_get"),
                Pipeline(self.__service_provider__(NewsService).fetch_intermediary, "nlp_news_fetch"),
                Pipeline(self.__service_provider__(NLPService).tokenize, "nlp_news_tokenizer"),
                Pipeline(self.__service_provider__(NLPService).predict, "nlp_news_predict"),
                Pipeline(self.__service_provider__(NLPService).postprocess, "nlp_news_postprocess"),
                Pipeline(self.__service_provider__(SentimentService).write, "nlp_news_write"),
                Pipeline(self.__service_provider__(SentimentService).set_target_slug, "nlp_sentiment_set_target_slug"),
                Pipeline(self.__service_provider__(SentimentService).update_intermediary, "nlp_sentiment_update_intermediary")
            ]
        )

    def ts_earliest_engine(self, **kwargs) -> Engine:
        context: dict[str, Any] = kwargs.get("context", {})
        return Engine(
            context=context.copy(),
            pipelines=[
                Pipeline(self.__service_provider__(MarketDataService).get_earliest, name="ts_pipeline_earliest_get"),
                Pipeline(self.__service_provider__(MarketDataService).fetch_earliest, name="ts_pipeline_earliest_fetch"),
                Pipeline(self.__service_provider__(MarketDataService).filter, name="ts_pipeline_filter"),
                Pipeline(self.__service_provider__(MarketDataService).batch_earliest, name="ts_pipeline_batch"),
                Pipeline(self.__service_provider__(MarketDataService).write, name="ts_pipeline_write"),
            ],
        )

    def ts_latest_fetch(self, **kwargs) -> Engine:
        context: dict[str, Any] = kwargs.get("context", {})
        return Engine(
            context=context.copy(),
            pipelines=[
                Pipeline(self.__service_provider__(MarketDataService).get_latest, "ts_pipeline_latest_get"),
                Pipeline(self.__service_provider__(MarketDataService).fetch_latest, "ts_pipeline_latest_fetch"),
                Pipeline(self.__service_provider__(MarketDataService).filter, "ts_pipeline_filter"),
                Pipeline(self.__service_provider__(MarketDataService).batch_latest, "ts_pipeline_batch"),
                Pipeline(self.__service_provider__(MarketDataService).write, "ts_pipeline_write"),
            ],
        )
        
    def ts_prediction_engine(self, **kwargs) -> Engine:
        context: dict[str, Any] = kwargs.get("context", {})
        return Engine(
            context=context.copy(),
            pipelines=[
                Pipeline(self.__service_provider__(TSService).fetch, "ts_pipeline_fetch"),
                Pipeline(self.__service_provider__(TSService).preprocess, "ts_pipeline_preprocess"),
                Pipeline(self.__service_provider__(TSService).predict, "ts_pipeline_predict"),
                Pipeline(self.__service_provider__(TSService).emit_predictions, "ts_pipeline_emit_predictions")
            ]
        )

    def rl_train_engine(self, **kwargs) -> Engine:
        context: dict[str, Any] = kwargs.get("context", {})
        return Engine(
            context=context.copy(),
            pipelines=[
                Pipeline(self.__service_provider__(SentimentService).get_latest, "sentiment_get_latest"),
                Pipeline(self.__service_provider__(TSService).get_latest, "ohlcv_get_latest"),
                Pipeline(self.__service_provider__(RLService).preprocess, "rl_preprocess"),
                Pipeline(self.__service_provider__(RLService).train, "rl_train")
            ]
        )