from base64 import b64decode, b64encode
from copy import deepcopy
from itertools import product
from typing import Dict, List, Optional, Union

from firestore_ci import FirestoreDocument

import db.pnr as db_pnr
from assembly.mac2_data_macro import macros, DataMacro
from assembly.seg6_segment import segments
from config import config
from db.test_data_elements import Core, Pnr, Tpfdf, Output, FixedFile
from utils.data_type import Register
from utils.errors import InvalidBaseRegError


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

    def get_field(self, field_name: str, core_variation: int = 0, pnr_variation: int = 0, tpfdf_variation: int = 0):
        output = self.get_output(core_variation, pnr_variation, tpfdf_variation)
        field_data = next(field_data for core in output.cores for field_data in core.field_data
                          if field_data['field'] == field_name)
        return b64decode(field_data['data']).hex().upper()

    def get_output(self, core_variation: int = 0, pnr_variation: int = 0, tpfdf_variation: int = 0) -> Output:
        return next(output for output in self.outputs if output.variation['core'] == core_variation and
                    output.variation['pnr'] == pnr_variation and output.variation['tpfdf'] == tpfdf_variation)

    def get_unsigned_value(self, reg: str) -> int:
        if reg not in self.output.regs:
            raise InvalidBaseRegError
        return self.output.regs[reg] & config.REG_MAX

    def set_field(self, field_name: str, data: Union[bytearray, bytes], variation: int = 0) -> None:
        macro_name = DataMacro.get_label_reference(field_name).name
        field_dict = {'field': field_name, 'data': b64encode(data).decode(), 'variation': variation}
        self.create_field_byte(macro_name, field_dict, persistence=False)

    def yield_variation(self):
        core_variation = max(core.variation for core in self.cores) if self.cores else 0
        pnr_variation = max(pnr.variation for pnr in self.pnr) if self.pnr else 0
        df_variation = max(df.variation for df in self.tpfdf) if self.tpfdf else 0
        for variation in product(range(0, core_variation + 1), range(0, pnr_variation + 1), range(0, df_variation + 1)):
            test_data = deepcopy(self)
            test_data.cores = [core for core in test_data.cores if core.variation == variation[0]]
            test_data.pnr = [pnr for pnr in test_data.pnr if pnr.variation == variation[1]]
            test_data.tpfdf = [df for df in test_data.tpfdf if df.variation == variation[2]]
            test_data.output.variation['core'] = variation[0]
            test_data.output.variation['pnr'] = variation[1]
            test_data.output.variation['tpfdf'] = variation[2]
            yield test_data
        return

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

    def get_header_dict(self) -> dict:
        return {'id': self.id, 'name': self.name, 'seg_name': self.seg_name}

    def create_field_byte(self, macro_name, field_dict, persistence=True) -> dict:
        if not Core.validate_field_dict(macro_name, field_dict):
            return dict()
        if set(field_dict) != {'field', 'data', 'variation'}:
            return dict()
        if not isinstance(field_dict['data'], str) or not field_dict['data']:
            return dict()
        max_variation = max(core.variation for core in self.cores) + 1 if self.cores else 0
        if field_dict['variation'] not in range(max_variation + 1):
            return dict()
        core_dict = {'macro_name': macro_name, 'variation': field_dict['variation']}
        field_dict = field_dict.copy()
        del field_dict['variation']
        core = next((core for core in self.cores if core.macro_name == core_dict['macro_name'] and
                     core.variation == core_dict['variation']), None)
        if not core:
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
        if not isinstance(pnr_dict, dict) or set(pnr_dict) != {'key', 'locator', 'data', 'variation'}:
            return None
        if not (isinstance(pnr_dict['key'], str) and isinstance(pnr_dict['locator'], str) and
                isinstance(pnr_dict['data'], str) and isinstance(pnr_dict['variation'], int)):
            return None
        if db_pnr.Pnr.get_attribute_by_name(pnr_dict['key']) is None:
            return None
        if pnr_dict['locator'] and len(pnr_dict['locator']) != 6:
            return None
        max_variation = max(pnr.variation for pnr in self.pnr) + 1 if self.pnr else 0
        if pnr_dict['variation'] not in range(max_variation + 1):
            return None
        pnr_dict['field_data'] = list()
        pnr_data = pnr_dict['data'].split(',')
        pnr = None
        for data in pnr_data:
            pnr_dict['data'] = data.strip()
            pnr = Pnr.create_from_dict(pnr_dict) if persistence else Pnr.dict_to_doc(pnr_dict)
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

    def create_pnr_field_data(self, pnr_id: str, core_dict: dict, persistence=True) -> Optional[Pnr]:
        pnr = next((pnr for pnr in self.pnr if pnr.id == pnr_id), None)
        if not pnr:
            return None
        if not isinstance(core_dict, dict) or 'macro_name' not in core_dict or 'field_data' not in core_dict:
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
        max_variation = max(df.variation for df in self.tpfdf) + 1 if self.tpfdf else 0
        if df_dict['variation'] not in range(max_variation + 1):
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

    def delete_tpfdf_lrec(self, df_id: str) -> Optional[Tpfdf]:
        lrec: Tpfdf = next((lrec for lrec in self.tpfdf if lrec.id == df_id), None)
        if not lrec:
            return None
        copy_lrec = deepcopy(lrec)
        self.tpfdf.remove(lrec)
        self.save()
        lrec.delete(cascade=True)
        return copy_lrec


TestData.init('test_data')
