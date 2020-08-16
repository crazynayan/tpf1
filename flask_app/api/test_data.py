from typing import List, Dict, Union, Tuple

from firestore_ci import FirestoreDocument

from assembly.seg6_segment import segments
from flask_app.api.constants import ErrorMsg, Types, NAME, SEG_NAME, TYPE, ACTION, Action, NEW_NAME


class TestData(FirestoreDocument):
    # Types of Test Data elements
    REGISTERS = "Registers"
    CORE_BLOCK = "Core Block"
    PNR = "PNR"
    FIXED_FILE = "Fixed File"
    POOL_FILE = "Pool File"
    TPFDF = "TPFDF"
    OUTPUT_HEADER = "Output Header"
    INPUT_HEADER = "Input Header"

    def __init__(self):
        super().__init__()
        # Common Fields
        self.name: str = str()
        self.output: bool = bool()
        self.type: str = str()
        # Variation
        self.variation: int = int()  # Input Core Block, PNR, TPFDF, Fixed File, Pool File
        self.variation_name: str = str()  # Input Core Block, PNR, TPFDF, Fixed File, Pool File
        self.variation_link: Dict[str, int] = {  # Output Data
            self.CORE_BLOCK: 0,
            self.PNR: 0,
            self.TPFDF: 0,
            self.FIXED_FILE: 0
        }
        self.variation_name_link: Dict[str, str] = {  # Output Data
            self.CORE_BLOCK: str(),
            self.PNR: str(),
            self.TPFDF: str(),
            self.FIXED_FILE: str()
        }
        # Input Header, Output Header
        self.seg_name: str = str()  # Input Header
        self.error_simulations: List[str] = list()  # Input Header
        self.partition: str = str()  # Input Header
        self.registers: Dict[str, int] = dict()  # Input Header, Output Header
        self.reg_pointers: Dict[str, Union[str, int]] = dict()  # Output Header
        self.dumps: List[str] = list()  # Output Header
        self.messages: List[str] = list()  # Output Header
        self.last_line: str = str()  # Output Header
        self.debug: List[str] = list()  # Output Header
        # Common Data Specific field
        self.field_data: List[dict] = list()  # Core Block, PNR, TPFDF, Fixed File, Pool File
        self.macro_name: str = str()  # Core Block, TPFDF, Fixed File, Pool File
        # Core Block, PNR, TPFDF
        self.base_reg: str = str()  # Core Block
        self.pnr_locator: str = str()  # PNR
        self.key: str = str()  # PNR, TPFDF
        self.pnr_text: str = str()  # PNR
        # File Specific
        self.record_id: int = 0  # Fixed File, Pool File
        self.forward_chain_label: str = str()  # Fixed File, Pool File
        self.forward_chain_count: str = str()  # Fixed File, Pool File
        self.fixed_type: int = 0  # Fixed File
        self.fixed_ordinal: int = -1  # Fixed File
        self.index_field: str = str()  # Pool File
        self.index_macro_name: str = str()  # Pool File
        self.item_macro_name: str = str()  # Fixed File, Pool File
        self.item_field: str = str()  # Fixed File, Pool File
        self.item_count_field: str = str()  # Fixed File, Pool File
        self.item_field_data: list = list()  # Fixed File, Pool File

    @staticmethod
    def _check_empty(data: dict, key: str) -> bool:
        # return True if empty else False
        return not (isinstance(data, dict) and isinstance(key, str) and data and data.get(key, None)
                    and isinstance(data[key], str) and data[key].strip() != str())

    @classmethod
    def _validate_name(cls, data: dict, key: str) -> (bool, str):
        # return True, msg  if invalid else False, empty msg
        if cls._check_empty(data, key):
            return True, ErrorMsg.NOT_EMPTY
        elif len(data[key]) > 100:
            return True, ErrorMsg.LESS_100
        elif cls.objects.filter_by(name=data[key], type=cls.INPUT_HEADER).first():
            return True, ErrorMsg.UNIQUE
        return False, str()

    @classmethod
    def _validate_for_copy_rename(cls, data_dict) -> Tuple[dict, List["TestData"]]:
        # return errors dict, empty list if invalid else empty dict, list of TestData elements
        test_data = list()
        errors = dict()
        error, message = cls._validate_name(data_dict, NEW_NAME)
        if error:
            errors[NEW_NAME] = message
        if cls._check_empty(data_dict, NAME):
            errors[NAME] = ErrorMsg.NOT_EMPTY
        else:
            test_data = cls.objects.filter_by(name=data_dict[NAME]).get()
            if not test_data:
                errors[NAME] = ErrorMsg.NOT_FOUND
        return errors, test_data

    @classmethod
    def process_test_data(cls, data_dict: dict) -> (int, dict):
        if cls._check_empty(data_dict, ACTION):
            return 400, {ACTION: ErrorMsg.NOT_EMPTY}
        if data_dict[ACTION] == Action.CREATE:
            return cls.create_test_data(data_dict)
        if data_dict[ACTION] == Action.RENAME:
            return cls.rename_test_data(data_dict)
        if data_dict[ACTION] == Action.COPY:
            return cls.copy_test_data(data_dict)
        return 400, {ACTION: ErrorMsg.INVALID_ACTION}

    @classmethod
    def create_test_data(cls, data_dict: dict) -> (int, dict):
        errors = dict()
        if cls._check_empty(data_dict, SEG_NAME):
            errors[SEG_NAME] = ErrorMsg.NOT_EMPTY
        elif data_dict[SEG_NAME].upper() not in segments:
            errors[SEG_NAME] = ErrorMsg.SEG_LIBRARY
        error, message = cls._validate_name(data_dict, NAME)
        if error:
            errors[NAME] = message
        if errors:
            return 400, errors
        input_dict = dict()
        input_dict[NAME] = data_dict[NAME].strip()
        input_dict[TYPE] = Types.INPUT_HEADER
        input_dict[SEG_NAME] = data_dict[SEG_NAME].upper()
        header: dict = TestData.objects.truncate.no_orm.create(input_dict)
        return 200, header

    @classmethod
    def rename_test_data(cls, data_dict: dict) -> (int, dict):
        errors, test_data = cls._validate_for_copy_rename(data_dict)
        if errors:
            return 400, errors
        for element in test_data:
            element.name = data_dict[NEW_NAME].strip()
        saved_test_data: List[dict] = cls.objects.no_orm.truncate.save_all(test_data)
        response = next(element for element in saved_test_data if element[TYPE] == Types.INPUT_HEADER)
        return 200, response

    @classmethod
    def copy_test_data(cls, data_dict: dict) -> (int, dict):
        errors, test_data = cls._validate_for_copy_rename(data_dict)
        if errors:
            return 400, errors
        for element in test_data:
            element.name = data_dict[NEW_NAME].strip()
        copy_test_data: List[dict] = cls.objects.truncate.to_dicts(test_data)
        created_test_data: List[dict] = cls.objects.no_orm.truncate.create_all(copy_test_data)
        return 200, created_test_data


TestData.init("test_elements")
