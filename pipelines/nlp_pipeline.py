from typing import Any, Callable
from .pipeline import Pipeline


class NLPPipeline(Pipeline):

    __name__ = "nlp_pipeline"

    def __init__(
        self,
        action: Callable,
        name: str = __name__,
        **kwargs,
    ) -> None:
        super().__init__(action, name, **kwargs)

    def __call__(self, **kwargs) -> dict[str, Any]:
        result = self.action(**{**self.context(), **kwargs})
        print(f"{self.__name__} executed")
        return self.done(result)
