from base64 import b64decode
from copy import copy
from typing import List, Dict, Union

from firestore_ci import FirestoreDocument

from p3_db.test_data import TestData
from p3_db.test_data_elements import Core, Pnr, FixedFile, Output


def convert_field_list(field_list: List[dict]) -> list:
    updated_field_list = list()
    for field_data in field_list:
        updated_field_data = copy(field_data)
        updated_field_data["data"] = b64decode(field_data["data"]).hex().upper()
        updated_field_list.append(updated_field_data)
    return updated_field_list


class TestResult(FirestoreDocument):
    HEADER, CORE, PNR, TPFDF, FILE, RESULT = "header", "core", "pnr", "tpfdf", "file", "result"
    VALID_TYPE_FIELDS = {
        HEADER: ["name", "type", "seg_name", "stop_segments", "errors", "regs", "owner"],
        CORE: ["name", "type", "variation", "variation_name", "macro_name", "heap_name", "ecb_level", "global_name",
               "field_data", "hex_data", "is_global_record"],
        PNR: ["name", "type", "variation", "variation_name", "locator", "key", "field_data", "text"],
        TPFDF: ["name", "type", "variation", "variation_name", "macro_name", "key", "field_data"],
        FILE: ["name", "type", "variation", "variation_name", "fixed_rec_id", "fixed_forward_chain_label",
               "fixed_forward_chain_count", "fixed_type", "fixed_ordinal", "fixed_field_data", "fixed_item_label",
               "fixed_item_adjust", "fixed_item_repeat", "fixed_item_count_label", "fixed_item_field_data",
               "pool_macro_name", "pool_rec_id", "pool_fixed_label", "pool_forward_chain_label",
               "pool_forward_chain_count", "pool_field_data", "pool_item_label", "pool_item_adjust", "pool_item_repeat",
               "pool_item_count_label", "pool_item_field_data"],
        RESULT: ["name", "type", "variation", "variation_name", "result_id", "result_regs", "reg_pointers", "dumps",
                 "messages", "last_node", "user_comment", "core_comment", "pnr_comment", "core_field_data",
                 "pnr_field_data"],
    }
    VALID_COMMENT_TYPES = {"user_comment", "core_comment", "pnr_comment"}

    def __init__(self, name=str(), test_data=None, core=None, pnr=None, tpfdf=None, file=None, output=None):
        super().__init__()
        self.name = name  # Each test result should have unique name. Helps in grouping elements of a test result.
        self.type = str()  # Must be from valid type fields.
        # Header
        self.owner = str()
        self.seg_name = str()
        self.stop_segments: List[str] = list()
        self.errors: List[str] = list()
        self.regs: Dict[str, int] = dict()
        # Common Inputs
        self.variation: int = int()
        self.variation_name: str = str()
        self.field_data: List[dict] = list()
        # Core
        self.macro_name: str = str()  # Also used in tpfdf, file
        self.heap_name: str = str()
        self.ecb_level: str = str()
        self.global_name: str = str()
        self.hex_data: str = str()
        self.is_global_record: bool = bool()
        # PNR
        self.locator: str = str()
        self.key: str = str()  # Also used in tpfdf
        self.text: List[str] = list()
        # File Header
        self.fixed_rec_id: int = int()
        self.fixed_forward_chain_label: str = str()
        self.fixed_forward_chain_count: int = int()
        self.fixed_type: int = int()
        self.fixed_ordinal: int = int()
        self.fixed_field_data: List[dict] = list()
        self.fixed_item_label: str = str()
        self.fixed_item_adjust: bool = bool()
        self.fixed_item_repeat: int = int()
        self.fixed_item_count_label: str = str()
        self.fixed_item_field_data: List[dict] = list()
        self.pool_macro_name: str = str()
        self.pool_rec_id: int = int()
        self.pool_fixed_label: str = str()
        self.pool_forward_chain_label: str = str()
        self.pool_forward_chain_count: int = int()
        self.pool_field_data: List[dict] = list()
        self.pool_item_label: str = str()
        self.pool_item_adjust: bool = bool()
        self.pool_item_repeat: int = int()
        self.pool_item_count_label: str = str()
        self.pool_item_field_data: List[dict] = list()
        # RESULT
        self.result_id: int = int()
        self.result_regs: Dict[str, int] = dict()
        self.reg_pointers: Dict[str, Union[str, int]] = dict()
        self.dumps: List[str] = list()
        self.messages: List[str] = list()
        self.last_node: str = str()
        self.user_comment: str = str()
        self.core_comment: str = str()
        self.pnr_comment: str = str()
        self.core_field_data: List[dict] = list()
        self.pnr_field_data: List[dict] = list()
        # Initialize
        self.init_header(test_data, name)
        self.init_core(core)
        self.init_pnr(pnr)
        self.init_tpfdf(tpfdf)
        self.init_file(file)
        self.init_result(output)

    def init_from_input_object(self, input_object):
        for field in self.VALID_TYPE_FIELDS[self.type]:
            if not hasattr(input_object, field):
                continue
            setattr(self, field, getattr(input_object, field))
        return

    def init_header(self, test_data: TestData, name):
        if not test_data:
            return
        self.type = self.HEADER
        self.init_from_input_object(test_data)
        self.name = name

    def init_core(self, core: Core):
        if not core:
            return
        self.type = self.CORE
        self.init_from_input_object(core)
        self.field_data = convert_field_list(core.field_data)

    def init_pnr(self, pnr: Pnr):
        if not pnr:
            return
        self.type = self.CORE
        self.init_from_input_object(pnr)
        self.field_data = convert_field_list(pnr.field_data_item)

    def init_tpfdf(self, tpfdf: Core):
        if not tpfdf:
            return
        self.type = self.TPFDF
        self.init_from_input_object(tpfdf)
        self.field_data = convert_field_list(tpfdf.field_data)

    def init_file(self, file: FixedFile):
        if not file:
            return
        self.type = self.FILE
        self.fixed_rec_id: int = file.rec_id
        self.fixed_forward_chain_label: str = file.forward_chain_label
        self.fixed_forward_chain_count: int = file.forward_chain_count
        self.fixed_type: int = file.fixed_type
        self.fixed_ordinal: int = file.fixed_ordinal
        self.fixed_field_data: List[dict] = convert_field_list(file.field_data)
        if file.file_items:
            self.fixed_item_label: str = file.file_items[0].field
            self.fixed_item_adjust: bool = file.file_items[0].adjust
            self.fixed_item_repeat: int = file.file_items[0].repeat
            self.fixed_item_count_label: str = file.file_items[0].count_field
            self.fixed_item_field_data: List[dict] = convert_field_list(file.file_items[0].field_data)
        if not file.pool_files:
            return
        self.pool_macro_name: str = file.pool_files[0].index_macro_name
        self.pool_rec_id: int = file.pool_files[0].rec_id
        self.pool_fixed_label: str = file.pool_files[0].index_field
        self.pool_forward_chain_label: str = file.pool_files[0].forward_chain_label
        self.pool_forward_chain_count: int = file.pool_files[0].forward_chain_count
        self.pool_field_data: List[dict] = convert_field_list(file.pool_files[0].field_data)
        if not file.pool_files[0].file_items:
            return
        self.pool_item_label: str = file.pool_files[0].file_items[0].field
        self.pool_item_adjust: bool = file.pool_files[0].file_items[0].adjust
        self.pool_item_repeat: int = file.pool_files[0].file_items[0].repeat
        self.pool_item_count_label: str = file.pool_files[0].file_items[0].count_field
        self.pool_item_field_data: List[dict] = convert_field_list(file.pool_files[0].file_items[0].field_data)

    def init_result(self, output: Output):
        if not output:
            return
        self.type = self.RESULT
        self.init_from_input_object(output)
        self.result_regs = output.regs
        self.pnr_field_data = [field_data for pnr in output.pnr_outputs
                               for field_data in convert_field_list(pnr.field_data)]
        self.core_field_data = [field_data for core in output.cores
                                for field_data in convert_field_list(core.field_data)]
        return

    @classmethod
    def is_comment_type_valid(cls, comment_type: str) -> bool:
        return comment_type in cls.VALID_COMMENT_TYPES

    def set_comment(self, comment: str, comment_type: str):
        setattr(self, comment_type, comment)

    def trunc_to_dict(self) -> dict:
        result = {key: value for key, value in self.doc_to_dict().items() if key in self.VALID_TYPE_FIELDS[self.type]}
        result["id"] = self.id
        return result


TestResult.init()
