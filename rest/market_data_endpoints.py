# Interface. No implementation.
from typing import Any
from .endpoint import Endpoint

class MarketDataEndpoints(Endpoint):

    # populated from the observable_context created in server.py.
    __context__: dict[str, Any] = {}

    def history(self, *args, **kwargs):
        pass

    # Return the available symbols for the exchange api.
    def symbols(self, *args, **kwargs):
        pass
