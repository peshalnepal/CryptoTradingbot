from typing import Any
from .adapter import Adapter
from db.models import News, Article
from nlp import NLPDataFrame
from pandas import DataFrame
from datetime import datetime


class NewsApiAdapter(Adapter):

    __required_args = ["title", "description", "publishedAt"]
    __date_format__ = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self) -> None:
        super().__init__()

    def parse(self, news: News) -> NLPDataFrame:
        """Parse news to NLPDataFrame

        Args:
            news (News): a news object from NewsAPI

        Returns:
            NLPDataFrame: NLPDataFrame for making predictions
        """
        objs = []
        for i, article in enumerate(news.articles):
            if article.content() == "[Removed]":
                continue
            try:
                objs.append(
                    {
                        "Text": f"{article.title()} | {article.description()} | {article.content()}",
                        "Timestamp": self.__timestamp(article),
                    }
                )
                    
            except Exception as e:
                print(f"Error with article #{i+1}", e)

        return NLPDataFrame(data=DataFrame(objs))

    def __is_valid_article__(self, article: dict):
        try:
            if isinstance(article, dict):
                # Perform further validation here.

                for arg in self.__required_args:
                    if arg not in article:
                        raise ValueError(
                            f"Article does not contain required property: [{arg}]"
                        )

                return True
        except ValueError as e:
            print(e)

    def __timestamp(self, article: Article):
        date_obj = datetime.strptime(article.published_at(), self.__date_format__)
        timestamp = int(date_obj.timestamp())
        return timestamp // 10 ** (len(str(timestamp)) - 10)
