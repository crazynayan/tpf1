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


class DropInvalidError(AssemblyError):
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


class BaseAddressError(ExecutionError):
    pass


class PackExecutionError(ExecutionError):
    pass


class BctExecutionError(ExecutionError):
    pass


class ExExecutionError(ExecutionError):
    pass


class DumpExecutionError(ExecutionError):
    pass


class HeapaExecutionError(ExecutionError):
    pass


class MhinfExecutionError(ExecutionError):
    pass


class LevtaExecutionError(ExecutionError):
    pass


class SegmentNotFoundError(ExecutionError):
    pass


class EcbLevelFormatError(ExecutionError):
    pass


class PartitionError(ExecutionError):
    pass


class MaskError(ExecutionError):
    pass


class Pd0BaseError(ExecutionError):
    pass


class PdredFieldError(ExecutionError):
    pass


class PdredVerifyError(ExecutionError):
    pass


class PdredSearchError(ExecutionError):
    pass


class PdredNotFoundError(ExecutionError):
    pass


class PdredPd0Error(ExecutionError):
    pass


class DbredError(ExecutionError):
    pass


class FaceError(ExecutionError):
    pass


class PnrLocatorNotFoundError(ExecutionError):
    pass


class UcdrError(ExecutionError):
    pass


class PnrElementError(TestDataError):
    pass


class InvalidBaseRegError(TestDataError):
    pass


class TpfdfError(TestDataError):
    pass


class FileItemSpecificationError(TestDataError):
    pass


class PoolFileSpecificationError(TestDataError):
    pass
