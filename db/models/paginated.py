from .model import Model

class Paginated:
    
    __item_index__: int = -1
    __item__: Model = None
    
    def __init__(self, **kwargs) -> None:
        self["__item_index__"] = kwargs.get("page_index", 0)
        self["__item__"] = kwargs.get("item", None)
    
    def item(self) -> Model:
        return
    
    def set_item(self, item):
        self["__item__"]= item
    
    def item_index(self) -> int:
        return self["__item_index__"]
    
    def set_item_index(self, page_index):
        self["__item_index__"] = page_index