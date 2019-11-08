from copy import deepcopy
from typing import TypeVar, Optional, Set, Union, Type, List, Dict, Iterable

from google.cloud.exceptions import NotFound
from google.cloud.firestore import Client, CollectionReference, Query, DocumentSnapshot

# Need environment variable GOOGLE_APPLICATION_CREDENTIALS set to path of the the service account key (json file)
DB = Client()

FirestoreDocumentChild = TypeVar('FirestoreDocumentChild', bound='FirestoreDocument')

ORDER_ASCENDING = Query.ASCENDING
ORDER_DESCENDING = Query.DESCENDING

REFERENCE: Dict[str, callable] = dict()


class _Query:
    _COMPARISON_OPERATORS = {'<', '<=', '==', '>', '>=', 'array contains'}
    _DIRECTION = {ORDER_ASCENDING, ORDER_DESCENDING}

    def __init__(self):
        self._doc_class: Optional[Type[FirestoreDocumentChild]] = None
        self._doc_ref: Optional[CollectionReference] = None
        self._query_ref: Optional[Union[Query, CollectionReference]] = None
        self._doc_fields: Set = set()
        self._cascade: bool = False

    def set_document(self, document_class: Type[FirestoreDocumentChild]) -> None:
        self._doc_class = document_class
        self._doc_fields = set(document_class().doc_to_dict())
        self._doc_ref: CollectionReference = DB.collection(self._doc_class.COLLECTION)
        self.init_query()

    def init_query(self) -> None:
        self._query_ref = self._doc_ref
        self._cascade = False

    def filter_by(self, **kwargs) -> '_Query':
        for field_name, field_value in kwargs.items():
            if field_name in self._doc_fields:
                self._query_ref = self._query_ref.where(field_name, '==', field_value)
        return self

    def filter(self, field_name: str, condition: str, field_value: object) -> '_Query':
        if field_name not in self._doc_fields or condition not in self._COMPARISON_OPERATORS:
            return self
        self._query_ref = self._query_ref.where(field_name, condition, field_value)
        return self

    def order_by(self, field_name: str, direction: str = ORDER_ASCENDING) -> '_Query':
        if field_name not in self._doc_fields or direction not in self._DIRECTION:
            return self
        self._query_ref = self._query_ref.order_by(field_name, direction=direction)
        return self

    def limit(self, count: int) -> '_Query':
        self._query_ref = self._query_ref.limit(count) if count > 0 else self._query_ref.limit(0)
        return self

    @property
    def cascade(self) -> '_Query':
        self._cascade = True
        return self

    def get(self) -> List[FirestoreDocumentChild]:
        docs: Iterable[DocumentSnapshot] = self._query_ref.stream()
        documents: List = [self._doc_class.dict_to_doc(doc.to_dict(), doc.id, cascade=self._cascade) for doc in docs]
        self.init_query()
        return documents

    def first(self) -> Optional[FirestoreDocumentChild]:
        doc: DocumentSnapshot = next((self._query_ref.limit(1).stream()), None)
        document = self._doc_class.dict_to_doc(doc.to_dict(), doc.id, cascade=self._cascade) if doc else None
        self.init_query()
        return document

    def delete(self) -> bool:
        docs: Iterable[DocumentSnapshot] = self._query_ref.stream()
        documents: List = [self._doc_class.dict_to_doc(doc.to_dict(), doc.id, cascade=self._cascade) for doc in docs]
        result = all(document.delete(cascade=self._cascade) for document in documents)
        self.init_query()
        return result


