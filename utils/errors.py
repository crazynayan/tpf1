class TpfAnalyzerError(Exception):
    pass


class AssemblyError(TpfAnalyzerError):
    pass


class ExecutionError(TpfAnalyzerError):
    pass


class TestDataError(TpfAnalyzerError):
    pass


class NotFoundInSymbolTableError(AssemblyError):
    pass


class EquLabelRequiredError(AssemblyError):
    pass


class EquDataTypeHasAmpersandError(AssemblyError):
    pass


class RegisterInvalidError(AssemblyError, ExecutionError):
    pass


class UsingInvalidError(AssemblyError):
    pass


class FieldDspInvalidError(AssemblyError):
    pass


class FieldLengthInvalidError(AssemblyError):
    pass


class DataInvalidError(AssemblyError):
    pass


class BitsInvalidError(AssemblyError):
    pass


class RegisterIndexInvalidError(AssemblyError):
    pass


class BranchInvalidError(AssemblyError):
    pass


class ConditionMaskError(AssemblyError):
    pass


class PackExecutionError(ExecutionError):
    pass


class BctExecutionError(ExecutionError):
    pass


class SegmentNotFoundError(ExecutionError):
    pass


class EcbLevelFormatError(ExecutionError):
    pass


class PartitionError(ExecutionError):
    pass


class PnrElementError(TestDataError):
    pass


class InvalidBaseRegError(TestDataError):
    pass


class TpfdfError(TestDataError):
    pass
