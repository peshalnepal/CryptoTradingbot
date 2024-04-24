from security import Credentials
from firebase_admin import initialize_app
from firebase_admin.credentials import Certificate

from pipelines import Pipeline
from engine import Engine
from db import FirestoreDB
from services import NewsService, NLPService, SentimentService
from nlp import NLPModel, NLPTokenizer, NLPPostProcessor
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep

app = initialize_app(Certificate(Credentials("firebase").load()))
db = FirestoreDB(app)

sentiment_service = SentimentService()
news_service = NewsService()
nlp_service = NLPService(
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

context = {"db": db, "symbol": "BTC-USDT"}

engine = Engine(
    context=context,
    pipelines=[
        Pipeline(sentiment_service.get_earliest, "nlp_sentiment_get"),
        Pipeline(news_service.fetch_earliest, "nlp_news_get"),
        Pipeline(nlp_service.tokenize, "nlp_news_tokenizer"),
        Pipeline(nlp_service.predict, "nlp_news_predict"),
        Pipeline(nlp_service.postprocess, "nlp_news_postprocess"),
        Pipeline(sentiment_service.write, "nlp_sentiment_write"),
    ],
)

engine.run_sequential()
sleep(30)
engine.run_sequential()
sleep(30)
engine.run_sequential()
