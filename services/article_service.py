from typing import Any
from db import FirestoreDB
from db.models import Article, News, Page
from adapters import ArticleAdapter

from google.cloud.firestore import DocumentSnapshot, CollectionReference, Query, FieldFilter

class ArticleService:
    
    __stubs__: dict[str, dict[str, Article]] = {"latest": {}, "earliest": {}}
    __adapter__ = ArticleAdapter()
    
    def set_earliest_articles(self, **kwargs) -> dict[str, Any]:
        if "news_data" not in kwargs or len(kwargs["news_data"].articles) <= 0:
            print(f"[{self}] set_article_pages: news_data not in kwargs, bypassing`")
            return {**kwargs}
        print(f"[{self}] set_article_pages: executing")
        db: FirestoreDB = kwargs.get("db")
        news_data: News = kwargs.get("news_data")
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        
        # Paginate articles
        paginated: list[Article] = self.__adapter__.parse_items(news_data=news_data, symbol=symbol)
        pages: list[Page] = self.__adapter__.parse_pages(paginated=paginated, symbol=symbol)
        
        # <Attempt to articles from slugs>
        
        # Get reference to collection related to symbol
        first_page = pages[0]
        coll: CollectionReference = db.get_coll(first_page.get_coll())
        
        # Make symbol and last page queries.
        symbol_query: Query = coll.where(FieldFilter("symbol", "==", first_page.symbol()))            
        last_page_query: Query = symbol_query.order_by("page_index", "ASCENDING").limit_to_last(1)
        
        # Get the last page index in the database related to the symbol query. (Move to get_slug and get function)
        page_index_db = 0
        for doc in last_page_query.get():
            page_index_db = doc.get("page_index")
            
        # Set the pages index to the enumeration index + db index + 1.
        # Set the page to the collection
        for i, page in enumerate(pages):
            page.set_page_index(page_index_db + i + 1)
            coll: CollectionReference = db.get_coll(Page(coll="Pages_ARTICLES"))
            # coll.add(page.build())
            
        return {**kwargs}
    
    def get_article_pages(self, **kwargs) -> dict[str, Any]:
        db: FirestoreDB = kwargs.get("db")
        
        coll = db.get_coll(Article())
        query = coll.order_by(field_path="published_at", direction="ASCENDING")
        
        articles = []
        for snap in query.get():
            article = snap.get(kwargs.get("article_path", ""))
            articles.append(Article(**article))
        