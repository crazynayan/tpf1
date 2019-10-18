class Error:
    NO_ERROR = 0
    DS_DUP_FACTOR = 'DS - Duplication factor is not a number.'
    EXP_INVALID_KEY = 'Evaluate - Field not present in data map.'
    EQU_INVALID_VALUE = 'Equate - Not yet supporting macro variables.'
    EXP_REGEX = 'Expression - Regex cannot parse the expression.'
    FBD_NO_LEN = 'FieldBaseDsp - Operand cannot have length or index.'
    FBD_INVALID_KEY = 'Field - Field not present in data map.'
    FBD_INVALID_BASE = 'Field - Invalid base register specified.'
    FBD_INVALID_DSP = 'Field - Invalid displacement specified.'
    FX_INVALID_INDEX = 'FieldIndex - Invalid index register specified.'
    BITS_INVALID_NUMBER = 'Bits - Invalid number.'
    REG_INVALID = 'Register - Invalid.'
    RFX_INVALID_REG = 'RegisterFieldIndex - Invalid register specified'
    FL_LEN_REQUIRED = 'FieldLen - Length required.'
    FL_INVALID_LEN = 'FieldLen - Invalid length.'
    FD_INVALID_DATA = 'FieldData - Invalid data.'
    RD_INVALID_NUMBER = 'RegisterData - Invalid number.'
    RDF_INVALID_DATA = 'RegisterDataField - Invalid data.'
    BC_INDEX = 'BranchGeneric - Index is not yet supported in Branch instructions.'
    BC_INVALID_MASK = 'ConditionGeneric - Mask value not present in the command file.'
    BC_INVALID_BRANCH = 'BranchGeneric - Invalid Branch Label'
    EQU_LABEL_REQUIRED = 'Equ - Label required.'
    SC_INVALID_SEGMENT = 'SegmentCall - Invalid Segment.'
    FLFD_INVALID_DATA = 'FieldLenFieldData - Invalid data.'
    RL_INVALID_LEN = 'RegisterLabel - Invalid length of previous instruction.'
    RL_INVALID_LABEL = 'RegisterLabel - Invalid label.'


class TpfAnalyzerError(KeyError):
    pass


class NotFoundInSymbolTableError(TpfAnalyzerError):
    pass


class EquLabelRequiredError(TpfAnalyzerError):
    pass


class EquDataTypeHasAmpersandError(TpfAnalyzerError):
    pass


class RegisterInvalidError(TpfAnalyzerError):
    pass


class UsingInvalidError(TpfAnalyzerError):
    pass


class FieldDspInvalidError(TpfAnalyzerError):
    pass


class FieldLengthInvalidError(TpfAnalyzerError):
    pass


class BitsInvalidError(TpfAnalyzerError):
    pass
