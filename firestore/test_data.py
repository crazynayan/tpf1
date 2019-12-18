from base64 import b64decode, b64encode
from typing import Dict, List, Tuple, Union, Optional

from firestore_ci import FirestoreDocument

from assembly.mac2_data_macro import macros, DataMacro
from assembly.seg6_segment import segments
from config import config
from utils.data_type import Register
from utils.errors import InvalidBaseRegError, FileItemSpecificationError, PoolFileSpecificationError


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


class Core(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.base_reg: str = str()
        self.field_bytes: List[FieldByte] = list()

    def __repr__(self):
        return self.macro_name

    def create_field_byte(self, macro_name: str, field_dict: dict) -> Optional[FieldByte]:
        if 'field' not in field_dict or not field_dict['field']:
            return None
        if macro_name not in macros:
            return None
        macros[macro_name].load()
        if not macros[macro_name].check(field_dict['field']):
            return None
        field_dict['length'] = field_dict['length'] if 'length' in field_dict and field_dict['length'] \
            else macros[macro_name].evaluate(f"L'{field_dict['field']}")
        field_dict['data'] = field_dict['data'] if 'data' in field_dict else str()
        field_byte = next((field_byte for field_byte in self.field_bytes if field_byte.field == field_dict['field']),
                          None)
        if not field_byte:
            field_byte = FieldByte.create_from_dict(field_dict)
            self.field_bytes.append(field_byte)
            self.save()
        else:
            field_byte.length = field_dict['length']
            field_byte.data = field_dict['data']
            field_byte.save()
        return field_byte

    def delete_field_byte(self, field_name: str) -> str:
        field_byte = next((field_byte for field_byte in self.field_bytes if field_byte.field == field_name), None)
        if not field_byte:
            return str()
        self.field_bytes.remove(field_byte)
        self.save()
        return field_byte.delete()


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

    def create_field_byte(self, field_dict: dict) -> Optional[FieldByte]:
        if 'field' not in field_dict or not field_dict['field']:
            return None
        field_dict['data'] = field_dict['data'] if 'data' in field_dict else str()
        field_byte = next((field_byte for field_byte in self.field_bytes if field_byte.field == field_dict['field']),
                          None)
        if not field_byte:
            field_byte = FieldByte.create_from_dict(field_dict)
            self.field_bytes.append(field_byte)
            self.save()
        else:
            field_byte.data = field_dict['data']
            field_byte.save()
        return field_byte

    def create_field_bytes(self, core_dict: dict) -> str:
        if 'macro_name' not in core_dict or 'field_bytes' not in core_dict:
            return str()
        if core_dict['macro_name'] not in macros:
            return str()
        macro: DataMacro = macros[core_dict['macro_name']]
        macro.load()
        for field, value in core_dict['field_bytes'].items():
            if not macro.check(field):
                return str()
            if not self.create_field_byte({'field': field, 'data': value}):
                return str()
        return self.id


Pnr.init('pnr')


class Output(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.regs: Dict[str, int] = dict()
        self.reg_pointers: Dict[str, Union[str, int]] = dict()
        self.cores: List[Core] = list()
        self.dumps: List[str] = list()
        self.messages: List[str] = list()
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

    def add_all_regs(self) -> None:
        for reg in config.REG:
            self.regs[reg] = 0
        return

    def add_all_reg_pointers(self, length) -> None:
        for reg in config.REG:
            self.reg_pointers[reg] = length

    def create_field_byte(self, macro_name, field_dict) -> Optional[FieldByte]:
        if macro_name not in macros:
            return None
        base_reg = field_dict['base_reg'] if 'base_reg' in field_dict and \
                                             Register(field_dict['base_reg']).is_valid() and \
                                             field_dict['base_reg'] != 'R0' else str()
        core = next((core for core in self.cores if core.macro_name == macro_name), None)
        if not core:
            core: Core = Core.create_from_dict({'macro_name': macro_name, 'base_reg': base_reg})
            self.cores.append(core)
            self.save()
        elif core.base_reg != base_reg:
            core.base_reg = base_reg
            core.save()
        return core.create_field_byte(macro_name, field_dict)

    def delete_core(self, macro_name: str) -> str:
        core: Core = next((core for core in self.cores if core.macro_name == macro_name), None)
        if not core:
            return str()
        self.cores.remove(core)
        self.save()
        return core.delete(cascade=True)

    def create_regs(self, reg_dict: dict) -> dict:
        if 'regs' not in reg_dict:
            return dict()
        self.regs = dict()
        try:
            self.add_regs(reg_dict['regs'])
        except InvalidBaseRegError:
            return dict()
        self.save()
        return self.regs

    def delete_regs(self) -> None:
        self.regs = dict()
        self.save()


Output.init()


class TestData(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name: str = ''
        self.seg_name: str = ''
        self.cores: List[Core] = list()
        self.pnr: List[Pnr] = list()
        self.tpfdf: List[Tpfdf] = list()
        self.fixed_files: List[FixedFile] = list()
        self.errors: List[str] = list()
        self.outputs: List[Output] = [Output()]
        self.partition: str = str()
        self.regs: Dict[str, int] = dict()

    @property
    def output(self):
        return self.outputs[0]

    @classmethod
    def _validate_header(cls, header: dict) -> bool:
        if 'name' not in header or 'seg_name' not in header:
            return False
        if header['seg_name'] not in segments:
            return False
        if len(header) != 2:
            return False
        if cls.objects.filter_by(name=header['name']).first() is not None:
            return False
        return True

    @classmethod
    def create_test_data(cls, header: dict) -> str:
        if not cls._validate_header(header):
            return str()
        test_data = cls.create_from_dict(header)
        return test_data.id

    def rename(self, header: dict) -> str:
        if not self._validate_header(header):
            return str()
        self.name = header['name']
        self.seg_name = header['seg_name']
        self.save()
        return self.id

    def copy(self) -> Optional['TestData']:
        name_copy = f"{self.name} - Copy"
        if self.objects.filter_by(name=name_copy).first() is not None:
            return None
        test_data_dict = self.cascade_to_dict()
        test_data_dict['name'] = name_copy
        return self.create_from_dict(test_data_dict)

    @classmethod
    def get_all(cls) -> List['TestData']:
        return cls.objects.order_by('name').get()

    @classmethod
    def get_test_data_by_name(cls, name: str) -> Optional['TestData']:
        return cls.objects.filter_by(name=name).first()

    @classmethod
    def get_test_data(cls, test_data_id: str) -> 'TestData':
        return cls.get_by_id(test_data_id, cascade=True)

    @classmethod
    def delete_test_data(cls, test_data_id: str) -> str:
        test_data: cls = cls.get_by_id(test_data_id, cascade=True)
        return test_data.delete(cascade=True) if test_data else str()

    def get_output_dict(self) -> dict:
        output_dict = self.get_header_dict()
        output_dict['outputs'] = self.outputs[0].cascade_to_dict() if self.outputs[0] else dict()
        return output_dict

    def get_header_dict(self) -> dict:
        return {'id': self.id, 'name': self.name, 'seg_name': self.seg_name}

    def add_all_regs(self) -> Dict[str, int]:
        for reg in config.REG:
            if reg in ['R8', 'R9']:
                continue
            self.regs[reg] = 0
        return self.regs

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

    def add_file(self, fixed_rec_id: int, fixed_file_type: int, fixed_file_ordinal: int, fixed_macro_name: str,
                 fixed_forward_chain_label: str = str(),
                 fixed_field_bytes: Dict[str, bytearray] = None,
                 fixed_item_field: str = str(),
                 fixed_item_count_field: str = str(),
                 fixed_item_position: int = 0,
                 fixed_item_forward_chain_count: int = 0,
                 fixed_item_field_bytes: Dict[str, bytearray] = None,
                 pool_rec_id: int = 0,
                 pool_macro_name: str = str(),
                 pool_index_field: str = str(),
                 pool_index_count: int = 0,
                 pool_index_forward_chain_count: int = 0,
                 pool_forward_chain_label: str = str(),
                 pool_field_bytes: Dict[str, bytearray] = None,
                 pool_item_field: str = str(),
                 pool_item_count_field: str = str(),
                 pool_item_position: int = 0,
                 pool_item_forward_chain_count: int = 0,
                 pool_item_field_bytes: Dict[str, bytearray] = None,
                 ) -> None:
        fixed_file = self._get_or_create_fixed_file(fixed_rec_id, fixed_file_type, fixed_file_ordinal, fixed_macro_name)
        fixed_file.forward_chain_label = fixed_forward_chain_label
        fixed_file.forward_chain_count = fixed_item_forward_chain_count
        if fixed_item_forward_chain_count and not fixed_forward_chain_label:
            raise PoolFileSpecificationError
        if fixed_field_bytes:
            fixed_file.field_bytes = FieldByte.from_dict(fixed_field_bytes)
        if fixed_item_field:
            if not fixed_item_field_bytes:
                raise FileItemSpecificationError
            item = FileItem()
            fixed_file.file_items.append(item)
            item.field = fixed_item_field
            item.position = fixed_item_position
            item.count_field = fixed_item_count_field
            item.field_bytes = FieldByte.from_dict(fixed_item_field_bytes)
        if pool_rec_id or pool_macro_name or pool_index_field:
            if not (pool_rec_id and pool_macro_name and pool_index_field):
                raise PoolFileSpecificationError
            pool = PoolFile()
            fixed_file.pool_files.append(pool)
            pool.rec_id = pool_rec_id
            pool.macro_name = pool_macro_name
            pool.index_field = pool_index_field
            pool.index_count = pool_index_count
            pool.index_forward_chain_count = pool_index_forward_chain_count
            pool.forward_chain_label = pool_forward_chain_label
            pool.forward_chain_count = pool_item_forward_chain_count
            if pool_item_forward_chain_count and not pool_forward_chain_label:
                raise PoolFileSpecificationError
            if pool_field_bytes:
                pool.field_bytes = FieldByte.from_dict(pool_field_bytes)
            if pool_item_field:
                if not pool_item_field_bytes:
                    raise FileItemSpecificationError
                item = FileItem()
                pool.file_items.append(item)
                item.field = pool_item_field
                item.position = pool_item_position
                item.count_field = pool_item_count_field
                item.field_bytes = FieldByte.from_dict(pool_item_field_bytes)
        return

    def _get_or_create_fixed_file(self, rec_id, file_type, file_ordinal, macro_name) -> 'FixedFile':
        fixed_file: FixedFile = next((file for file in self.fixed_files
                                      if file.rec_id == rec_id
                                      and file.fixed_type == file_type
                                      and file.fixed_ordinal == file_ordinal
                                      and file.macro_name == macro_name), None)
        if not fixed_file:
            fixed_file: FixedFile = FixedFile()
            fixed_file.rec_id = rec_id
            fixed_file.fixed_type = file_type
            fixed_file.fixed_ordinal = file_ordinal
            fixed_file.macro_name = macro_name
            self.fixed_files.append(fixed_file)
        return fixed_file

    def create_field_byte(self, macro_name, field_dict) -> Optional[FieldByte]:
        if macro_name not in macros:
            return None
        core = next((core for core in self.cores if core.macro_name == macro_name), None)
        if not core:
            core: Core = Core.create_from_dict({'macro_name': macro_name})
            self.cores.append(core)
            self.save()
        return core.create_field_byte(macro_name, field_dict)

    def delete_core(self, macro_name: str) -> str:
        core: Core = next((core for core in self.cores if core.macro_name == macro_name), None)
        if not core:
            return str()
        self.cores.remove(core)
        self.save()
        return core.delete(cascade=True)

    def add_reg(self, reg_dict: dict) -> dict:
        if 'reg' not in reg_dict or not Register(reg_dict['reg']).is_valid():
            return dict()
        if 'value' not in reg_dict or not isinstance(reg_dict['value'], int):
            return dict()
        self.regs[reg_dict['reg']] = reg_dict['value']
        self.save()
        return self.regs

    def delete_reg(self, reg: str) -> dict:
        if not Register(reg).is_valid():
            return dict()
        self.regs.pop(reg, None)
        self.save()
        return self.regs

    def create_pnr_element(self, pnr_dict: dict) -> Optional[Pnr]:
        if 'key' not in pnr_dict:
            return None
        pnr_dict['locator'] = pnr_dict['locator'] if 'locator' in pnr_dict else str()
        if pnr_dict['locator'] and len(pnr_dict['locator']) != 6:
            return None
        data_list = pnr_dict['data'] if 'data' in pnr_dict else str()
        pnr_dict['field_bytes'] = list()
        pnr = None
        for data in data_list.split(','):
            pnr_dict['data'] = data.strip()
            pnr = next((pnr for pnr in self.pnr if pnr.key == pnr_dict['key'] and pnr.locator == pnr_dict['locator']
                        and pnr.data == data and pnr.field_bytes == list()), None)
            if not pnr:
                pnr = Pnr.create_from_dict(pnr_dict)
                self.pnr.append(pnr)
                self.save()
        return pnr

    def delete_pnr_element(self, pnr_id: str) -> str:
        pnr: Pnr = next((pnr for pnr in self.pnr if pnr.id == pnr_id), None)
        if not pnr:
            return str()
        self.pnr.remove(pnr)
        self.save()
        return pnr.delete(cascade=True)


TestData.init('test_data')


class Tpfdf(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.key: str = str()
        self.field_bytes: List[FieldByte] = list()


Tpfdf.init('tpfdf')


class FlatFile(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.rec_id: int = 0
        self.item_field: str = str()
        self.file_items: List[FileItem] = list()
        self.pool_files: List[PoolFile] = list()
        self.forward_chain_label: str = str()
        self.forward_chain_count: int = 0
        self.field_bytes: List[FieldByte] = list()


class FixedFile(FlatFile):

    def __init__(self):
        super().__init__()
        self.fixed_type: int = 0
        self.fixed_ordinal: int = 0

    def __repr__(self):
        return f"{self.rec_id:04X}:{self.macro_name}:{self.fixed_type}:{self.fixed_ordinal}"


FixedFile.init('fixed_files')


class PoolFile(FlatFile):

    def __init__(self):
        super().__init__()
        self.index_field: str = str()
        self.index_forward_chain_count: int = 0
        self.index_item_count: int = 0

    def __repr__(self):
        return f"{self.rec_id:04X}:{self.macro_name}:{self.index_field}"


PoolFile.init('pool_files')


class FileItem(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.field: str = str()
        self.count_field: str = str()
        self.position: int = 0
        self.field_bytes: List[FieldByte] = list()

    def __repr__(self):
        return f"{self.field}:{self.field_bytes}"


FileItem.init('file_items')
