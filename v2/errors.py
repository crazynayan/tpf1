class Error:
    NO_ERROR = 0
    DS_DUP_FACTOR = 'DS - Duplication factor is not a number.'
    DS_DATA_TYPE = 'DS - Invalid data type.'
    EXP_INVALID_KEY = 'Expression - Field not present in data map.'
    EXP_INVALID_KEY_L = 'Expression - Field not present in data map for length attribute.'
    EXP_INVALID_KEY_X = 'Expression - Field not present in data map for hex data type.'
    EXP_DATA_TYPE = 'Expression - Invalid data type.'
    EXP_NOT_NUMBER = 'Expression - Not a number.'
    EXP_EVAL_FAIL = 'Expression - Function eval failed.'
    EXP_REGEX = 'Expression - Regex cannot parse the expression.'
    FBD_NO_LEN = 'FieldBaseDsp - Operand cannot have length or index.'
    FBD_INVALID_KEY = 'Field - Field not present in data map.'
    FBD_INVALID_KEY_BASE = 'Field - Macro not present for identifying base register.'
    FBD_INVALID_BASE = 'Field - Invalid base register specified.'
    FBD_INVALID_DSP = 'Field - Invalid displacement specified.'
    FX_INVALID_INDEX = 'FieldIndex - Invalid index register specified.'
    BITS_INVALID_NUMBER = 'Bits - Invalid number.'
    BITS_INVALID_BIT = 'Bits - Invalid bit value.'
    INSTRUCTION_INVALID = 'Instruction - Invalid Class.'
    REG_INVALID = 'Register - Invalid.'
    RFX_INVALID_REG = 'RegisterFieldIndex - Invalid register specified'
    FL_LEN_REQUIRED = 'FieldLen - Length required.'
    FL_BASE_REQUIRED = 'FieldLen - Base required.'
    FL_INVALID_LEN = 'FieldLen - Invalid length.'
