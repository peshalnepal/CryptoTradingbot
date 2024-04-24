# Abstraction, only add implementations to subclasses

from .persistent import Persistent
from typing import Any


# Model serves as an abstraction of the single responsibility layer Type
class Model(Persistent):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        pass

    def __setattr__(self, __name: str, __value: Any) -> None:
        self[__name] = __value

    def from_df(self, **kwargs):
        pass

    def build(self) -> dict:
        pass
