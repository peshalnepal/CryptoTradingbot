from typing import Any
from .adapter import Adapter
from db.models import Article, News, Page, Paginated

class ArticleAdapter(Adapter):
    
    def parse_items(self, **kwargs) -> list[Article]:
        news: News = kwargs.get("news_data")
        symbol: str = kwargs.get("symbol", "BTC-USDT")
        
        if len(news.articles) <= 0:
            print(f"[{self}] parse: Error with articles argument from newsApi. Check data")
            raise ValueError(message = f"[{self}] parse: Error with articles argument from newsApi. Check data")
        
        items = []

        for article in news.articles:
            if article.content() == "[Removed]":
                continue
            
            # We do not set the article item_index yet, it is set when the 
            # pages are separated via the modulo operator in self.parse_pages
            article.set_symbol(symbol)
            items.append(article)
            
        return items
    
    def parse_pages(self, **kwargs) -> list[Page]:
        articles: list[Article] = kwargs.get("articles", [])
        if len(articles) <= 0: 
            return
        
        items:list[Paginated] = []
        pages:list[Page] = []
        page_max_items = kwargs.get("page_max_items", 10)
        symbol = kwargs.get("symbol", "BTC-USDT")
        
        for i, article in enumerate(articles):
            article_index = i % page_max_items
            items.append(Paginated(item=article, item_index=article_index))
            
            if article_index + 1 >= page_max_items:
                # Instead of setting page index here, we need to check the result of the db cache
                # and set the proper page number in respect to what asset we're fetching information for.
                pages.append(Page(items=items, symbol=symbol, coll=f"Pages_ARTICLES"))
                items.clear()
        
        return pages