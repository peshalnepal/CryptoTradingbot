from .paginated import Paginated
from .model import Model

class Page(Model):
    
    __items__: list[Paginated] = []
    __symbol__: str = "BTC-USDT"
    __page_index__: int = -1
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_items(kwargs.get("item", []))
        self.set_symbol(kwargs.get("symbol", "BTC-USDT"))
        self.set_page_index(kwargs.get("page_index", 0))
        
    def __getitem__(self, index: int) -> Paginated:
        return self.item(index)
    
    def __iter__(self):
        return iter(self.items())
    
    def __contains__(self, item: Paginated) -> bool:
        # Implement logic to check if item is in database
        return item in self.items()
        
    def append_item(self, item: Paginated):
        if len(self.items()) == 0:
            self.items().append(item)
        elif isinstance(item, self.item(0)):
            self.items().append(item)
        else:
            print(f"[{self}] Page {item}, was not the same type as the elements in __items__")
            raise ValueError(message=f"Page {item}, was not the same type as the elements in __items__")
            
    def insert_item(self, item: Paginated, index: int = 0):
        if len(self.items()) == 0:
            self.items().insert(index, item)
        elif isinstance(item, self.item(0)):
            self.items().insert(index, item)
        else:
            print(f"[{self}] Page {item}, was not the same type as the elements in __items__")
            raise ValueError(message=f"Page {item}, was not the same type as the elements in __items__")
            
    def update_item(self, index: int, item: Paginated):
        if len(self.items()) == 0:
            print(f"[{self}] update_item: No pages exist")
            raise IndexError(message=f"[{self}] update_item: No pages exist")
        if index < len(self.items()) and isinstance(item, self.item(index)):
            self.set_item(item)
            
    def build(self) -> dict:
        return {
            "items": [item.build() for item in self.items()],
            "page_index": self["__page_index__"],
            "symbol": self["symbol"]
        }
        
    def item(self, index: int) -> Paginated:
        if index > len(self.items()):
            print(f"[{self}] page: Does not contain specified index = {index}")
            raise IndexError(message="Invalid page index, pages object does not contain specified page.")
        return self["__items__"][index]

    def set_item(self, index: int, item: Paginated):
        if index > len(self.items()):
            print(f"[{self}] page: Does not contain specified index = {index}")
            raise IndexError(message="Invalid page index, pages object does not contain specified page")
        self["__items__"][index] = item
        
    def items(self) -> list[Paginated]:
        return self["__items__"]
    
    def set_items(self, items):
        self["__items__"] = items
        
    def symbol(self) -> str:
        return self["__symbol__"]
    
    def set_symbol(self, symbol):
        self["__symbol__"] = symbol
        
    def page_index(self) -> int:
        return self["__page_index__"]
    
    def set_page_index(self, page_index):
        self["__page_index__"] = page_index
    
    