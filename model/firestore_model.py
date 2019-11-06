from copy import deepcopy
from typing import TypeVar, Optional, Set, Union, Type, List

from google.cloud.exceptions import NotFound
from google.cloud.firestore import Client, CollectionReference, Query


def init_firestore_db():
    # Need environment variable GOOGLE_APPLICATION_CREDENTIALS set to path of the the service account key (json file)
    if FirestoreModel.DB is None:
        FirestoreModel.DB = Client()
    return


FirestoreModelType = TypeVar('FirestoreModelType', bound='FirestoreModel')

ORDER_ASCENDING = Query.ASCENDING
ORDER_DESCENDING = Query.DESCENDING


class _Query:
    _COMPARISON_OPERATORS = {'<', '<=', '==', '>', '>=', 'array contains'}
    _DIRECTION = {ORDER_ASCENDING, ORDER_ASCENDING}
    _MODEL_CLASS: Type[FirestoreModelType] = None
    _DOC_REF: CollectionReference = None
    _QUERY_REF: Union[Query, CollectionReference] = None
    _MODEL_FIELDS: Set = None

    @classmethod
    def set_model(cls, model_class: Type[FirestoreModelType]) -> None:
        init_firestore_db()
        cls._MODEL_CLASS = model_class
        cls._MODEL_FIELDS = set(model_class().to_dict())
        cls._DOC_REF: CollectionReference = cls._MODEL_CLASS.DB.collection(cls._MODEL_CLASS.COLLECTION)
        cls.init_query()

    @classmethod
    def init_query(cls) -> None:
        cls._QUERY_REF = cls._DOC_REF

    @classmethod
    def filter_by(cls, **kwargs) -> Type['_Query']:
        for field_name, field_value in kwargs.items():
            if field_name in cls._MODEL_FIELDS:
                cls._QUERY_REF = cls._QUERY_REF.where(field_name, '==', field_value)
        return cls

    @classmethod
    def filter(cls, field_name: str, condition: str, field_value: object) -> Type['_Query']:
        if field_name not in cls._MODEL_FIELDS or condition not in cls._COMPARISON_OPERATORS:
            return cls
        cls._QUERY_REF = cls._QUERY_REF.where(field_name, condition, field_value)
        return cls

    @classmethod
    def order_by(cls, field_name: str, direction: str = ORDER_ASCENDING) -> Type['_Query']:
        if field_name not in cls._MODEL_FIELDS or direction not in cls._DIRECTION:
            return cls
        cls._QUERY_REF = cls._QUERY_REF.order_by(field_name, direction=direction)
        return cls

    @classmethod
    def get(cls) -> List[FirestoreModelType]:
        docs = cls._QUERY_REF.stream()
        cls.init_query()
        return [cls._MODEL_CLASS.from_dict(doc.to_dict(), doc.id) for doc in docs]

    @classmethod
    def first(cls) -> Optional[FirestoreModelType]:
        doc = next((cls._QUERY_REF.limit(1).stream()), None)
        cls.init_query()
        return cls._MODEL_CLASS.from_dict(doc.to_dict(), doc.id) if doc else None

    @classmethod
    def get_by_id(cls, doc_id: str) -> Optional[FirestoreModelType]:
        try:
            doc = cls._DOC_REF.document(doc_id).get()
        except NotFound:
            doc = None
        return cls._MODEL_CLASS.from_dict(doc.to_dict(), doc.id) if doc else None


class FirestoreModel:
    COLLECTION: Optional[str] = None  # Collection should be initialize by the child class call to set_collection.
    DB: Optional[Client] = None  # db should NOT be changed directly. It is set by set_collection method.
    query: _Query = _Query()

    @classmethod
    def set_collection(cls, collection: str):
        cls.COLLECTION = collection
        cls.query.set_model(cls)

    def __init__(self):
        self._doc_id: Optional[str] = None  # This tracks the document id of the collection.

    def __repr__(self) -> str:
        return f"/{self.COLLECTION}/{self._doc_id}"

    @property
    def doc_id(self) -> str:
        return self._doc_id

    def set_doc_id(self, doc_id: str) -> None:
        self._doc_id = doc_id

    def to_dict(self) -> dict:
        model_dict = deepcopy(self.__dict__)
        del model_dict['_doc_id']
        return model_dict

    @classmethod
    def from_dict(cls, model_dict: dict, doc_id: Optional[str] = None) -> FirestoreModelType:
        model = cls()
        if doc_id:
            model.set_doc_id(doc_id)
        for field in model_dict:
            if field in model.__dict__:
                setattr(model, field, model_dict[field])
        return model

    @classmethod
    def create_from_dict(cls, model_dict: dict, doc_id: Optional[str] = None) -> FirestoreModelType:
        model = cls.from_dict(model_dict, doc_id)
        if doc_id:
            model.update()
        else:
            doc = cls.DB.collection(cls.COLLECTION).add(model_dict)
            model.set_doc_id(doc[1].id)
        return model

    def update(self, doc_id: Optional[str] = None) -> None:
        self._doc_id = doc_id if doc_id else self._doc_id
        if self._doc_id:
            self.DB.collection(self.COLLECTION).document(self._doc_id).set(self.to_dict())
        return

    def delete(self) -> None:
        if not self._doc_id:
            return
        self.DB.collection(self.COLLECTION).document(self._doc_id).delete()
        self._doc_id = None
