from .model import Model

class Article(Model):
    __source__: dict[str, str] = {}
    __author__: str
    __title__: str
    __description__: str
    __url__: str
    __url_to_image__: str
    __published_at__: str
    __content__: str
    __symbol__: str

    def __init__(self, **kwargs) -> None:
        super().__init__(coll="Articles", **kwargs)
        self.__source__ = kwargs.get("source")
        self.__author__ = kwargs.get("author")
        self.__title__ = kwargs.get("title")
        self.__description__ = kwargs.get("description")
        self.__url__ = kwargs.get("url")
        self.__url_to_image__ = kwargs.get("urlToImage", kwargs.get("url_to_image"))
        self.__published_at__ = kwargs.get("publishedAt", kwargs.get("published_at"))
        self.__content__ = kwargs.get("content")
        self.__symbol__ = kwargs.get("symbol", "BTC-USDT")
        
    def build(self) -> dict:
        return {
            "source": self.source(),
            "author": self.author(),
            "description": self.description(),
            "url": self.url(),
            "published_at": self.published_at(),
            "content": self.content(),
            "symbol": self.symbol(),
            "title": self.title(),
            "page_index": self.item_index()
        }
        
    def source(self):
        return self["__source__"]

    def set_source(self, source):
        self["__source__"] = source

    def author(self):
        return self["__author__"]

    def set_author(self, author):
        self["__author__"] = author

    def description(self):
        return self["__description__"]

    def set_description(self, description):
        self["__description__"] = description

    def url(self):
        return self["__url__"]

    def set_url(self, url):
        self["__url__"] = url

    def published_at(self):
        return self["__published_at__"]

    def set_published_at(self, published_at):
        self["__published_at__"] = published_at

    def content(self):
        return self["__content__"]

    def set_content(self, content):
        self["__content__"] = content

    def symbol(self):
        return self["__symbol__"]

    def set_symbol(self, symbol):
        self["__symbol__"] = symbol
        
    def title(self):
        return self["__title__"]
    
    def set_title(self, title):
        self["__title__"] = title

        
    