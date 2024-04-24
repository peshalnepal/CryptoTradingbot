from nlp import NLPTokenizer
from services import NewsService, NLPService
from pipelines import Pipeline
from engine import Engine
from apis import INewsAPI
from transformers import AutoTokenizer

api = NewsService()
nlp = NLPService(
    tokenizer=NLPTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(
            "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )
    )
)

fetch = Pipeline(api.fetch, "fetch_pipeline")
tokenize = Pipeline(nlp.tokenize, "tokenize_pipeline")

engine = Engine(context={"reports_api": INewsAPI()}, pipelines=[fetch, tokenize])

engine.run_sequential()
