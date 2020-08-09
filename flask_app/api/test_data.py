from typing import List, Dict, Union

from firestore_ci import FirestoreDocument


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
        self.variation: int = int()
        self.variation_name: str = str()
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


TestData.init("test_elements")
