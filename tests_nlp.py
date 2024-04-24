

from pipelines import Pipeline
from engine import Engine
from db import FirestoreDB
from services import NewsService, NLPService, SentimentService, ArticleService
from nlp import NLPModel, NLPTokenizer, NLPPostProcessor
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from time import sleep
from apscheduler.schedulers.background import BlockingScheduler

scheduler = BlockingScheduler()

from security import Credentials
from firebase_admin import initialize_app
from firebase_admin.credentials import Certificate
app = initialize_app(Certificate(Credentials("firebase").load()))
db = FirestoreDB(app)

sentiment_service = SentimentService()
news_service = NewsService()
article_service = ArticleService()

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

context = {"db": db, "symbol": "BTC-USDT", "scheduler": scheduler}

engine_earliest = Engine(
    context=context,
    pipelines=[
        Pipeline(sentiment_service.get_earliest_slug, "nlp_sentiment_slug_get"),
        Pipeline(sentiment_service.get_earliest, "nlp_sentiment_get"),
        Pipeline(news_service.fetch_earliest, "nlp_news_fetch"),
        # Pipeline(article_service.set_earliest_articles, "nlp_news_articles_set"),
        Pipeline(nlp_service.tokenize, "nlp_news_tokenizer"),
        Pipeline(nlp_service.predict, "nlp_news_predict"),
        Pipeline(nlp_service.postprocess, "nlp_news_postprocess"),
        Pipeline(sentiment_service.write, "nlp_sentiment_write"),
        Pipeline(sentiment_service.set_earliest_slug, "nlp_sentiment_slug_set"),
    ],
)

# nlp_intermediary = Engine(
#     context=context.copy(),
#     pipelines=[
#         Pipeline(sentiment_service.get_intermediary_slug, "nlp_sentiment_get_intermediary_slug"),
#         Pipeline(sentiment_service.get_target_slug, "nlp_sentiment_get_target_slug"),
#         Pipeline(sentiment_service.get_intermediary, "nlp_sentiment_get"),
#         Pipeline(news_service.fetch_intermediary, "nlp_news_fetch"),
#         Pipeline(nlp_service.tokenize, "nlp_news_tokenizer"),
#         Pipeline(nlp_service.predict, "nlp_news_predict"),
#         Pipeline(nlp_service.postprocess, "nlp_news_postprocess"),
#         Pipeline(sentiment_service.write, "nlp_news_write"),
#         Pipeline(sentiment_service.set_target_slug, "nlp_sentiment_set_target_slug"),
#         Pipeline(sentiment_service.update_intermediary, "nlp_sentiment_update_intermediary")
#     ],
# )

count = 0
while count < 20:
    engine_earliest.run_sequential()
    count = count+1
    sleep(10)
    print(f"\n\n[EXECUTION COUNT]: {count}\n\n")
print(f"--Finished 30 jobs--")
