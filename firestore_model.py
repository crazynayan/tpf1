from google.cloud.exceptions import NotFound
from google.cloud.firestore import Query
from firebase_admin import firestore, initialize_app, credentials, get_app


def init_firestore_db(gac_key_path, name=None):
    if name:
        try:
            db_app = get_app(name)
        except ValueError:
            db_app = initialize_app(credentials.Certificate(gac_key_path), name=name)
    else:
        try:
            db_app = get_app()
        except ValueError:
            db_app = initialize_app(credentials.Certificate(gac_key_path))

    FirestoreModel.init_db(db_app)
    return db_app


class FirestoreModel:
    # COLLECTION should ALWAYS be overridden by the base class with the collection name
    COLLECTION = 'firestore'
    # DEFAULT FIELD can be overridden if the default name of the field needs a change
    DEFAULT = 'name'
    BATCH = None
    DELETE_BATCH_SIZE = 10
    ORDER_ASCENDING = Query.ASCENDING
    ORDER_DESCENDING = Query.DESCENDING
    try:
        db = firestore.client()
    except ValueError:
        db = None

    def __init__(self, field_value=None):
        self.doc_id = None
        setattr(self, self.DEFAULT, field_value)

    def __repr__(self):
        return f'<{self.DEFAULT}: {getattr(self, self.DEFAULT)}>'

    @classmethod
    def init_db(cls, db_app=None):
        try:
            cls.db = firestore.client(db_app)
        except ValueError:
            return False
        return True

    @classmethod
    def get_transaction(cls):
        return cls.db.transaction() if cls.db else None

    def to_dict(self):
        model_dict = self.__dict__.copy()
        try:
            del model_dict['doc_id']
        except KeyError:
            pass
        return model_dict

    @classmethod
    def from_dict(cls, source):
        if cls.DEFAULT not in source:
            return None
        model = cls(source[cls.DEFAULT])
        for field in model.__dict__:
            if field in source:
                setattr(model, field, source[field])
        return model

    def create(self):
        doc = self.db.collection(self.COLLECTION).add(self.to_dict())
        self.doc_id = doc[1].id
        return self

    def update(self, doc_id=None):
        if doc_id:
            self.doc_id = doc_id
        elif not self.doc_id:
            return None
        self.db.collection(self.COLLECTION).document(self.doc_id).set(self.to_dict())
        return self

    @classmethod
    def read(cls, doc_id=None):
        if not doc_id:
            return None
        try:
            doc = cls.db.collection(cls.COLLECTION).document(doc_id).get()
        except NotFound:
            return None
        if not doc.exists:
            return None
        model = cls.from_dict(doc.to_dict())
        model.doc_id = doc.id
        return model

    def refresh(self):
        if not self.doc_id:
            return False
        try:
            doc = self.db.collection(self.COLLECTION).document(self.doc_id).get()
        except NotFound:
            return False
        if not doc.exists:
            return False
        doc_dict = doc.to_dict()
        for field in doc_dict:
            if field in self.__dict__:
                setattr(self, field, doc_dict[field])
        return True

    def get_doc(self, transaction=None):
        # Returns the document reference if no transaction provided else it will provided a transactional doc
        if not self.doc_id:
            return None, None
        doc_ref = self.db.collection(self.COLLECTION).document(self.doc_id)
        doc = None
        if transaction:
            try:
                doc = self.db.collection(self.COLLECTION).document(self.doc_id).get(transaction=transaction)
            except NotFound:
                pass
            if doc and not doc.exists:
                doc = None
        return doc_ref, doc

    def delete(self, doc_id=None):
        if doc_id:
            self.doc_id = doc_id
        elif not self.doc_id:
            return None
        self.db.collection(self.COLLECTION).document(self.doc_id).delete()
        self.doc_id = None
        return self

    @classmethod
    def _get_models(cls, docs, dict_type=False):
        models = dict() if dict_type else list()
        for doc in docs:
            model = cls.from_dict(doc.to_dict())
            model.doc_id = doc.id
            if dict_type:
                models[doc.id] = model
            else:
                models.append(model)
        return models

    @classmethod
    def get_all(cls, dict_type=False):
        docs = cls.db.collection(cls.COLLECTION).stream()
        return cls._get_models(docs, dict_type)

    @classmethod
    def query(cls, dict_type=False, **kwargs):
        doc_ref = cls.db.collection(cls.COLLECTION)
        for field in kwargs:
            if field in cls().__dict__ and field != 'doc_id':
                doc_ref = doc_ref.where(field, '==', kwargs[field])
        docs = doc_ref.stream()
        return cls._get_models(docs, dict_type)

    @classmethod
    def query_array(cls, array, dict_type=False):
        doc_ref = cls.db.collection(cls.COLLECTION)
        if array and isinstance(array, tuple) and len(array) == 2:
            doc_ref = doc_ref.where(array[0], 'array_contains', array[1])
        docs = doc_ref.stream()
        return cls._get_models(docs, dict_type)

    @classmethod
    def order_by(cls, *criteria, query=None, array=None, page=None):
        doc_ref = cls.db.collection(cls.COLLECTION)
        if query and isinstance(query, dict):
            for field in query:
                if field in cls().__dict__ and field != 'doc_id':
                    doc_ref = doc_ref.where(field, '==', query[field])
        if array and isinstance(array, tuple) and len(array) == 2:
            doc_ref = doc_ref.where(array[0], 'array_contains', array[1])
        saved_ref = doc_ref
        field = None
        order = None
        for criterion in criteria:
            if isinstance(criterion, str):
                field = criterion
                order = cls.ORDER_ASCENDING
            elif isinstance(criterion, tuple) and \
                    len(criterion) >= 2 and \
                    isinstance(criterion[0], str) and \
                    criterion[1] in (cls.ORDER_DESCENDING, cls.ORDER_ASCENDING):
                field = criterion[0]
                order = criterion[1]
            if order:
                doc_ref = doc_ref.order_by(field, direction=order)
        # Multiple criteria for order will raise an exception if composite index not defined.
        # The exception is NOT caught here since it will help the developer to create the composite index
        # All scenarios for multiple order_by is recommended to be tested in unittest.
        if page is None or not isinstance(page, FirestorePage) or len(criteria) != 1\
                or page.want not in [FirestorePage.NEXT_PAGE, FirestorePage.PREV_PAGE]:
            docs = doc_ref.stream()
            models = list()
            for doc in docs:
                model = cls.from_dict(doc.to_dict())
                model.doc_id = doc.id
                models.append(model)
            return models
        # Pagination logic
        if page.want == FirestorePage.NEXT_PAGE or page.current_start is None:
            if page.current_end is None:
                query = doc_ref.limit(page.per_page)
            else:
                end_ref, _ = page.current_end.get_doc()
                query = doc_ref.limit(page.per_page).start_after(end_ref.get())
            models = list()
            for doc in query.stream():
                model = cls.from_dict(doc.to_dict())
                model.doc_id = doc.id
                models.append(model)
                if len(models) == 1:
                    page.current_start = model
                page.current_end = model
            try:
                end_ref, _ = page.current_end.get_doc()
                next(doc_ref.limit(1).start_after(end_ref.get()).stream())
                page.has_next = True
            except (StopIteration, AttributeError):
                page.has_next = False
            try:
                reverse = cls.ORDER_ASCENDING if order == cls.ORDER_DESCENDING else cls.ORDER_DESCENDING
                reverse_ref = saved_ref.order_by(field, direction=reverse)
                end_ref, _ = page.current_start.get_doc()
                next(reverse_ref.limit(1).start_after(end_ref.get()).stream())
                page.has_prev = True
            except (StopIteration, AttributeError):
                page.has_prev = False
            page.items = models
            return page
        # Previous Page logic
        if order == cls.ORDER_DESCENDING:
            reverse = cls.ORDER_ASCENDING
            reverse_sort = True
        else:
            reverse = cls.ORDER_DESCENDING
            reverse_sort = False
        reverse_ref = saved_ref.order_by(field, direction=reverse)
        start_ref, _ = page.current_start.get_doc()
        query = reverse_ref.limit(page.per_page).start_after(start_ref.get())
        models = list()
        for doc in query.stream():
            model = cls.from_dict(doc.to_dict())
            model.doc_id = doc.id
            models.append(model)
            if len(models) == 1:
                page.current_end = model
            page.current_start = model
        try:
            start_ref, _ = page.current_start.get_doc()
            next(reverse_ref.limit(1).start_after(start_ref.get()).stream())
            page.has_prev = True
        except (StopIteration, AttributeError):
            page.has_prev = False
        try:
            end_ref, _ = page.current_start.get_doc()
            next(doc_ref.limit(1).start_after(end_ref.get()).stream())
            page.has_next = True
        except (StopIteration, AttributeError):
            page.has_next = False
        if len(models) > 0:
            models.sort(key=lambda item: getattr(item, field), reverse=reverse_sort)
        page.items = models
        return page

    @classmethod
    def query_first(cls, **kwargs):
        doc_ref = cls.db.collection(cls.COLLECTION)
        for field in kwargs:
            if field in cls().__dict__ and field != 'doc_id':
                doc_ref = doc_ref.where(field, '==', kwargs[field])
        docs = doc_ref.limit(1).stream()
        try:
            doc = next(docs)
        except StopIteration:
            return None
        model = cls.from_dict(doc.to_dict())
        model.doc_id = doc.id
        return model

    @classmethod
    def delete_all(cls, batch_size=None):
        if batch_size is None or batch_size < 1:
            batch_size = cls.DELETE_BATCH_SIZE
        deleted = 0
        for doc in cls.db.collection(cls.COLLECTION).limit(batch_size).stream():
            doc.reference.delete()
            deleted += 1
        if deleted == batch_size:   # if more to delete
            return cls.delete_all(batch_size)

    @classmethod
    def init_batch(cls):
        cls.BATCH = cls.db.batch()

    def update_batch(self):
        if not self.doc_id:
            return None
        if not self.BATCH:
            self.BATCH = self.db.batch()
        model_ref = self.db.collection(self.COLLECTION).document(self.doc_id)
        self.BATCH.set(model_ref, self.to_dict())
        return self

    @classmethod
    def commit_batch(cls):
        if not cls.BATCH:
            return False
        cls.BATCH.commit()
        cls.BATCH = None
        return True


