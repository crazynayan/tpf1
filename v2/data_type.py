import re
from v2.errors import Error


class Register:
    INVALID = '??'
    REG = {
        'R0': ['R0', 'R00', 'RAC', '0'],
        'R1': ['R1', 'R01', 'RG1', '1'],
        'R2': ['R2', 'R02', 'RGA', '2'],
        'R3': ['R3', 'R03', 'RGB', '3'],
        'R4': ['R4', 'R04', 'RGC', '4'],
        'R5': ['R5', 'R05', 'RGD', '5'],
        'R6': ['R6', 'R06', 'RGE', '6'],
        'R7': ['R7', 'R07', 'RGF', '7'],
        'R8': ['R8', 'R08', 'RAP', '8'],
        'R9': ['R9', 'R09', 'REB', '9'],
        'R10': ['R10', 'RLA', '10'],
        'R11': ['R11', 'RLB', '11'],
        'R12': ['R12', 'RLC', '12'],
        'R13': ['R13', 'RLD', '13'],
        'R14': ['R14', 'RDA', '14'],
        'R15': ['R15', 'RDB', '15'],
    }

    def __init__(self, reg=None):
        super().__init__()
        self.reg = next((key for key in self.REG for reg_val in self.REG[key] if reg_val == reg), self.INVALID)

    def __repr__(self):
        return self.reg

    def is_valid(self):
        return self.reg != self.INVALID


class Field:
    def __init__(self):
        self.name = None
        self.base = None
        self.dsp = -1

    def __repr__(self):
        return f"{self.name}:{self.base}+{self.dsp}"

    @staticmethod
    def get_base_dsp(operand):
        # Returns up to 3 elements that are first divided by ( and then by a , and then by a )
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
        # Get displacement
        dsp, result = macro.get_value(dsp)
        if result != Error.NO_ERROR:
            return field, result
        if not isinstance(dsp, int) or dsp < 0:
            return field, Error.FBD_INVALID_DSP
        # Get field name
        possible_name = macro.get_field_name(base, dsp)
        name = base.reg + '_AREA' if possible_name is None else possible_name
        # Update the object and return it
        field.base = base
        field.dsp = dsp
        field.name = name
        return field, Error.NO_ERROR


class Bit:
    def __init__(self, name, value, on=False):
        self.name = name
        self.value = value
        self.on = on

    def __repr__(self):
        state = 'ON' if self.on else 'OFF'
        return f"{self.name}:0x{self.value:02x}:{state}"


class Bits:
    PREFIX = '#BIT'
    VALID_VALUE = {0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01}

    def __init__(self):
        self.bit0 = Bit(self.PREFIX + '0', 0x80)
        self.bit1 = Bit(self.PREFIX + '1', 0x40)
        self.bit2 = Bit(self.PREFIX + '2', 0x20)
        self.bit3 = Bit(self.PREFIX + '3', 0x10)
        self.bit4 = Bit(self.PREFIX + '4', 0x08)
        self.bit5 = Bit(self.PREFIX + '5', 0x04)
        self.bit6 = Bit(self.PREFIX + '6', 0x02)
        self.bit7 = Bit(self.PREFIX + '7', 0x01)

    def __repr__(self):
        bit_text = [str(bit) for _, bit in self.__dict__.items()]
        return '+'.join(bit_text)

    @property
    def value(self):
        return sum(bit.value for _, bit in self.__dict__.items() if bit.on)

    @property
    def text(self):
        bit_text = [bit.name for _, bit in self.__dict__.items() if bit.on]
        if len(bit_text) < 5:
            return '+'.join(bit_text)
        else:
            bit_text = [bit.name for _, bit in self.__dict__.items() if not bit.on]
            return f"#BITA-{'-'.join(bit_text)}"

    def set_name(self, name, value):
        bit = next(bit for _, bit in self.__dict__.items() if bit.value == value)
        bit.name = name

    def bit_by_name(self, name):
        return next(bit for _, bit in self.__dict__.items() if bit.name == name)

    def on_by_name(self, name):
        bit = next(bit for _, bit in self.__dict__.items() if bit.name == name)
        bit.on = True

    def off_by_name(self, name):
        bit = next(bit for _, bit in self.__dict__.items() if bit.name == name)
        bit.on = False

    def on_by_value(self, value):
        bit = next(bit for _, bit in self.__dict__.items() if bit.value == value)
        bit.on = True

    def off_by_value(self, value):
        bit = next(bit for _, bit in self.__dict__.items() if bit.value == value)
        bit.on = False

    @classmethod
    def from_number(cls, number):
        bits = cls()
        value = 0x80
        while value > 0:
            if value & number != 0:
                bits.on_by_value(value)
            value = value >> 1
        return bits

    @classmethod
    def from_operand(cls, operand, macro):
        number, result = macro.get_value(operand)
        if result != Error.NO_ERROR:
            return cls(), result
        if not isinstance(number, int) or number < 0 or number > 255:
            return cls(), Error.BITS_INVALID_NUMBER
        bits8 = cls().from_number(number)
        # Add the name from the expression
        for expression in re.split(f"[+-]", operand):
            value, data_type, result = macro.evaluate(expression)
            if result != Error.NO_ERROR:
                return bits8, result
            if data_type == macro.FIELD_LOOKUP:
                if value not in cls.VALID_VALUE:
                    return bits8, Error.BITS_INVALID_BIT
                bits8.set_name(expression, value)
        return bits8, Error.NO_ERROR
