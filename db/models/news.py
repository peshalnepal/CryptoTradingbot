from typing import Any
from db.models import Article


# Not a persisted model, used for NewsAPI return.
class News:
    status: str
    total_results: int
    articles: list[Article]

    def __init__(self, response: dict[str, Any]) -> None:
        self.status = response["status"]
        self.total_results = response["totalResults"]
        self.articles = [Article(**article) for article in response["articles"]]
