from typing import Type, TypeVar

T = TypeVar("T")


class AdapterProvider:

    __adapters__: set[T] = set()

    def __call__(self, type: Type[T]) -> T:
        for adapter in self.__adapters__:
            if isinstance(adapter, type):
                return adapter

        print(f"Could not find adapter of type {type}")
        return None

    def add(self, adapter: T):
        for existing_adapter in self.__adapters__:
            if isinstance(adapter, type(existing_adapter)):
                print(f"Adapter: [{adapter}] \n  - already exists in the provider")
                return

        self.__adapters__.add(adapter)
        print(f"Adapter added: [{adapter}]")


adapter_provider = AdapterProvider()
