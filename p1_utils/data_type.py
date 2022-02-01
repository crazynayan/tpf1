from typing import Optional, Dict, Callable

from config import config
from p1_utils.errors import PackExecutionError


class DataTypeGeneric:
    DATA_TYPES: Dict[str, int] = {
        "X": 1, "C": 1, "H": 2, "F": 4, "D": 8, "FD": 8, "B": 1, "P": 1, "Z": 1, "A": 4, "Y": 2, "AD": 8, "V": 4, "S": 2
    }

    def __init__(self):
        self.data_type: Optional[str] = None
        self.input: Optional[str] = None
        self.bytes: Optional[bytearray] = None

    @property
    def default_length(self) -> int:
        return self.DATA_TYPES[self.data_type] if self.bytes is None else len(self.bytes)

    @property
    def align_to_boundary(self) -> int:
        return 0 if self.DATA_TYPES[self.data_type] == 1 else self.DATA_TYPES[self.data_type]

    def from_bytes(self) -> int:
        return int.from_bytes(self.bytes, "big", signed=False)

    @property
    def decode(self) -> str:
        return self.bytes.decode(encoding="cp037")


class CDataType(DataTypeGeneric):

    def __init__(self):
        super().__init__()
        self.data_type = "C"

    @property
    def length(self) -> int:
        return len(self.input) if self.input is not None else self.default_length

    @property
    def value(self) -> int:
        return int.from_bytes(bytes(self.input, encoding="cp037"), "big", signed=False) \
            if self.input is not None else self.from_bytes()

    def to_bytes(self, length: int = None) -> bytearray:
        char_data = bytearray(self.input, encoding="cp037")
        if length is None or length == self.length:
            return char_data
        if self.length > length:
            return char_data[:length]  # Truncation
        char_data.extend(bytearray([config.CHAR_PADDING] * (length - self.length)))
        return char_data  # Padding

    @property
    def encode(self, length: int = None) -> str:
        char_bytes = self.to_bytes(length)
        return char_bytes.hex().upper()


