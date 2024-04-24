from typing import Any
from .adapter import Adapter


class GoogleNewsAdapter(Adapter):

    def parse(self, data: Any):
        print(data)
        pass
