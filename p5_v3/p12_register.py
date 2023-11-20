from p5_v3.p01_errors import ParserError


class Registers:
    R0, R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15 = "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", \
        "R10", "R11", "R12", "R13", "R14", "R15"
    TO_VALUE = {R0: 0, "R00": 0, "RAC": 0, R1: 1, "R01": 1, "RG1": 1, R2: 2, "R02": 2, "RGA": 2, R3: 3, "R03": 3, "RGB": 3,
                R4: 4, "R04": 4, "RGC": 4, R5: 5, "R05": 5, "RGD": 5, R6: 6, "R06": 6, "RGE": 6, R7: 7, "R07": 7, "RGF": 7,
                R8: 8, "R08": 8, "RAP": 8, R9: 9, "R09": 9, "REB": 9, R10: 10, "RLA": 10, R11: 11, "RLB": 11,
                R12: 12, "RLC": 12, R13: 13, "RLD": 13, R14: 14, "RDA": 14, R15: 15, "RDB": 15}
    REGISTER_PREFIX = "R"

    @classmethod
    def is_symbol_valid(cls, register: str) -> bool:
        return register in cls.TO_VALUE

    @classmethod
    def get_value(cls, register: str) -> int:
        try:
            return cls.TO_VALUE[register]
        except KeyError:
            raise ParserError("Registers -> Invalid Register.")

    @classmethod
    def is_value_valid(cls, register_value: int) -> bool:
        return 0 <= register_value <= 15

    @classmethod
    def get_symbol(cls, register_value: int) -> str:
        if not cls.is_value_valid(register_value):
            raise ParserError("Registers -> Invalid Register.")
        return f"{cls.REGISTER_PREFIX}{register_value}"