class XDataType(DataTypeGeneric):

    def __init__(self):
        super().__init__()
        self.data_type = "X"

    @property
    def length(self) -> int:
        return -(-len(self.input) // 2) if self.input is not None else self.default_length

    @property
    def value(self) -> int:
        return int(self.input, 16) if self.input is not None else self.from_bytes()

    def to_bytes(self, length: int = None) -> bytearray:
        length = length or self.length
        try:
            return bytearray(self.value.to_bytes(length, "big", signed=False))
        except OverflowError:
            return bytearray(self.value.to_bytes(self.length, "big", signed=False)[(self.length - length):])

    @property
    def decode(self) -> str:
        return self.bytes.decode(encoding="cp037") if self.bytes else self.to_bytes().decode(encoding="cp037")


class BDataType(DataTypeGeneric):
    def __init__(self):
        super().__init__()
        self.data_type = "B"

    @property
    def length(self) -> int:
        return -(-len(self.input) // 8) if self.input is not None else self.default_length

    @property
    def value(self) -> int:
        return int(self.input, 2) if self.input is not None else self.from_bytes()

    def to_bytes(self, length: int = None) -> bytearray:
        length = length or self.length
        try:
            return bytearray(self.value.to_bytes(length, "big", signed=False))
        except OverflowError:
            return bytearray(self.value.to_bytes(self.length, "big", signed=False)[(self.length - length):])


class PDataType(DataTypeGeneric):

    def __init__(self):
        super().__init__()
        self.data_type = "P"

    @property
    def length(self) -> int:
        if self.input is None:
            return self.default_length
        length_input = len(self.input) + 1 if self.input[0] not in ["+", "-"] else len(self.input)
        return -(-length_input // 2)

    @property
    def value(self) -> int:
        return int(self.input) if self.input is not None else self.from_bytes()

    def to_bytes(self, length: int = None) -> bytearray:
        packed_data = self.input[1:] if self.input[0] in ["+", "-"] else self.input
        packed_data = packed_data + "D" if self.input[0] == "-" else packed_data + "C"
        length = length or self.length
        try:
            return bytearray(int(packed_data, 16).to_bytes(length, "big", signed=False))
        except OverflowError:
            return bytearray(int(packed_data, 16).to_bytes(self.length, "big", signed=False)[(self.length - length):])

    def from_bytes(self) -> int:
        if not self.is_sign_valid() or not self.is_packed_digit():
            raise PackExecutionError
        sign = "-" if self.bytes[-1] & 0x0F in (0xB, 0xD) else "+"
        return int(f"{sign}{self.bytes.hex()[:-1]}")

    def is_packed_digit(self) -> bool:
        if self.bytes[-1] & 0xF0 >> 8 > 0x9:
            return False
        return all(byte & 0xF0 >> 8 <= 0x9 and byte & 0x0F <= 0x9 for byte in self.bytes[:-1])

    def is_sign_valid(self) -> bool:
        return self.bytes[-1] & 0x0F > 0x9


class ZDataType(DataTypeGeneric):

    def __init__(self):
        super().__init__()
        self.data_type = "Z"

    @property
    def length(self) -> int:
        if self.input is None:
            return self.default_length
        return len(self.input) - 1 if self.input[0] in ["+", "-"] else len(self.input)

    @property
    def value(self) -> int:
        return int(self.input) if self.input is not None else self.from_bytes()

    def to_bytes(self, length: int = None) -> bytearray:
        zoned_data = self.input[1:] if self.input[0] in ["+", "-"] else self.input
        sign = 0xD0 if self.input[0] == "-" else 0xC0
        zoned_data = bytearray(zoned_data, "cp037")
        zoned_data[-1] = zoned_data[-1] & 0x0F | sign
        if length is None or length == self.length:
            return zoned_data
        if self.length > length:
            return zoned_data[(self.length - length):]  # Truncation
        pad_data = bytearray([config.NUMBER_PADDING] * (length - self.length))
        pad_data.extend(zoned_data)
        return pad_data  # Padding

    def from_bytes(self) -> int:
        sign = "-" if self.bytes[-1] & 0xF0 == 0xD0 else "+"
        numeric_bytes = self.bytes.copy()
        numeric_bytes[-1] |= 0xF0
        return int(f"{sign}{numeric_bytes.decode(encoding='cp037')}")


class NumericDataType(DataTypeGeneric):
    @property
    def length(self) -> int:
        return self.default_length

    @property
    def value(self) -> int:
        return round(float(self.input)) if self.input is not None else self.from_bytes()

    def to_bytes(self, length: int = None) -> bytearray:
        number_length = length or self.length
        number = self.value
        try:
            return bytearray(number.to_bytes(number_length, "big", signed=True))
        except OverflowError:
            try:
                return bytearray(number.to_bytes(self.length, "big", signed=True)[(self.length - number_length):])
            except OverflowError:
                return bytearray(number.to_bytes(number_length, "big", signed=False))

    def from_bytes(self) -> int:
        return int.from_bytes(self.bytes, "big", signed=True)


class FDataType(NumericDataType):

    def __init__(self):
        super().__init__()
        self.data_type = "F"


class HDataType(NumericDataType):

    def __init__(self):
        super().__init__()
        self.data_type = "H"


class FDDataType(NumericDataType):

    def __init__(self):
        super().__init__()
        self.data_type = "FD"


class ADDataType(NumericDataType):

    def __init__(self):
        super().__init__()
        self.data_type = "AD"


class DDataType(NumericDataType):

    def __init__(self):
        super().__init__()
        self.data_type = "D"


class ADataType(NumericDataType):
    def __init__(self):
        super().__init__()
        self.data_type = "A"


class YDataType(NumericDataType):

    def __init__(self):
        super().__init__()
        self.data_type = "Y"


class VDataType(NumericDataType):
    def __init__(self):
        super().__init__()
        self.data_type = "V"


class SDataType(NumericDataType):

    def __init__(self):
        super().__init__()
        self.data_type = "S"


class DataType:
    DT: Dict[str, Callable] = {
        "X": XDataType,
        "C": CDataType,
        "H": HDataType,
        "F": FDataType,
        "D": DDataType,
        "FD": FDDataType,
        "AD": ADDataType,
        "B": BDataType,
        "P": PDataType,
        "Z": ZDataType,
        "A": ADataType,
        "Y": YDataType,
        "V": VDataType,
        "S": SDataType,
    }

    def __init__(self, data_type: str, **kwargs):
        self.data_type_object = self.DT[data_type]()
        self.data_type_object.input = kwargs["input"] if "input" in kwargs else None
        self.data_type_object.bytes = kwargs["bytes"] if "bytes" in kwargs and "input" not in kwargs else None

    @property
    def default_length(self) -> int:
        return self.data_type_object.default_length

    @property
    def align_to_boundary(self) -> int:
        return self.data_type_object.align_to_boundary

    @property
    def length(self) -> int:
        return self.data_type_object.length

    @property
    def value(self) -> int:
        return self.data_type_object.value

    def to_bytes(self, length: int = None) -> bytearray:
        return self.data_type_object.to_bytes(length)

    def from_bytes(self) -> int:
        return self.data_type_object.from_bytes()

    @property
    def decode(self) -> str:
        return self.data_type_object.decode

    @property
    def encode(self) -> str:
        return self.data_type_object.encode


class Register:

    def __init__(self, reg: str = None):
        super().__init__()
        self.reg = next((key for key in config.REG for reg_val in config.REG[key] if reg_val == reg),
                        config.REG_INVALID)

    def __repr__(self) -> str:
        return self.reg

    def is_valid(self) -> bool:
        return self.reg != config.REG_INVALID

    def is_even(self) -> bool:
        return self.reg in config.REGISTERS_EVEN

    def get_next_register(self) -> "Register":
        if not self.is_valid():
            return self
        if self.reg == "R15":
            return Register("R0")
        return Register(config.REGISTERS[self.value + 1])

    @classmethod
    def from_index(cls, index: int) -> "Register":
        if not (0 <= index < len(config.REGISTERS)):
            return cls("INVALID")
        return cls(config.REGISTERS[index])

    @property
    def value(self) -> int:
        return config.REGISTERS.index(self.reg)
