from typing import Any, Callable


class Pipeline:

    __name__ = "pipeline"
    __done__ = False
    action: Callable

    def __init__(
        self,
        action: Callable,
        name: str = __name__,
    ) -> None:
        """Takes a pipeline argument that is an NDarray of functions that accept a context of **kwargs"""
        if isinstance(action, Callable):
            self.action = action

        if isinstance(name, str):
            self.__name__ = name

    def __call__(self, context: dict[str, Any]):
        """**kwargs is the context of the super class 'Engine'

        Returns:
            dict[str, Any]: The context to be passed to the next functions in the pipeline.
        """
        next_context = self.action(**context)
        for key, value in next_context.items():
            context[key] = value

        self.done()

    def reset(self):
        self.__done__ = False

    def done(self):
        print(f"Pipeline(name={self.__name__}) action finished")
        self.__done__ = True
