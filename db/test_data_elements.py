from typing import List, Dict, Union

from firestore_ci import FirestoreDocument

from assembly.mac2_data_macro import macros
from assembly.seg6_segment import segments
from config import config
from utils.data_type import Register


class Core(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.base_reg: str = str()
        self.variation: int = 0
        self.field_data: List[dict] = list()

    def __repr__(self):
        return self.macro_name

    @staticmethod
    def validate_field_dict(macro_name: str, field_dict: dict) -> bool:
        if 'field' not in field_dict or not field_dict['field']:
            return False
        if macro_name not in macros:
            return False
        macros[macro_name].load()
        if not macros[macro_name].check(field_dict['field']):
            return False
        if 'length' in field_dict and not isinstance(field_dict['length'], int):
            return False
        if 'data' in field_dict and not (isinstance(field_dict['data'], str) and field_dict['data']):
            return False
        return True

    def create_field_byte(self, field_dict: dict, persistence: bool) -> dict:
        field_byte = next((field_byte for field_byte in self.field_data if field_byte['field'] == field_dict['field']),
                          None)
        if not field_byte:
            field_byte = field_dict.copy()
            self.field_data.append(field_byte)
        else:
            if 'length' in field_dict:
                field_byte['length'] = field_dict['length']
            if 'data' in field_dict:
                field_byte['data'] = field_dict['data']
        if persistence:
            self.save()
        return field_byte

    def delete_field_byte(self, field_name: str) -> dict:
        field_byte = next((field_byte for field_byte in self.field_data if field_byte['field'] == field_name), None)
        if not field_byte:
            return dict()
        self.field_data.remove(field_byte)
        self.save()
        return field_byte


Core.init()


class Pnr(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.locator: str = str()
        self.key: str = str()
        self.data: str = str()
        self.field_data: List[dict] = list()
        self.variation: int = 0

    def __repr__(self):
        return f"{self.locator}:{self.variation}:{self.key}:{self.data}:{len(self.field_data)}"


Pnr.init('pnr')


class Tpfdf(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.key: str = str()
        self.field_data: list = list()
        self.variation: int = 0


Tpfdf.init('tpfdf')


class Output(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.regs: Dict[str, int] = dict()
        self.reg_pointers: Dict[str, Union[str, int]] = dict()
        self.cores: List[Core] = list()
        self.dumps: List[str] = list()
        self.messages: List[str] = list()
        self.last_line: str = str()
        self.debug: List[str] = list()

    def create_field_byte(self, macro_name: str, field_dict: dict, persistence=True) -> dict:
        if not Core.validate_field_dict(macro_name, field_dict):
            return dict()
        if 'data' in field_dict:
            return dict()
        base_reg = str()
        if 'base_reg' in field_dict:
            base_reg = field_dict['base_reg'] if field_dict['base_reg'] != 'R0' else str()
            field_dict = field_dict.copy()
            del field_dict['base_reg']
        if not base_reg and macro_name not in config.DEFAULT_MACROS:
            return dict()
        if base_reg and macro_name in config.DEFAULT_MACROS:
            return dict()
        if base_reg and not Register(base_reg).is_valid():
            return dict()
        field_dict['length'] = field_dict['length'] if 'length' in field_dict and field_dict['length'] \
            else macros[macro_name].evaluate(f"L'{field_dict['field']}")
        core = next((core for core in self.cores if core.macro_name == macro_name), None)
        if core:
            core.base_reg = base_reg
        else:
            core_dict = {'macro_name': macro_name, 'base_reg': base_reg}
            core: Core = Core.create_from_dict(core_dict) if persistence else Core.dict_to_doc(core_dict)
            self.cores.append(core)
            if persistence:
                self.save()
        field_byte = core.create_field_byte(field_dict, persistence)
        return field_byte

    def delete_field_byte(self, macro_name: str, field_name: str) -> dict:
        core: Core = next((core for core in self.cores if core.macro_name == macro_name), None)
        if not core:
            return dict()
        field_byte = core.delete_field_byte(field_name)
        if not field_byte:
            return dict()
        if not core.field_data:
            self.cores.remove(core)
            self.save()
            core.delete(cascade=True)
        return field_byte

    def create_regs(self, reg_dict: dict) -> bool:
        if 'regs' not in reg_dict:
            return False
        self.regs = dict()
        for reg in reg_dict['regs']:
            if not Register(reg).is_valid():
                return False
            self.regs[reg] = 0
        self.save()
        return True

    def add_debug_seg(self, debug: dict, persistence=True) -> list:
        if 'traces' not in debug or not debug['traces'] or not isinstance(debug['traces'], list):
            return list()
        for seg in debug['traces']:
            if seg.upper() not in segments:
                return list()
        for seg in debug['traces']:
            self.debug.append(seg.upper())
        if persistence:
            self.save()
        return self.debug

    def delete_debug_seg(self, seg_name: str, persistence=True) -> str:
        seg_name = seg_name.upper()
        if not seg_name or seg_name not in self.debug:
            return str()
        self.debug.remove(seg_name)
        if persistence:
            self.save()
        return seg_name


Output.init()


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
        self.field_bytes: list = list()


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
        self.field_bytes: list = list()

    def __repr__(self):
        return f"{self.field}:{self.field_bytes}"


FileItem.init('file_items')
