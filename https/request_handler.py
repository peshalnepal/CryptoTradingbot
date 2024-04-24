from http import HTTPMethod
from typing import Any
from apis import Provider
from requests import request


class RequestHandler:
    __provider = None

    def __init__(self, provider: Provider) -> None:
        self.__provider = provider
        pass

    def __call__(self, *params: Any, **kwds: Any) -> Any:
        if "method" not in kwds.keys():
            raise ValueError("[method] must be supplied to request handler.")
        if "endpoint" not in kwds.keys():
            raise ValueError("[endpoint] must be supplied to request handler.")

        endpoint = kwds.get("endpoint", None)
        method = kwds.get("method", HTTPMethod.GET)
        params = kwds.get("params", None)

        response = request(
            url=self.__provider.base_url() + endpoint,
            method=method,
            params=params,
        )

        response.raise_for_status()
        return response.json()

    def set_provider(self, provider: Provider) -> None:
        self.__provider = provider
