from typing import Any
from db.models import Paginated, Page

class Adapter:

    def parse_items(self, data: Any) -> list[Paginated]:
        pass
    
    def parse_pages(self, data: Any) -> list[Page]:
        pass
    
    def parse(self, data: Any) -> Any:
        pass

    def parse_df(self, df: Any) -> Any:
        pass

    def parse_batch(self, data: Any) -> Any:
        pass

    def parse_light(self, data: Any) -> Any:
        pass
    

