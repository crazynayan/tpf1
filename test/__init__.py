import random
import string
from base64 import b64encode
from typing import Dict, List, Union

from assembly.mac2_data_macro import DataMacro
from config import config
from db.test_data import TestData
from db.test_data_elements import Pnr, FixedFile, PoolFile, FileItem
from utils.errors import PoolFileSpecificationError, FileItemSpecificationError


class TestDataUTS(TestData):

    def add_all_regs(self) -> None:
        for reg in config.REG:
            if reg in ['R8', 'R9']:
                continue
            self.output.regs[reg] = 0
        return

    def add_all_reg_pointers(self, length: int) -> None:
        for reg in config.REG:
            self.output.reg_pointers[reg] = length

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
            self.create_pnr_field_data(pnr.id, core_dict, persistence=False)
        return

    def add_tpfdf(self, field_data_list: List[Dict[str, str]], key: str, macro_name: str, variation: int = 0):
        df_dict = {'key': key, 'macro_name': macro_name, 'variation': variation}
        for field_data in field_data_list:
            df_dict['field_data'] = field_data
            self.create_tpfdf_lrec(df_dict, persistence=False)
        return

    def add_file(self, fixed_rec_id: int, fixed_file_type: int, fixed_file_ordinal: int, fixed_macro_name: str,
                 fixed_forward_chain_label: str = str(),
                 fixed_field_data: Dict[str, bytearray] = None,
                 fixed_item_field: str = str(),
                 fixed_item_count_field: str = str(),
                 fixed_item_position: int = 0,
                 fixed_item_forward_chain_count: int = 0,
                 fixed_item_field_data: Dict[str, bytearray] = None,
                 pool_rec_id: int = 0,
                 pool_macro_name: str = str(),
                 pool_index_field: str = str(),
                 pool_index_count: int = 0,
                 pool_index_forward_chain_count: int = 0,
                 pool_forward_chain_label: str = str(),
                 pool_field_data: Dict[str, bytearray] = None,
                 pool_item_field: str = str(),
                 pool_item_count_field: str = str(),
                 pool_item_position: int = 0,
                 pool_item_forward_chain_count: int = 0,
                 pool_item_field_data: Dict[str, bytearray] = None,
                 ) -> None:
        fixed_file = self._get_or_create_fixed_file(fixed_rec_id, fixed_file_type, fixed_file_ordinal, fixed_macro_name)
        fixed_file.forward_chain_label = fixed_forward_chain_label
        fixed_file.forward_chain_count = fixed_item_forward_chain_count
        if fixed_item_forward_chain_count and not fixed_forward_chain_label:
            raise PoolFileSpecificationError
        if fixed_field_data:
            fixed_file.field_data = self._bytearray_to_field_data(fixed_field_data)
        if fixed_item_field:
            if not fixed_item_field_data:
                raise FileItemSpecificationError
            item = FileItem()
            fixed_file.file_items.append(item)
            item.field = fixed_item_field
            item.position = fixed_item_position
            item.count_field = fixed_item_count_field
            item.field_data = self._bytearray_to_field_data(fixed_item_field_data)
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
            if pool_field_data:
                pool.field_data = self._bytearray_to_field_data(pool_field_data)
            if pool_item_field:
                if not pool_item_field_data:
                    raise FileItemSpecificationError
                item = FileItem()
                pool.file_items.append(item)
                item.field = pool_item_field
                item.position = pool_item_position
                item.count_field = pool_item_count_field
                item.field_data = self._bytearray_to_field_data(pool_item_field_data)
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
    def _bytearray_to_field_data(field_bytes: Dict[str, bytearray]):
        return [{'field': field, 'data': b64encode(data).decode()} for field, data in field_bytes.items()]
