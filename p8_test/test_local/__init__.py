import unittest
from base64 import b64encode
from typing import List, Union, Dict

from config import config
from p2_assembly.mac2_data_macro import DataMacro
from p3_db.test_data import TestData
from p4_execution.debug import get_debug_loc, add_debug_loc, get_missed_loc
from p4_execution.ex5_execute import TpfServer


class TestDataUTS(TestData):

    def add_all_regs(self) -> None:
        for reg in config.REG:
            if reg in ["R8", "R9"]:
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
            field_dict["field"] = field
            field_dict["base_reg"] = base_reg if base_reg else str()
            field_dict["length"] = length
            self.output.create_field_byte(macro_name, field_dict, persistence=False)
        return

    def set_field(self, field_name: str, data: Union[bytearray, bytes], variation: int = 0) -> None:
        macro_name = DataMacro.get_label_reference(field_name).name
        field_dict = {"field": field_name, "data": b64encode(data).decode(), "variation": variation,
                      "variation_name": str()}
        self.create_field_byte(macro_name, field_dict, persistence=False)

    def set_global_field(self, global_name: str, hex_data: str, variation: int = 0) -> None:
        body = {"global_name": global_name, "variation": variation, "variation_name": str(), "is_global_record": False,
                "hex_data": hex_data, "seg_name": str(), "field_data": str()}
        self.create_global(body, persistence=False)

    def set_global_record(self, global_name: str, field_data: str, seg_name: str, variation: int = 0) -> None:
        body = {"global_name": global_name, "variation": variation, "variation_name": str(), "is_global_record": True,
                "hex_data": str(), "seg_name": seg_name, "field_data": field_data}
        self.create_global(body, persistence=False)

    def add_pnr_element(self, data_list: List[str], key: str, locator: str = None, variation: int = 0) -> None:
        body = {"key": key, "text": ",".join(data_list), "variation": variation, "variation_name": str(),
                "locator": locator if locator else str(), "field_data_item": str()}
        self.create_pnr_input(body, persistence=False)
        return

    def add_pnr_field_data(self, field_data_item: str, key: str, locator: str = None, variation: int = 0):
        body = {"key": key, "text": str(), "variation": variation, "variation_name": str(),
                "locator": locator if locator else str(), "field_data_item": field_data_item}
        self.create_pnr_input(body, persistence=False)
        return

    def add_tpfdf(self, field_data_list: List[Dict[str, str]], key: str, macro_name: str, variation: int = 0):
        df_dict = {"key": key, "macro_name": macro_name, "variation": variation, "variation_name": str()}
        for field_data in field_data_list:
            df_dict["field_data"] = field_data
            self.create_tpfdf_lrec(df_dict, persistence=False)
        return


class TestDebug(unittest.TestCase):
    SEGMENTS = ["ETA1", "ETAX", "ETAF", "ETAZ", "ETK1", "ETKF", "ETA4", "ETA5", "ETAW", "ETA6", "ETK2", "ETK6", "ETAA",
                "ETA9", "ETG1", "INS0", "ETG2", "ETGG", "ETG3", "ETGE", "EWA1", "EXA1", "EXAA", "EXAK", "EXA2", "EXA3",
                "EXA8", "EXA9", "EXA4", "EXA5", "EXE1", "EXE2", "EXER", "EXE3", "EXE6", "EXE4", "EXEN"]
    SUCCESS_END = "EXEN0000"
    ETG1_TJR_END = "ETG10750.2"
    EXAA_NPTY_END = "EXAA0525.6"
    FMSG_END = "FMSG0100"
    IGR1_END = "IGR1E000"

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.output.debug = self.SEGMENTS if config.TEST_DEBUG else list()
        self.output = None
        self.test_data.set_global_record("@PDTPC", field_data=str(), seg_name=str())

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