class FirestorePage:
    PER_PAGE = 25
    NEXT_PAGE = 1
    PREV_PAGE = -1

    def __init__(self, per_page=None):
        self.per_page = per_page if per_page is not None else self.PER_PAGE
        self.current_start = None
        self.current_end = None
        self.has_next = False
        self.has_prev = False
        self.items = None
        self.want = self.NEXT_PAGE


class MapToModelMixin:
    """
    Overrides from_dict and to_dict of FirestoreModel to ensure firestore maps are converted to/from models while
    reading and writing from files.
    Usage:
    1. For base models: Inherit before FirestoreModel [for e.g. Class(MapToModelMixin, FirestoreModel)].
    2. For models that are maps of a containing model just inherit MapToModelMixin
    Override the MAP_OBJECTS field with a set of containing model that are represented by maps in firestore.
    """
    MAP_OBJECTS = {}
    INITIALIZE = 'init'

    def to_dict(self):
        model_dict = self.__dict__.copy()
        try:
            del model_dict['doc_id']
        except KeyError:
            pass
        for field in model_dict:
            self_field = getattr(self, field)
            if type(self_field) in self.MAP_OBJECTS:
                model_dict[field] = getattr(self, field).to_dict()
            elif isinstance(self_field, list) and self_field and type(self_field[0]) in self.MAP_OBJECTS:
                model_list = list()
                if len(self_field) > 1:
                    for sub_dict in self_field[1:]:
                        model_list.append(sub_dict.to_dict())
                model_dict[field] = model_list
                if len(model_dict) == 1:
                    return model_list
        return model_dict

    @classmethod
    def from_dict(cls, source):
        model = cls()
        if isinstance(source, dict):
            for field in source:
                if field not in model.__dict__:
                    continue
                model_field = getattr(model, field)
                if type(model_field) in cls.MAP_OBJECTS:
                    setattr(model, field, type(model_field).from_dict(source[field]))
                else:
                    setattr(model, field, source[field])
        elif isinstance(source, list) and len(model.__dict__) == 1:
            model_field = getattr(model, next(key for key in model.__dict__))
            if isinstance(model_field, list) and model_field and type(model_field[0]) in cls.MAP_OBJECTS:
                model_list = [type(model_field[0])()]
                for source_dict in source:
                    model_list.append(type(model_field[0]).from_dict(source_dict))
                setattr(model, next(key for key in model.__dict__), model_list)
        return model


