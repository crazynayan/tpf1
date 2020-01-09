from copy import deepcopy
from typing import Dict, List, Union, Optional

from firestore_ci import FirestoreDocument

import db.pnr as db_pnr
from assembly.mac2_data_macro import macros, DataMacro
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
        if not header:
            return False
        if 'name' not in header or 'seg_name' not in header:
            return False
        header['seg_name'] = header['seg_name'].upper()
        if header['seg_name'] not in segments or not header['name']:
            return False
        if len(header) != 2:
            return False
        return True

    @classmethod
    def create_test_data(cls, header: dict) -> Optional['TestData']:
        if not cls._validate_header(header):
            return None
        if cls.objects.filter_by(name=header['name']).first() is not None:
            return None
        test_data = cls.create_from_dict(header)
        return test_data

    def rename(self, header: dict) -> bool:
        if not self._validate_header(header):
            return False
        self.name = header['name']
        self.seg_name = header['seg_name']
        return self.save()

    def copy(self) -> Optional['TestData']:
        if self.name.endswith(config.COPY_SUFFIX):
            return None
        name_copy = f"{self.name}{config.COPY_SUFFIX}"
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

    def create_field_byte(self, macro_name, field_dict, persistence=True) -> dict:
        if not Core.validate_field_dict(macro_name, field_dict):
            return dict()
        if 'data' not in field_dict:
            return dict()
        if 'base_reg' in field_dict:
            return dict()
        if 'length' in field_dict:
            return dict()
        core = next((core for core in self.cores if core.macro_name == macro_name), None)
        if not core:
            core: Core = Core.create_from_dict({'macro_name': macro_name}) if persistence \
                else Core.dict_to_doc({'macro_name': macro_name})
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

    def add_reg(self, reg_dict: dict) -> bool:
        if 'reg' not in reg_dict or not Register(reg_dict['reg']).is_valid():
            return False
        if 'value' not in reg_dict or not isinstance(reg_dict['value'], int):
            return False
        if len(reg_dict) != 2:
            return False
        if reg_dict['value'] < -0x80000000 or reg_dict['value'] > 0x7FFFFFFF:
            return False
        self.regs[reg_dict['reg']] = reg_dict['value']
        self.save()
        return True

    def delete_reg(self, reg: str) -> bool:
        if not Register(reg).is_valid():
            return False
        if reg not in self.regs:
            return False
        del self.regs[reg]
        self.save()
        return True

    def create_pnr_element(self, pnr_dict: dict, persistence: bool = True) -> Optional[Pnr]:
        if 'key' not in pnr_dict:
            return None
        if db_pnr.Pnr.get_attribute_by_name(pnr_dict['key']) is None:
            return None
        pnr_dict['locator'] = pnr_dict['locator'] if 'locator' in pnr_dict else str()
        if pnr_dict['locator'] and len(pnr_dict['locator']) != 6:
            return None
        data_list = pnr_dict['data'] if 'data' in pnr_dict else str()
        if 'field_data' in pnr_dict:
            return None
        pnr_dict['field_data'] = list()
        pnr_data = list()
        for data in data_list.split(','):
            data = data.strip()
            pnr = next((pnr for pnr in self.pnr if pnr.key == pnr_dict['key'] and pnr.locator == pnr_dict['locator']
                        and pnr.data == data and pnr.field_data == list()), None)
            if pnr is not None:
                return None
            pnr_data.append(data)
        pnr = None
        for data in pnr_data:
            pnr_dict['data'] = data
            pnr = Pnr.create_from_dict(pnr_dict) if persistence else Pnr.dict_to_doc(pnr_dict, cascade=True)
            self.pnr.append(pnr)
            if persistence:
                self.save()
        return pnr

    def delete_pnr_element(self, pnr_id: str) -> Optional[Pnr]:
        pnr: Pnr = next((pnr for pnr in self.pnr if pnr.id == pnr_id), None)
        if not pnr:
            return None
        copy_pnr = deepcopy(pnr)
        self.pnr.remove(pnr)
        self.save()
        pnr.delete(cascade=True)
        return copy_pnr

    def create_pnr_field_bytes(self, pnr_id: str, core_dict: dict, persistence=True) -> Optional[Pnr]:
        pnr = next((pnr for pnr in self.pnr if pnr.id == pnr_id), None)
        if not pnr:
            return None
        if 'macro_name' not in core_dict or 'field_data' not in core_dict:
            return None
        if core_dict['macro_name'] not in macros:
            return None
        macro: DataMacro = macros[core_dict['macro_name']]
        macro.load()
        if not isinstance(core_dict['field_data'], dict):
            return None
        for field, value in core_dict['field_data'].items():
            if not macro.check(field):
                return None
            if not isinstance(value, str):
                return None
        for field, value in core_dict['field_data'].items():
            field_dict = {'field': field, 'data': value}
            field_byte = next((field_byte for field_byte in pnr.field_data
                               if field_byte['field'] == field_dict['field']), None)
            if not field_byte:
                field_byte = field_dict
                pnr.field_data.append(field_byte)
            else:
                field_byte['data'] = field_dict['data']
        pnr.data = str()
        if persistence:
            pnr.save()
        return pnr

    def create_tpfdf_lrec(self, df_dict: dict, persistence=True) -> Optional[Tpfdf]:
        if set(df_dict) != {'key', 'field_data', 'macro_name', 'variation'}:
            return None
        if not isinstance(df_dict['key'], str) or len(df_dict['key']) != 2 or not df_dict['key'].isalnum():
            return None
        if df_dict['macro_name'] not in macros:
            return None
        df_macro = macros[df_dict['macro_name']]
        df_macro.load()
        if not isinstance(df_dict['field_data'], dict) or not df_dict['field_data']:
            return None
        if not isinstance(df_dict['variation'], int):
            return None
        for field, value in df_dict['field_data'].items():
            if not df_macro.check(field):
                return None
            if not isinstance(value, str):
                return None
        df_dict = df_dict.copy()
        df_dict['key'] = df_dict['key'].upper()
        df_dict['field_data'] = [{'field': field, 'data': value} for field, value in df_dict['field_data'].items()]
        df_lrec = next((lrec for lrec in self.tpfdf if lrec.field_data == df_dict['field_data'] and
                        lrec.macro_name == df_dict['macro_name'] and lrec.key == df_dict['key'] and
                        lrec.variation == df_dict['variation']), None)
        if df_lrec:
            return None
        df_doc = Tpfdf.create_from_dict(df_dict) if persistence else Tpfdf.dict_to_doc(df_dict)
        self.tpfdf.append(df_doc)
        if persistence:
            self.save()
        return df_doc


TestData.init('test_data')


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
