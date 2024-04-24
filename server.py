from typing import Any
from reactivex import Observer, create, merge, scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from flask import Flask
from security import Cors, Credentials
from rest import (
    OKEXMarketDataEndpoints,
    MarketDataHistoricalEndpoints,
    SentimentEndpoints,
    TSEndpoints,
    TimeseriesTempEndpoints,
    Endpoint
)
from db import FirestoreDB
from firebase_admin import initialize_app
from firebase_admin.credentials import Certificate
from concurrent.futures import ThreadPoolExecutor
from adapters import adapter_provider, OHLCVAdapter, SentimentAdapter
from services import (
    service_provider,
    NLPService,
    EngineService,
    MarketDataService,
    ArticleService,
    NewsService,
    SentimentService,
    TSService,
    RLService
)
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from nlp.models import NLPModel
from nlp.processing import (
    NLPPostProcessor,
    NLPTokenizer,
)
from datetime import datetime
from sockets import SocketServer
from multiprocessing.pool import Pool

import math
from time import sleep


class Server(Flask):
    __config__: Config = Config()
    __scheduler__: BackgroundScheduler = BackgroundScheduler()
    __endpoints__: list[Endpoint]

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.__scheduler__.start()

        # -- Security --
        Cors(self, self.__config__)

        # -- Firebase app and storage -- 
        app = initialize_app(Certificate(Credentials("firebase").load()))
        db = FirestoreDB(app)

        # -- Threading --
        threads = ThreadPoolExecutor(
            max_workers=int(math.floor(self.get_config().cores() / 2)),
            thread_name_prefix="CTB",
        )

        # -- Multi Processing --
        pool = Pool(processes=int(math.floor(self.get_config().cores() / 2)))

        # --- Services ---
        # Service should be added here in the global context to avoid circular imports
        # where some services require using service_provider __call__.
        adapter_provider.add(OHLCVAdapter())
        adapter_provider.add(SentimentAdapter())        
        service_provider.add(EngineService(service_provider=service_provider))
        service_provider.add(NewsService())
        service_provider.add(ArticleService())
        service_provider.add(MarketDataService())
        service_provider.add(SentimentService())
        service_provider.add(TSService())
        service_provider.add(RLService())

        service_provider.add(
            NLPService(
                model=NLPModel(
                    model=AutoModelForSequenceClassification.from_pretrained(
                        "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
                    ),
                    is_auto_model=True,
                ),
                tokenizer=NLPTokenizer(
                    tokenizer=AutoTokenizer.from_pretrained(
                        "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
                    )
                ),
                postprocessor=NLPPostProcessor(
                    chain=[
                        "set",
                    ]
                ),
            )
        )

        context = {
            "config": self.get_config(),
            "db": db,
            "pool": pool,
            "threads": threads,
            "scheduler": self.__scheduler__,
            "adapter_provider": adapter_provider,
            "service_provider": service_provider,
            "socket_server": SocketServer(
                self,
                # Intentional to avoid circular reference.
                self.get_config(),
            ),
        }

        def ts_observable(
                observer: Observer, _: scheduler.ThreadPoolScheduler,
            ):
                self.__scheduler__.add_job(
                    lambda: ts_primary(observer),
                    "interval",
                    seconds = (60 * 0.1),
                    id="BTC-USDT_ts_predictions"
                )
                return context

        def ts_primary(observer: Observer):
            result = ts_prediction_engine.run_sequential()
            print(f"-- Context Job Completed -- \nRESULT:\n", result)
            observer.on_next(result)
            
        def nlp_observable(
            observer: Observer, _: scheduler.ThreadPoolScheduler,
        ):
            self.__scheduler__.add_job(
                lambda: nlp_primary(observer),
                "interval",
                seconds = (60 * 1),
                id="BTC-USDT_nlp_sentiment"
            )
            
        def nlp_primary(
            observer: Observer
        ):
            result = nlp_sentiment_engine.run_sequential()
            print(f"-- Context Job Completed -- \nRESULT:\n", result)
            observer.on_next(result)
            
        observable_context = merge(create(ts_observable))

        ts_latest_engine = service_provider(EngineService).ts_latest_fetch(
            context={
                **context,
                "job_id": "BTC-USDT_ts_latest",
                "symbol": "BTC-USDT" 
            }
        )

        ts_prediction_engine = service_provider(EngineService).ts_prediction_engine(
            context={
                **context,
                "job_id": "BTC-USDT_ts_predictions",
                "symbol": "BTC-USDT"
            }
        )
        
        nlp_sentiment_engine = service_provider(EngineService).nlp_intermediary_engine(
            context={
                **context,
                "job_id": "BTC-USDT_nlp_sentiment",
                "symbol": "BTC-USDT"
            }
        )

        self.__endpoints__ = [
            TimeseriesTempEndpoints(self, context),
            OKEXMarketDataEndpoints(self, context),
            MarketDataHistoricalEndpoints(self, context),
            SentimentEndpoints(self, context),
            TSEndpoints(self, context)
        ]
        
        observable_context.subscribe(on_next=lambda ctx: self.set_endpoint_ctx(ctx))

        sleep(2)
        # self.__scheduler__.add_job(
        #     ts_latest_engine.run_sequential,
        #     "interval",
        #     seconds=int((60*0.02))
        # )
        
    def set_endpoint_ctx(self, ctx: dict[str, Any]):
        print("Setting endpoint context")
        for endpoint in self.__endpoints__:
            endpoint.set_ctx(ctx)

    def get_config(self) -> Config:
        return self.__config__
