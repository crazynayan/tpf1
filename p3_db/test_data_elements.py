from typing import List, Dict, Union

from firestore_ci import FirestoreDocument

import p3_db.pnr as db_pnr
from config import config
from p1_utils.data_type import Register
from p2_assembly.mac2_data_macro import macros
from p2_assembly.seg6_segment import segments


class Core(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.base_reg: str = str()
        self.variation: int = 0
        self.field_data: List[dict] = list()
        self.variation_name: str = str()

    def __repr__(self):
        return self.macro_name

    @staticmethod
    def validate_field_dict(macro_name: str, field_dict: dict) -> bool:
        if not isinstance(field_dict, dict):
            return False
        if 'field' not in field_dict or not field_dict['field']:
            return False
        if macro_name not in macros:
            return False
        macros[macro_name].load()
        if not macros[macro_name].check(field_dict['field']):
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
        self.variation_name: str = str()

    def __repr__(self):
        return f"{self.locator}:{self.variation}:{self.key}:{self.data}:{len(self.field_data)}"

    @classmethod
    def validate(cls, pnr_dict: dict) -> bool:
        if not isinstance(pnr_dict, dict) or not pnr_dict:
            return False
        template = cls().__dict__
        if not set(pnr_dict).issubset(template):
            return False
        if not all(isinstance(value, type(template[field])) for field, value in pnr_dict.items()):
            return False
        if not {'locator', 'key', 'variation', 'variation_name'}.issubset(pnr_dict):
            return False
        if pnr_dict['locator'] and len(pnr_dict['locator']) != 6:
            return False
        if db_pnr.Pnr.get_attribute_by_name(pnr_dict['key']) is None:
            return False
        return True


Pnr.init('pnr')


class Tpfdf(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.key: str = str()
        self.field_data: list = list()
        self.variation: int = 0
        self.variation_name: str = str()


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
        self.variation: Dict[str, int] = {'core': 0, 'pnr': 0, 'tpfdf': 0, 'file': 0}
        self.variation_name: Dict[str, str] = {'core': str(), 'pnr': str(), 'tpfdf': str(), 'file': str()}

    def create_field_byte(self, macro_name: str, field_dict: dict, persistence=True) -> dict:
        if not Core.validate_field_dict(macro_name, field_dict):
            return dict()
        if set(field_dict) != {'field', 'length', 'base_reg'}:
            return dict()
        if not isinstance(field_dict['length'], int) or field_dict['length'] < 0:
            return dict()
        if field_dict['base_reg'] and not Register(field_dict['base_reg']).is_valid():
            return dict()
        core_dict = {'macro_name': macro_name, 'base_reg': field_dict['base_reg']}
        field_dict = field_dict.copy()
        del field_dict['base_reg']
        core_dict['base_reg'] = core_dict['base_reg'] if core_dict['base_reg'] != 'R0' else str()
        if not core_dict['base_reg'] and macro_name not in config.DEFAULT_MACROS:
            return dict()
        if core_dict['base_reg'] and macro_name in config.DEFAULT_MACROS:
            return dict()
        field_dict['length'] = field_dict['length'] if 'length' in field_dict and field_dict['length'] \
            else macros[macro_name].evaluate(f"L'{field_dict['field']}")
        core = next((core for core in self.cores if core.macro_name == core_dict['macro_name']), None)
        if core:
            core.base_reg = core_dict['base_reg']
        else:
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
        self.file_items: List[FileItem] = list()
        self.pool_files: List[PoolFile] = list()
        self.forward_chain_label: str = str()
        self.forward_chain_count: int = 0
        self.field_data: list = list()

    @classmethod
    def validate(cls, file_dict: dict) -> bool:
        template = cls().__dict__
        if not isinstance(file_dict, dict) or not file_dict:
            return False
        if not set(file_dict).issubset(template):
            return False
        if not all(isinstance(value, type(template[field])) for field, value in file_dict.items()):
            return False
        if not {'macro_name', 'rec_id'}.issubset(file_dict):
            return False
        file = cls.dict_to_doc(file_dict, cascade=False)
        if file.rec_id <= 0:
            return False
        if file.macro_name not in macros:
            return False
        macro = macros[file.macro_name]
        macro.load()
        if not all(FileItem.validate(file_item) for file_item in file.file_items):
            return False
        if not all(PoolFile.validate(pool_file) for pool_file in file.pool_files):
            return False
        if file.forward_chain_count or file.forward_chain_label:
            if not macro.check(file.forward_chain_label):
                return False
            if file.forward_chain_count < 0:
                return False
        for field_value in file.field_data:
            if not isinstance(field_value, dict):
                return False
            if set(field_value) != {'field', 'data'}:
                return False
            if not macro.check(field_value['field']):
                return False
            if not isinstance(field_value['data'], str):
                return False
        return True


class FixedFile(FlatFile):

    def __init__(self):
        super().__init__()
        self.fixed_type: int = 0
        self.fixed_ordinal: int = 0
        self.variation: int = 0
        self.variation_name: str = str()

    def __repr__(self):
        return f"{self.rec_id:04X}:{self.macro_name}:{self.fixed_type}:{self.fixed_ordinal}"

    @classmethod
    def validate(cls, file_dict: dict) -> bool:
        if not super().validate(file_dict):
            return False
        if not {'variation', 'fixed_type', 'fixed_ordinal'}.issubset(file_dict):
            return False
        if file_dict['fixed_type'] < 0 or file_dict['fixed_ordinal'] < 0 or file_dict['variation'] < 0:
            return False
        return True


FixedFile.init('fixed_files')


class PoolFile(FlatFile):

    def __init__(self):
        super().__init__()
        self.index_field: str = str()
        self.index_macro_name: str = str()

    def __repr__(self):
        return f"{self.rec_id:04X}:{self.macro_name}:{self.index_field}"

    @classmethod
    def validate(cls, file_dict: dict) -> bool:
        if not super().validate(file_dict):
            return False
        if not {'index_field', 'index_macro_name'}.issubset(file_dict):
            return False
        file = cls.dict_to_doc(file_dict, cascade=False)
        if file.index_macro_name not in macros:
            return False
        macro = macros[file.index_macro_name]
        macro.load()
        if not macro.check(file.index_field):
            return False
        return True


PoolFile.init('pool_files')


class FileItem(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.macro_name: str = str()
        self.field: str = str()
        self.count_field: str = str()
        self.field_data: list = list()

    def __repr__(self):
        return f"{self.field}:{self.field_data}"

    @classmethod
    def validate(cls, item_dict: dict) -> bool:
        template = cls().__dict__
        if not isinstance(item_dict, dict) or not item_dict:
            return False
        if not set(item_dict).issubset(template):
            return False
        if not all(isinstance(value, type(template[field])) for field, value in item_dict.items()):
            return False
        if not {'field', 'macro_name', 'field_data'}.issubset(item_dict):
            return False
        item = cls.dict_to_doc(item_dict, cascade=False)
        if item.macro_name not in macros:
            return False
        macro = macros[item.macro_name]
        macro.load()
        if not macro.check(item.field):
            return False
        if item.count_field and not macro.check(item.count_field):
            return False
        if not item.field_data:
            return False
        for field_value in item.field_data:
            if not isinstance(field_value, dict):
                return False
            if set(field_value) != {'field', 'data'}:
                return False
            if not macro.check(field_value['field']):
                return False
            if not isinstance(field_value['data'], str):
                return False
        return True


FileItem.init('file_items')
