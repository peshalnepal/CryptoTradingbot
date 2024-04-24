# Firebase Firestore.
# Why I am choosing Firestore over Realtime: https://firebase.google.com/docs/database/rtdb-vs-firestore
# Docs: https://firebase.google.com/docs/firestore
# Limits: https://firebase.google.com/docs/firestore/quotas

# Please don't write any code that will incur costs on my google account.
# If you're having trouble w/ batch operations. Message Thomas on WhatsApp.
from typing import Any
from pandas import Timestamp
from .database import Database
from .models import Model
from firebase_admin import App, firestore
from google.cloud.firestore import (
    Client,
    DocumentReference,
    DocumentSnapshot,
    CollectionReference,
)


class FirestoreDB(Database):

    __db__: Client

    def __init__(self, app: App) -> None:
        super().__init__()
        self.__db__ = firestore.client(app)

    # If obj is
    def set(self, *objs: Model) -> Model:
        for obj in objs:
            coll = self.__db__.collection(obj.get_coll())
            doc = coll.document(obj.get_id())
            doc.set(obj.build())

    def set_all(self, *objs: Model) -> list[Model]:
        batch = self.__db__.batch()
        coll = self.get_coll(*objs)
        
        for obj in objs:
            data = obj.build()
            id = obj.get_id()
            doc = coll.document(id)
            batch.set(doc, data)
            
        batch.commit()
        return list(objs)

    def get(self, *objs: Model, **kwargs) -> Model:
        obj = objs[0]
        path = kwargs.get("path", "")
        coll = self.__db__.collection(obj.get_coll())
        snap = coll.document(obj.get_id()).get()
        return snap.get(path)

    def get_all(self, *objs: Model, **kwargs) -> list[Model]:

        r = []
        path = kwargs.get("path", "")

        if len(objs) == 1:
            obj = objs[0]
            coll = self.__db__.collection(obj.get_coll())

            if "sort_by" in kwargs:
                query = coll.order_by(
                    kwargs.get("sort_by"),
                    direction=kwargs.get("sort_by_direction", "ASCENDING"),
                )

                for doc in query.get():
                    r.append(doc.get(path))

                return r

            for doc in coll.get():
                r.append(doc.get(path))

            return r

        for obj in objs:
            coll = self.__db__.collection(obj.get_coll())
            doc = coll.document(obj.get_id())
            r.append(doc.get().get(path))

        return r

    def delete(self, *objs: Model) -> tuple[Timestamp, Model]:
        obj = objs[0]
        coll = self.__db__.collection(obj.get_coll())
        timestamp = coll.document(obj.get_id()).delete()
        return [timestamp, obj]

    def delete_all(self, *objs: Model) -> list[tuple[Timestamp, Model]]:
        r = []
        for obj in objs:
            coll = self.__db__.collection(obj.get_coll())
            doc = coll.document(obj.get_id())
            timestamp = doc.delete()
            r.append([timestamp, obj])
        return r

    def get_doc(self, *objs: Model) -> DocumentReference:
        obj = objs[0]
        coll = self.__db__.collection(obj.get_coll())
        return coll.document(obj.get_id())

    def get_docs(self, coll: CollectionReference) -> list[DocumentReference]:
        return coll.get()

    def get_coll(self, *objs: Model) -> CollectionReference:
        obj = objs[0]
        return self.__db__.collection(obj.get_coll())

    def set_docs(self, **kwargs) -> Any:
        docs: list[DocumentReference] = kwargs.get("docs")
        objs: list[Model] = kwargs.get("models")
        for doc, obj in zip(docs, objs):
            doc.set(obj.build())
    
    def update(self, *objs, **kwargs):
        field = kwargs.get("field")
        value = kwargs.get("value")
        symbol = kwargs.get("symbol")
        obj: Model = objs[0]
        
        # Get reference to Sentiment_BATCHES
        coll:CollectionReference = self.__db__.collection(obj.get_coll())
        # Get reference to BTC-USDT
        doc:DocumentReference = coll.document(symbol)
        # Get reference to BTC-USDT_batches
        sub_coll:CollectionReference = doc.collection(f"{symbol}_batches")
        # Get document to update
        sub_doc:DocumentReference = sub_coll.document(obj.get_id())
        
        sub_doc.update({field: value})

    def subscribe(self):
        pass

    def unsubscribe(self):
        pass
