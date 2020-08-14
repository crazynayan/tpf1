ACTION = "action"


class Action:
    CREATE = "create"
    COPY = "copy"
    RENAME = "rename"


ALL_ACTIONS = [value for key, value in Action.__dict__.items() if not key.startswith("__")]


class ErrorMsg:
    NOT_EMPTY = "must not be empty"
    UNIQUE = "must be unique"
    SEG_LIBRARY = "must be present in segment library"
    NOT_FOUND = "not found"
    LESS_100 = "must be less than 100 characters"
    INVALID_ACTION = f"must be either {', '.join(ALL_ACTIONS)}"
    RENAME_SAME = "must be different than original name"


class SuccessMsg:
    DELETE = "deleted successfully"


class Types:
    REGISTERS = "Registers"
    CORE_BLOCK = "Core Block"
    PNR = "PNR"
    FIXED_FILE = "Fixed File"
    POOL_FILE = "Pool File"
    TPFDF = "TPFDF"
    OUTPUT_HEADER = "Output Header"
    INPUT_HEADER = "Input Header"


TEST_DATA = "test_data"
NEW_NAME = "new_name"

# Test Data Attributes
NAME = "name"
SEG_NAME = "seg_name"
TYPE = "type"
