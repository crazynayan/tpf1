import random
import string
import unittest
from typing import List, Union, Dict

from config import config
from p2_assembly.mac2_data_macro import DataMacro
from p3_db.test_data import TestData
from p3_db.test_data_elements import Pnr
from p4_execution.debug import get_debug_loc, add_debug_loc, get_missed_loc
from p4_execution.ex5_execute import TpfServer


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
        pnr_dict = {'key': key, 'data': ','.join(data_list), 'variation': variation, 'variation_name': str(),
                    'locator': str()}
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
        df_dict = {'key': key, 'macro_name': macro_name, 'variation': variation, 'variation_name': str()}
        for field_data in field_data_list:
            df_dict['field_data'] = field_data
            self.create_tpfdf_lrec(df_dict, persistence=False)
        return


class TestDebug(unittest.TestCase):
    SEGMENTS = ["ETA1", "ETAX", "ETAF", "ETAZ", "ETK1", "ETKF", "ETA4", "ETA5", "ETAW"]
    SUCCESS_END = "ETA60000"

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.output.debug = self.SEGMENTS if config.TEST_DEBUG else list()
        self.output = None

    def tearDown(self) -> None:
        if not config.TEST_DEBUG:
            return
        if not self.output or not self.output.debug:
            return
        add_debug_loc(config.ET_DEBUG_DATA, self.output.debug)
        add_debug_loc(config.ET_DEBUG_DATA_MISSED, self.output.debug_missed)

    @classmethod
    def tearDownClass(cls) -> None:
        if not config.TEST_DEBUG:
            return
        config.ET_CLASS_COUNTER += 1
        if config.ET_CLASS_COUNTER < config.ET_TEST_CLASS_COUNT:
            return
        for segment in cls.SEGMENTS:
            loc = get_debug_loc(config.ET_DEBUG_DATA, segment)
            loc_missed = get_missed_loc(config.ET_DEBUG_DATA_MISSED, config.ET_DEBUG_DATA, segment)
            print(f"{segment} LOC Done = {loc}, LOC Missed = {loc_missed}")
