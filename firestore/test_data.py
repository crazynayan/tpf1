from typing import Dict, List

from firestore.firestore_ci import FirestoreDocument


class TestData(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.regs: Dict[str, str] = dict()
        self.cores: List[Core] = list()
        self.pnr: List[Pnr] = list()
        self.tpfdf: List[Tpfdf] = list()
        self.flat_files = list()
        self.errors: List[str] = list()
        self.test_data: List[TestData] = list()  # For output

    @classmethod
    def create_test_data(cls, test_data_dict: dict) -> str:
        test_data = cls.create_from_dict(test_data_dict)
        return test_data.id

    @classmethod
    def get_test_data(cls, test_data_id: str) -> dict:
        test_data: cls = cls.get_by_id(test_data_id, cascade=True)
        return test_data.cascade_to_dict() if test_data else dict()

    @classmethod
    def delete_test_data(cls, test_data_id: str) -> str:
        test_data: cls = cls.get_by_id(test_data_id, cascade=True)
        return test_data.delete(cascade=True) if test_data else str()


TestData.init('test_data')


class Core(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.field_bytes: List[FieldByte] = list()


Core.init()


class Pnr(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.locator: str = str()
        self.key: str = str()
        self.data: str = str()
        self.field_bytes: List[FieldByte] = list()


Pnr.init('pnr')


class Tpfdf(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.key: str = str()
        self.field_bytes: List[FieldByte] = list()


Tpfdf.init('tpfdf')


class File:

    def __init__(self):
        self.macro_name: str = str()
        self.rec_id: int = 0
        self.item_field: str = str()
        self.file_items: List[FileItem] = list()
        self.pool_files: List[PoolFile] = list()
        self.forward_chain_label: str = str()
        self.forward_chain_count: int = 0
        self.field_bytes: List[FieldByte] = list()


class FlatFile(FirestoreDocument, File):

    def __init__(self):
        super().__init__()
        self.fixed_type: int = 0
        self.fixed_ordinal: int = 0


FlatFile.init('flat_files')


class PoolFile(FirestoreDocument, File):

    def __init__(self):
        super().__init__()
        self.index_field: str = str()
        self.index_forward_chain_count: int = 0
        self.index_item_count: int = 0


PoolFile.init('pool_files')


class FileItem(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.field: str = str()
        self.count_field: str = str()
        self.field_bytes: List[FieldByte] = list()


FileItem.init('file_items')


class FieldByte(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.field: str = str()
        self.data: str = str()


FieldByte.init('field_bytes')
