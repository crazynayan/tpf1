from munch import Munch

from p5_v3.base_parser import Operators
from p5_v3.errors import ParserError


class DataType:
    X, C, H, F, D, FD, B, P, Z, A, Y, AD, V, S = "X", "C", "H", "F", "D", "FD", "B", "P", "Z", "A", "Y", "AD", "V", "S"
    DEFAULT_LENGTH: Munch = Munch({X: 1, C: 1, H: 2, F: 4, D: 8, FD: 8, B: 1, P: 1, Z: 1, A: 4, Y: 2, AD: 8, V: 4, S: 2})
    INPUT_BASED_LENGTH: Munch = Munch()
    INPUT_BASED_LENGTH.X = lambda string: -(-len(string) // 2)
    INPUT_BASED_LENGTH.C = lambda string: len(string)
    INPUT_BASED_LENGTH.H = lambda _: DataType.DEFAULT_LENGTH.H
    INPUT_BASED_LENGTH.F = lambda _: DataType.DEFAULT_LENGTH.F
    INPUT_BASED_LENGTH.D = lambda _: DataType.DEFAULT_LENGTH.D
    INPUT_BASED_LENGTH.FD = lambda _: DataType.DEFAULT_LENGTH.FD
    INPUT_BASED_LENGTH.B = lambda string: -(-len(string) // 8)
    INPUT_BASED_LENGTH.P = lambda string: -(-(len(string) + 1 if string[0] not in {Operators.PLUS, Operators.MINUS} else len(string)) // 2)
    INPUT_BASED_LENGTH.Z = lambda string: len(string) - 1 if string[0] in {Operators.PLUS, Operators.MINUS} else len(string)
    INPUT_BASED_LENGTH.A = lambda _: DataType.DEFAULT_LENGTH.A
    INPUT_BASED_LENGTH.Y = lambda _: DataType.DEFAULT_LENGTH.Y
    INPUT_BASED_LENGTH.AD = lambda _: DataType.DEFAULT_LENGTH.AD
    INPUT_BASED_LENGTH.V = lambda _: DataType.DEFAULT_LENGTH.V
    INPUT_BASED_LENGTH.S = lambda _: DataType.DEFAULT_LENGTH.S

    @classmethod
    def get_data_type_from_start_of_string(cls, string: str) -> str:
        if len(string) >= 2 and string[:2] in cls.DEFAULT_LENGTH:
            return string[:2]
        if len(string) >= 1 and string[0] in cls.DEFAULT_LENGTH:
            return string[0]
        raise ParserError("DataType -> Input string is not a data type.")

    @classmethod
    def is_data_type_at_start_of_string(cls, string: str) -> bool:
        try:
            cls.get_data_type_from_start_of_string(string)
            return True
        except ParserError:
            return False

    @classmethod
    def get_length(cls, data_type: str, string: str = None) -> int:
        try:
            return cls.INPUT_BASED_LENGTH[data_type](string) if string else cls.DEFAULT_LENGTH[data_type]
        except KeyError:
            raise ParserError("DataType -> Invalid data type.")
