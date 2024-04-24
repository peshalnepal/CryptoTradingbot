# *Interface* Do Not Implement
from typing import Any


class Database:
    def set(self, *objs: Any) -> Any:
        # Add entry to database
        pass

    def set_all(self, *objs: Any) -> list[Any]:
        pass

    def get(self, *objs: Any, **kwargs) -> Any:
        pass

    def get_all(self, *objs: Any, **kwargs) -> list[Any]:
        pass

    def delete(self, *objs: Any, **kwargs) -> Any:
        pass

    def update(self):
        pass

    def subscribe(self):
        pass

    def unsubscribe(self):
        pass
