from base64 import b64decode, b64encode
from typing import Dict, List, Tuple

from config import config
from firestore.firestore_ci import FirestoreDocument
from utils.data_type import Register
from utils.errors import InvalidBaseRegError


class Output(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.regs: Dict[str, int] = dict()
        self.cores: List[Core] = list()
        self.dumps: List[str] = list()
        self.message: str = str()
        self.last_line: str = str()

    def add_regs(self, reg_list: List[str]) -> None:
        for reg in reg_list:
            if not Register(reg).is_valid():
                raise InvalidBaseRegError
            self.regs[reg] = 0
        return

    def get_unsigned_value(self, reg: str) -> int:
        if reg not in self.regs:
            raise InvalidBaseRegError
        return self.regs[reg] & config.REG_MAX


Output.init()


class TestData(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.cores: List[Core] = list()
        self.pnr: List[Pnr] = list()
        self.tpfdf: List[Tpfdf] = list()
        self.flat_files = list()
        self.errors: List[str] = list()
        self.outputs: List[Output] = [Output()]
        self.partition: str = str()

    @property
    def output(self):
        return self.outputs[0]

    @classmethod
    def create_test_data(cls, test_data_dict: dict) -> str:
        test_data = cls.create_from_dict(test_data_dict)
        return test_data.id

    @classmethod
    def get_test_data_dict(cls, test_data_id: str) -> dict:
        test_data: cls = cls.get_by_id(test_data_id, cascade=True)
        return test_data.cascade_to_dict() if test_data else dict()

    @classmethod
    def get_test_data(cls, test_data_id: str) -> 'TestData':
        return cls.get_by_id(test_data_id, cascade=True)

    @classmethod
    def delete_test_data(cls, test_data_id: str) -> str:
        test_data: cls = cls.get_by_id(test_data_id, cascade=True)
        return test_data.delete(cascade=True) if test_data else str()

    def get_output_dict(self) -> dict:
        return self.outputs[0].cascade_to_dict() if self.outputs[0] else dict()

    def _get_core(self, macro_name: str, output: bool, base_reg) -> 'Core':
        cores = self.outputs[0].cores if output else self.cores
        core: Core = next((core for core in cores if core.macro_name == macro_name), None)
        if not core:
            core = Core()
            core.macro_name = macro_name
            core.base_reg = base_reg
            cores.append(core)
        return core

    def add_core(self, fields: List[str], macro_name: str, output: bool = False,
                 base_reg: str = 'R0') -> Dict[str, 'FieldByte']:
        core = self._get_core(macro_name, output, base_reg)
        core_dict = dict()
        for field in fields:
            field_byte: FieldByte = FieldByte()
            field_byte.field = field
            core.field_bytes.append(field_byte)
            core_dict[field] = field_byte
        return core_dict

    def add_core_with_len(self, fields: List[Tuple[str, int]], macro_name: str,
                          base_reg: str = 'R0') -> Dict[str, 'FieldByte']:
        core = self._get_core(macro_name, True, base_reg)
        core_dict = dict()
        for field, length in fields:
            field_byte: FieldByte = FieldByte()
            field_byte.field = field
            field_byte.length = length
            core.field_bytes.append(field_byte)
            core_dict[field] = field_byte
        return core_dict

    def add_pnr(self, key: str, data: str = None, field_byte_array: Dict[str, bytearray] = None,
                locator: str = None) -> None:
        pnr = Pnr()
        pnr.key = key
        pnr.data = data if data else str()
        pnr.field_bytes = FieldByte.from_dict(field_byte_array) if field_byte_array else list()
        pnr.locator = locator if locator else str()
        self.pnr.append(pnr)

    def add_pnr_from_data(self, data_list: List[str], key: str, locator: str = None) -> None:
        for data in data_list:
            self.add_pnr(key, data=data, locator=locator)
        return

    def add_pnr_from_byte_array(self, byte_array_list: List[Dict[str, bytearray]], key, locator: str = None):
        for byte_array in byte_array_list:
            self.add_pnr(key, field_byte_array=byte_array, locator=locator)
        return

    def add_tpfdf(self, byte_array_list: List[Dict[str, bytearray]], key, macro_name: str):
        for byte_array in byte_array_list:
            lrec = Tpfdf()
            lrec.key = key
            lrec.macro_name = macro_name
            lrec.field_bytes = FieldByte.from_dict(byte_array)
            self.tpfdf.append(lrec)
        return


TestData.init('test_data')


class Core(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.base_reg: str = str()
        self.field_bytes: List[FieldByte] = list()

    def __repr__(self):
        return self.macro_name


Core.init()


class Pnr(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.locator: str = str()
        self.key: str = str()
        self.data: str = str()
        self.field_bytes: List[FieldByte] = list()

    def __repr__(self):
        return f"{self.locator}:{self.key}:{self.data}:{len(self.field_bytes)}"


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
        self.length: int = 0

    def __repr__(self):
        return f"{self.field}:{self.hex}"

    @property
    def hex(self):
        return b64decode(self.data).hex().upper()

    @classmethod
    def from_dict(cls, field_byte_array: Dict[str, bytearray]) -> List['FieldByte']:
        field_bytes: List[cls] = list()
        for field, byte_array in field_byte_array.items():
            field_byte = cls()
            field_byte.field = field
            field_byte.data = b64encode(byte_array).decode()
            field_bytes.append(field_byte)
        return field_bytes

    @classmethod
    def to_dict(cls, field_bytes: List['FieldByte']) -> Dict[str, bytearray]:
        return {field_byte.field.upper(): bytearray(b64decode(field_byte.data)) for field_byte in field_bytes
                if field_byte.data}


FieldByte.init('field_bytes')
