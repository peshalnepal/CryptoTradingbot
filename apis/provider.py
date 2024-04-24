from security import Credentials


class Provider:
    credentials: Credentials = None
    base_url: str = None

    def api_key(self) -> str:
        pass

    def base_url(self) -> str:
        pass
