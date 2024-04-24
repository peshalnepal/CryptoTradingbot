# Abstraction, don't implement functions here, only in sub-classes.
from db import Database
from uuid import uuid4


class Persistent(dict):
    # name == model file name
    # used to access the collection related to this model.
    __coll__: str | int = None

    # uuid4 or xx-xxxx-xxxx timestamp (seconds)
    # used to access a particular models data
    __id__: str | int = None

    # reference to database.
    __db__: Database

    def __init__(self, **kwargs) -> None:
        self.__coll__ = kwargs.get("coll")
        self.__id__ = kwargs.get("id", str(uuid4()))
        self.__db__ = kwargs.get("db", None)
        pass

    def get_coll(self) -> str:
        return self["__coll__"]

    def get_id(self) -> str:
        return self["__id__"]

    def get_db(self) -> Database:
        return self["__db__"]

    def set(self, **kwargs):
        pass

    def get(self, **kwargs):
        pass

    def get_all(self, **kwargs):
        pass

    def delete(self, **kwargs):
        pass

    def update(self, **kwargs):
        pass

    def subscribe(self, **kwargs):
        pass

    def unsubscribe(self, **kwargs):
        pass