class CollectionMixin(MapToModelMixin):
    def __init__(self, custom_class):
        self._object_list = list()
        if isinstance(custom_class, type(CollectionItemMixin)):
            self._object_list.append(custom_class())
        else:
            self._object_list.append(self.INITIALIZE)

    def __repr__(self):
        if self.is_empty:
            return self.INITIALIZE
        return ''.join([f'{ref}, ' for ref in self._object_list[1:]])[:-2]

    def __getitem__(self, index):
        return self._object_list[index]

    def append(self, other):
        if not isinstance(other, type(self._object_list[0])):
            return False
        self._object_list.append(other)
        return True

    def append_unique(self, other):
        if not isinstance(other, type(self._object_list[0])):
            return False
        if other not in self._object_list:
            self._object_list.append(other)
        return True

    def extend(self, others):
        if not isinstance(others, type(self)) or \
                others.is_empty or \
                not isinstance(others[0], type(self._object_list[0])):
            return False
        self._object_list.extend(others[1:])
        return True

    def extend_unique(self, others):
        if not isinstance(others, type(self)) or \
                others.is_empty or \
                not isinstance(others[0], type(self._object_list[0])):
            return False
        for other in others[1:]:
            if other not in self._object_list:
                self._object_list.append(other)
        return True

    @property
    def list_values(self):
        if self.is_empty:
            return list()
        else:
            return self._object_list[1:]

    @property
    def is_empty(self):
        return True if len(self._object_list) <= 1 else False


class CollectionItemMixin(MapToModelMixin):
    # Override the DEFAULT with a field name in your class which can never be None
    DEFAULT = 'name'

    def __init__(self):
        setattr(self, self.DEFAULT, None)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        for key in self.__dict__:
            if key not in other.__dict__:
                return False
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    @property
    def is_empty(self):
        return True if getattr(self, self.DEFAULT) is None else False

    def get_str(self, text=None):
        if self.is_empty:
            return self.INITIALIZE
        return text if text else f'<{self.DEFAULT}: {getattr(self, self.DEFAULT)}>'