class FirestoreDocument:
    COLLECTION: Optional[str] = None  # Collection should be initialize by the child class call to init.
    objects: _Query = None

    @classmethod
    def init(cls, collection: Optional[str] = None):
        cls.COLLECTION = collection if collection else f"{cls.__name__.lower()}s"
        cls.objects = _Query()
        cls.objects.set_document(cls)
        REFERENCE[cls.COLLECTION] = cls

    def __init__(self):
        self._doc_id: Optional[str] = None  # This tracks the document id of the collection.

    def __repr__(self) -> str:
        return f"/{self.COLLECTION}/{self._doc_id}"

    @property
    def id(self) -> str:
        return self._doc_id

    def set_id(self, doc_id: str) -> None:
        self._doc_id = doc_id

    def doc_to_dict(self) -> dict:
        doc_dict = deepcopy(self.__dict__)
        del doc_dict['_doc_id']
        return doc_dict

    @classmethod
    def dict_to_doc(cls, doc_dict: dict, doc_id: Optional[str] = None, cascade: bool = False) -> FirestoreDocumentChild:
        document = cls()
        if doc_id:
            document.set_id(doc_id)
        for field, value in doc_dict.items():
            if field not in document.__dict__:
                continue
            if not cascade or not cls._eligible_for_cascade(field, value):
                setattr(document, field, value)
                continue
            values = value if isinstance(value, list) else [value]
            if isinstance(values[0], dict):
                firestore_document_list = [REFERENCE[field].dict_to_doc(value_dict, cascade=True)
                                           for value_dict in values]
            else:
                firestore_document_list = [REFERENCE[field].get_by_id(nested_id, cascade=True) for nested_id in values]
            setattr(document, field, firestore_document_list)
        return document

    @staticmethod
    def _eligible_for_cascade(field, value) -> bool:
        if field not in REFERENCE:
            return False
        if isinstance(value, dict):
            return True
        if not isinstance(value, list):
            return False
        first_object = next(iter(value), None)
        if isinstance(first_object, dict) or isinstance(first_object, str):
            return True
        return False

    @classmethod
    def create_from_dict(cls, doc_dict: dict) -> FirestoreDocumentChild:
        document = cls.dict_to_doc(doc_dict, cascade=True)
        original_document = deepcopy(document)
        doc_id = document.create()
        original_document.set_id(doc_id)
        return original_document

    def create(self) -> str:
        documents = self._get_nested_documents()
        for field, doc_list in documents.items():
            ids: List[str] = list()
            for document in doc_list:
                doc_id = document.create()
                ids.append(doc_id)
            setattr(self, field, ids)
        doc = DB.collection(self.COLLECTION).add(self.doc_to_dict())
        return doc[1].id

    def save(self, cascade: bool = False) -> bool:
        if not self._doc_id:
            return False
        result = True
        document_copy = deepcopy(self)
        documents = document_copy._get_nested_documents()
        for field, doc_list in documents.items():
            ids: List[str] = list()
            for document in doc_list:
                if not document.id:
                    return False
                ids.append(document.id)
                if not cascade:
                    continue
                result = document.save(cascade=True)
                if result is False:
                    return False
            setattr(document_copy, field, ids)
        DB.collection(self.COLLECTION).document(self._doc_id).set(document_copy.doc_to_dict())
        return result

    def delete(self, cascade: bool = False) -> bool:
        if not self._doc_id:
            return False
        result = True
        if cascade:
            documents = self._get_nested_documents()
            result = all(document.delete(cascade=True) for _, doc_list in documents.items() for document in doc_list)
        if result is True:
            DB.collection(self.COLLECTION).document(self._doc_id).delete()
            self._doc_id = None
        return result

    def _get_nested_documents(self) -> Dict[str, List[FirestoreDocumentChild]]:
        documents = dict()
        for field, value in self.__dict__.items():
            if not isinstance(value, list) or not isinstance(next(iter(value), None), FirestoreDocument):
                continue
            documents[field] = list()
            for nested_document in value:
                documents[field].append(nested_document)
        return documents

    @classmethod
    def get_by_id(cls, doc_id: str, cascade: bool = False) -> Optional[FirestoreDocumentChild]:
        try:
            doc = DB.collection(cls.COLLECTION).document(doc_id).get()
        except NotFound:
            return None
        return cls.dict_to_doc(doc.to_dict(), doc.id, cascade=cascade)
