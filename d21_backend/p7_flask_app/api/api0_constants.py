# Special Request Attributes
ACTION = "action"
NEW_NAME = "new_name"
NEW_VARIATION_NAME = "new_variation_name"

# Special Response Attributes
TEST_DATA = "test_data"

# Test Data Attributes
NAME = "name"
SEG_NAME = "seg_name"
TYPE = "type"
FIELD_DATA = "field_data"
MACRO_NAME = "macro_name"
VARIATION = "variation"
VARIATION_NAME = "variation_name"

# Field Data Attributes
FIELD = "field"
DATA = "data"
LENGTH = "length"


class Actions:
    CREATE = "create"
    COPY = "copy"
    RENAME = "rename"
    UPDATE = "update"
    DELETE = "delete"


ALL_ACTIONS = [value for key, value in Actions.__dict__.items() if not key.startswith("__")]


class Types:
    INPUT_HEADER = "Input Header"
    INPUT_CORE_BLOCK = "Input Core Block"
    OUTPUT_CORE_BLOCK = "Output Core Block"


ALL_TYPES = [value for key, value in Types.__dict__.items() if not key.startswith("__")]


class ErrorMsg:
    NOT_EMPTY = "must not be empty"
    UNIQUE = "must be unique"
    SEG_LIBRARY = "must be present in segment library"
    MACRO_LIBRARY = "must be present in macro library"
    NOT_FOUND = "not found"
    LESS_100 = "must be less than 100 characters"
    INVALID_ACTION = f"must be either {', '.join(ALL_ACTIONS)}"
    RENAME_SAME = "must be different than the original name"
    MACRO_SAME = "must be from the same macro"
    MACRO_NOT_FOUND = "macro name not found"
    INVALID_TYPE = f"must be either {', '.join(ALL_TYPES)}"
    DATA_SAME = "must be different than the original"
    GREATER_0 = "must be greater than 0"
    VARIATION_NAME = f"must specify either {VARIATION} or {NEW_VARIATION_NAME} - not both"


class SuccessMsg:
    DELETE = "deleted successfully"
