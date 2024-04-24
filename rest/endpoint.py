

from typing import Any


class Endpoint:
    __ctx__: dict[str, Any] = {}
    
    def __init__(self, **kwargs) -> None:
        self.__ctx__ = kwargs.get("context", {})
        
    def set_ctx(self, ctx: dict[str, Any]):
        self.__ctx__ = {**self.__ctx__, **ctx}
        
    def ctx(self, key = None):
        if key == None:
            return self.__ctx__
        if key not in self.__ctx__:
            raise KeyError(message=f"{key} not found in endpoint ctx")
        return self.__ctx__[key]        
    