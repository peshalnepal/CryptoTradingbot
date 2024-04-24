from security import Credentials
from db import FirestoreDB
from firebase_admin import initialize_app
from firebase_admin.credentials import Certificate
from services import (
    service_provider,
    NLPService,
    EngineService,
    MarketDataService,
    NewsService,
)
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from nlp.models import NLPModel
from nlp.processing import (
    NLPPostProcessor,
    NLPTokenizer,
)
from pipelines import Pipeline
from engine import Engine
from adapters import OHLCVAdapter
from apscheduler.schedulers.background import BlockingScheduler

# -- App Providers --
app = initialize_app(Certificate(Credentials("firebase").load()))

# -- Storage --
# Preferably Firestore storage from firebase.
db = FirestoreDB(app)

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
service_provider.add(NewsService())
service_provider.add(MarketDataService())
service_provider.add(EngineService(service_provider=service_provider))

scheduler = BlockingScheduler()


context = {
    "db": db,
    "scheduler": scheduler,
    "service_provider": service_provider,
    "adapter": OHLCVAdapter(),
    "job_id": "test_job",
}

ts_pipeline_filter = Pipeline(
    service_provider(MarketDataService).filter,
    name="ts_pipeline_filter",
)

ts_pipeline_write = Pipeline(
    service_provider(MarketDataService).write,
    name="ts_pipeline_write",
)

ts_pipeline_get_latest = Pipeline(
    service_provider(MarketDataService).get_latest,
    name="ts_pipeline_latest_get",
)

ts_pipeline_fetch_latest = Pipeline(
    service_provider(MarketDataService).fetch_latest,
    name="ts_pipeline_latest_fetch",
)


ts_pipeline_batch_latest = Pipeline(
    service_provider(MarketDataService).batch_latest,
    name="ts_pipeline_batch_latest",
)

engine = Engine(
    context=context,
    pipelines=[
        ts_pipeline_get_latest,
        ts_pipeline_fetch_latest,
        ts_pipeline_filter,
        ts_pipeline_batch_latest,
        ts_pipeline_write,
    ],
)


scheduler.add_job(
    engine.run_sequential,
    "interval",
    seconds=10,
    id=context["job_id"],
)

scheduler.start()
