import re
from v2.errors import Error


class Register:
    INVALID = '??'
    REG = {
        'R0': ['R0', 'R00', 'RAC'],
        'R1': ['R1', 'R01', 'RG1'],
        'R2': ['R2', 'R02', 'RGA'],
        'R3': ['R3', 'R03', 'RGB'],
        'R4': ['R4', 'R04', 'RGC'],
        'R5': ['R5', 'R05', 'RGD'],
        'R6': ['R6', 'R06', 'RGE'],
        'R7': ['R7', 'R07', 'RGF'],
        'R8': ['R8', 'R08', 'RAP'],
        'R9': ['R9', 'R09', 'REB'],
        'R10': ['R10', 'RLA'],
        'R11': ['R11', 'RLB'],
        'R12': ['R12', 'RLC'],
        'R13': ['R13', 'RLD'],
        'R14': ['R14', 'RDA'],
        'R15': ['R15', 'RDB'],
    }

    def __init__(self, reg=None):
        super().__init__()
        self._reg = next((key for key in self.REG for reg_val in self.REG[key] if reg_val == reg), self.INVALID)

    def __repr__(self):
        return self._reg

    def is_valid(self):
        return self._reg != self.INVALID


class Field:
    def __init__(self):
        self.name = None
        self.base = None
        self.dsp = -1

    def __repr__(self):
        return f"{self.name}:{self.base}+{self.dsp}"

    @staticmethod
    def get_base_dsp(operand):
        return next(iter(re.findall(r"^([^(]+)\(*([^,)]*),*([^)]*)\)*", operand)))

    @staticmethod
    def get_expression_count(expression):
        return len(re.split(r"[+-]", expression))


class FieldBaseDsp(Field):
    def __init__(self):
        super().__init__()

    @classmethod
    def from_operand(cls, operand, macro):
        field = cls()
        dsp, base, error = field.get_base_dsp(operand)
        if error:
            return field, Error.FBD_NO_LEN
        if not base:
            name = dsp
            try:
                dsp = macro.data_map[name].dsp
            except KeyError:
                return field, Error.FBD_INVALID_KEY
            try:
                base = macro.files[macro.data_map[name].macro].base
            except KeyError:
                return field, Error.FBD_INVALID_KEY_BASE
            field.name = name
            field.dsp = dsp
            field.base = base
            return field, Error.NO_ERROR
        # Get base register
        base = Register(base)
        if not base.is_valid():
            return field, Error.FBD_INVALID_BASE
        base = str(base)
        # Get displacement
        dsp, result = macro.get_value(dsp)
        if result != Error.NO_ERROR:
            return field, result
        if not isinstance(dsp, int) or dsp < 0:
            return field, Error.FBD_INVALID_DSP
        # Get field name
        name = base + '_AREA'
        field.base = base
        field.dsp = dsp
        field.name = name
        return field


class _Bit:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}:0x{self.value:02x}"


class Bits:
    BIT_MAP = {'0': 0x80, '1': 0x40, '2': 0x20, '3': 0x10, '4': 0x08, '5': 0x04, '6': 0x02, '7': 0x01}
    PREFIX = '#BIT'
    VALID_VALUE = {0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01}

    def __init__(self):
        self._bits = list()

    def add_bit(self, value, name=None):
        if name is None:
            name = next(self.PREFIX + position for position, bit_value in self.BIT_MAP.items() if bit_value == value)
        self._bits.append(_Bit(name, value))

    @classmethod
    def from_number(cls, number):
        bits = cls()
        bits._bits = [_Bit(cls.PREFIX + position, value) for position, value in cls.BIT_MAP.items()
                      if number & value == value]
        return bits

    @classmethod
    def from_operand(cls, operand, macro):
        if '-' in operand:
            number, result = macro.get_value(operand)
            if result != Error.NO_ERROR:
                return cls(), result
            if not isinstance(number, int) or number < 0 or number > 255:
                return cls(), Error.BITS_INVALID_NUMBER
            return cls().from_number(number), Error.NO_ERROR
        bits = cls()
        for expression in operand.split('+'):
            value, data_type, result = macro.evaluate(expression)
            if result != Error.NO_ERROR:
                return cls(), result
            if value not in cls.VALID_VALUE:
                return cls(), Error.BITS_INVALID_BIT
            if data_type != 'X' or data_type != macro.FIELD_LOOKUP or data_type != macro.INTEGER:
                return cls(), Error.BITS_INVALID_DATA_TYPE
            if data_type == macro.FIELD_LOOKUP:
                bits.add_bit(value, expression)
            else:
                bits.add_bit(value)
        return bits, Error.NO_ERROR
