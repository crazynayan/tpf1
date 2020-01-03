from typing import Dict, List, Tuple

from config import config
from firestore.test_data import TestData, Core, FieldByte, Pnr, Tpfdf, FileItem, PoolFile, FixedFile, Output
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
