from typing import Type, TypeVar

# from ..sockets import OKEXCandlestickSocket

T = TypeVar("T")


class ServiceProvider:

    __services__: set[T] = set()

    def __call__(self, type: Type[T]) -> T:
        for service in self.__services__:
            if isinstance(service, type):
                return service

        print(f"Could not find service of type {type}")
        return None

    def add(self, service: T):
        for existing_service in self.__services__:
            if isinstance(service, type(existing_service)):
                print(f"Service: [{service}] \n  - already exists in the provider")
                return

        self.__services__.add(service)
        print(f"Service added: [{service}]")


service_provider = ServiceProvider()
