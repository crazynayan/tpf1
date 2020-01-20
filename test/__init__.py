import random
import string
from base64 import b64encode, b64decode
from typing import Dict, List, Union

from assembly.mac2_data_macro import DataMacro
from config import config
from db.test_data import TestData
from db.test_data_elements import Pnr, Output, FixedFile, PoolFile, FileItem
from utils.data_type import Register
from utils.errors import PoolFileSpecificationError, FileItemSpecificationError, InvalidBaseRegError


class OutputUTS(Output):

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

    def add_all_reg_pointers(self, length: int) -> None:
        for reg in config.REG:
            self.reg_pointers[reg] = length


class TestDataUTS(TestData):

    def __init__(self):
        super().__init__()
        self.outputs = [OutputUTS()]

    def add_all_regs(self) -> Dict[str, int]:
        for reg in config.REG:
            if reg in ['R8', 'R9']:
                continue
            self.regs[reg] = 0
        return self.regs

    def add_fields(self, fields: List[Union[str, tuple]], macro_name: str, base_reg: str = None) -> None:
        field_dict = dict()
        for field in fields:
            field, length = field if isinstance(field, tuple) else (field, 0)
            field_dict['field'] = field
            field_dict['base_reg'] = base_reg if base_reg else str()
            field_dict['length'] = length
            self.output.create_field_byte(macro_name, field_dict, persistence=False)
        return

    def add_pnr_element(self, data_list: List[str], key: str, locator: str = None, variation: int = 0) -> Pnr:
        pnr_dict = {'key': key, 'data': ','.join(data_list), 'variation': variation, 'locator': str()}
        if locator:
            pnr_dict['locator'] = locator
        pnr = self.create_pnr_element(pnr_dict, persistence=False)
        pnr.set_id(''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=20)))
        return pnr

    def add_pnr_field_data(self, field_data_list: List[Dict[str, str]], key, locator: str = None,
                           variation: int = 0) -> None:
        core_dict = {'macro_name': DataMacro.get_label_reference(next(iter(field_data_list[0].keys()))).name}
        for field_data in field_data_list:
            core_dict['field_data'] = field_data
            pnr = self.add_pnr_element(list(), key, locator, variation)
            self.create_pnr_field_bytes(pnr.id, core_dict, persistence=False)
        return

    def add_tpfdf(self, field_data_list: List[Dict[str, str]], key: str, macro_name: str, variation: int = 0):
        df_dict = {'key': key, 'macro_name': macro_name, 'variation': variation}
        for field_data in field_data_list:
            df_dict['field_data'] = field_data
            self.create_tpfdf_lrec(df_dict, persistence=False)
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

    @staticmethod
    def hex(data: str):
        return b64decode(data).hex().upper()


class FieldByte:

    def __init__(self):
        super().__init__()
        self.field: str = str()
        self.data: str = str()
        self.length: int = 0

    def __repr__(self):
        return f"{self.field}"

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
