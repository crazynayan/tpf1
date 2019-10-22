class TpfAnalyzerError(Exception):
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


class DataInvalidError(TpfAnalyzerError):
    pass


class BitsInvalidError(TpfAnalyzerError):
    pass


class RegisterIndexInvalidError(TpfAnalyzerError):
    pass


class RegisterLabelInvalidError(TpfAnalyzerError):
    pass


class BranchInvalidError(TpfAnalyzerError):
    pass


class BranchIndexError(TpfAnalyzerError):
    pass


class ConditionMaskError(TpfAnalyzerError):
    pass


class PackExecutionError(TpfAnalyzerError):
    pass
