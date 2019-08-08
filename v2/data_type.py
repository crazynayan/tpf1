import re
from v2.errors import Error


class DataType:
    DATA_TYPES = {'X': 1, 'C': 1, 'H': 2, 'F': 4, 'D': 8, 'FD': 8, 'B': 1, 'P': 1, 'Z': 1, 'A': 4, 'Y': 2}

    def __init__(self, data_type=None, **kwargs):
        data_type = 'X' if data_type is None else data_type.upper()
        if data_type not in self.DATA_TYPES:
            raise TypeError
        self.data_type = data_type
        self.input = kwargs['input'] if 'input' in kwargs else None
        self.bytes = kwargs['bytes'] if 'bytes' in kwargs else None

    @property
    def data_type_object(self):
        if self.input is not None:
            return eval(f"{self.data_type}DataType(input=self.input)")
        if self.bytes is not None:
            return eval(f"{self.data_type}DataType(bytes=self.bytes)")
        raise ValueError

    @property
    def default_length(self):
        return self.DATA_TYPES[self.data_type] if self.bytes is None else len(self.bytes)

    @property
    def length(self):
        return self.data_type_object.length

    @property
    def value(self):
        return self.data_type_object.value

    def to_bytes(self):
        return self.data_type_object.to_bytes()

    def from_bytes(self):
        return self.data_type_object.from_bytes()


class CDataType(DataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'C'

    @property
    def length(self):
        return len(self.input) if self.input is not None else self.default_length

    @property
    def value(self):
        return int.from_bytes(bytes(self.input, encoding='cp037'), 'big', signed=False) \
            if self.input is not None else self.from_bytes()

    def to_bytes(self):
        self.bytes = bytes(self.input, encoding='cp037')
        return self.bytes

    def from_bytes(self):
        return self.bytes.decode(encoding='cp037')


class XDataType(DataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'X'

    @property
    def length(self):
        return -(-len(self.input) // 2) if self.input is not None else self.default_length

    @property
    def value(self):
        return int(self.input, 16) if self.input is not None else self.from_bytes()

    def to_bytes(self):
        self.bytes = self.value.to_bytes(self.length, 'big', signed=False)
        return self.bytes

    def from_bytes(self):
        return int.from_bytes(self.bytes, 'big', signed=False)


class BDataType(DataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'B'

    @property
    def length(self):
        return -(-len(self.input) // 8) if self.input is not None else self.default_length

    @property
    def value(self):
        return int(self.input, 2) if self.input is not None else self.from_bytes()

    def to_bytes(self):
        self.bytes = self.value.to_bytes(self.length, 'big', signed=False)
        return self.bytes

    def from_bytes(self):
        return int.from_bytes(self.bytes, 'big', signed=False)


class PDataType(DataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'P'

    @property
    def length(self):
        if self.input is None:
            return self.default_length
        length_input = len(self.input) + 1 if self.input[0] not in ['+', '-'] else len(self.input)
        return -(-length_input // 2)

    @property
    def value(self):
        return int(self.input) if self.input is not None else self.from_bytes()

    def to_bytes(self):
        packed_data = self.input[1:] if self.input[0] in ['+', '-'] else self.input
        packed_data = packed_data + 'D' if self.input[0] == '-' else packed_data + 'C'
        self.bytes = int(packed_data, 16).to_bytes(self.length, 'big', signed=False)
        return self.bytes

    def from_bytes(self):
        sign = '-' if self.bytes[-1] & 0x0F == 0x0D else '+'
        number = int.from_bytes(self.bytes, 'big', signed=False)
        return int(f"{sign}{number >> 4:0x}")


class ZDataType(DataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'Z'

    @property
    def length(self):
        if self.input is None:
            return self.default_length
        return len(self.input) - 1 if self.input[0] in ['+', '-'] else len(self.input)

    @property
    def value(self):
        return int(self.input) if self.input is not None else self.from_bytes()

    def to_bytes(self):
        zoned_data = self.input[1:] if self.input[0] in ['+', '-'] else self.input
        sign = 0xD0 if self.input[0] == '-' else 0xC0
        self.bytes = bytearray(zoned_data, 'cp037')
        self.bytes[-1] = self.bytes[-1] & 0x0F | sign
        return self.bytes

    def from_bytes(self):
        sign = '-' if self.bytes[-1] & 0xF0 == 0xD0 else '+'
        numeric_bytes = self.bytes.copy()
        numeric_bytes[-1] |= 0xF0
        return int(f"{sign}{numeric_bytes.decode(encoding='cp037')}")


class NumericDataType(DataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def length(self):
        return self.default_length

    @property
    def value(self):
        return int(self.input) if self.input is not None else self.from_bytes()

    def to_bytes(self):
        self.bytes = self.value.to_bytes(self.length, 'big', signed=False)
        return self.bytes

    def from_bytes(self):
        return int.from_bytes(self.bytes, 'big', signed=True)


class FDataType(NumericDataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'F'


class HDataType(NumericDataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'H'


class FDDataType(NumericDataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'FD'


class DDataType(NumericDataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'D'


class ADataType(NumericDataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'A'


class YDataType(NumericDataType):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_type = 'Y'


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
    def split_operand(operand):
        # Returns up to 3 elements that are first divided by ( and then by a , and then by a )
        return next(iter(re.findall(r"^([^(]+)\(*([^,)]*),*([^)]*)\)*", operand)))

    def set_base_dsp_by_name(self, name, macro):
        length = 0
        if name.isdigit() or len(re.split(r"['+-]", name)) > 1:
            dsp, result = macro.get_value(name)
            if result != Error.NO_ERROR:
                return length, result
            base = Register('R0')
            name = 'R0_AREA'
        else:
            try:
                dsp = macro.data_map[name].dsp
            except KeyError:
                return length, Error.FBD_INVALID_KEY
            length = macro.data_map[name].length
            try:
                base = macro.files[macro.data_map[name].macro].base
            except KeyError:
                return length, Error.FBD_INVALID_KEY_BASE
        self.name = name
        self.dsp = dsp
        self.base = base
        return length, Error.NO_ERROR

    def set_base_dsp_by_operands(self, base, dsp, macro, length):
        # Set base register
        self.base = Register(base)
        if not self.base.is_valid():
            return Error.FBD_INVALID_BASE
        # Set displacement
        self.dsp, result = macro.get_value(dsp)
        if result != Error.NO_ERROR:
            return result
        if not isinstance(self.dsp, int) or not 0 <= self.dsp <= 4095:
            return Error.FBD_INVALID_DSP
        # Set name
        possible_name = macro.get_field_name(self.base, self.dsp, length)
        self.name = self.base.reg + '_AREA' if possible_name is None else possible_name
        return Error.NO_ERROR


class FieldBaseDsp(Field):
    def __init__(self):
        super().__init__()

    def set(self, operand, macro, length=1):
        operand1, operand2, error = self.split_operand(operand)
        if error:
            result = Error.FBD_NO_LEN
        elif not operand2:
            _, result = self.set_base_dsp_by_name(operand1, macro)
        else:
            result = self.set_base_dsp_by_operands(operand2, operand1, macro, length)
        return result


class FieldIndex(Field):
    def __init__(self):
        super().__init__()
        self.index = None

    def set(self, operand, macro, length):
        operand1, operand2, operand3 = self.split_operand(operand)
        if not operand2 and not operand3:
            _, result = self.set_base_dsp_by_name(operand1, macro)
        elif not operand3:
            result = self.set_base_dsp_by_operands(operand2, operand1, macro, length)
        elif not operand2:
            result = self.set_base_dsp_by_operands(operand3, operand1, macro, length)
        else:
            result = self.set_base_dsp_by_operands(operand3, operand1, macro, length)
            if result == Error.NO_ERROR:
                self.index = Register(operand2)
                result = Error.NO_ERROR if self.index.is_valid() else Error.FX_INVALID_INDEX
        return result


class FieldLen(Field):
    def __init__(self):
        super().__init__()
        self.length = 0

    def set(self, operand, macro, max_len):
        operand1, operand2, operand3 = self.split_operand(operand)
        length = -1
        if not operand3:
            length, result = self.set_base_dsp_by_name(operand1, macro)
            if operand2 and result == Error.NO_ERROR:
                length, result = macro.get_value(operand2)
        elif not operand2:
            result = Error.FL_LEN_REQUIRED
        else:
            length, result = macro.get_value(operand2)
            if result == Error.NO_ERROR:
                result = self.set_base_dsp_by_operands(operand3, operand1, macro, length)
        if result == Error.NO_ERROR:
            if isinstance(length, int) and 0 <= length <= max_len:
                self.length = length if length > 0 else 1
            else:
                result = Error.FL_INVALID_LEN
        return result


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

    def set_from_number(self, number):
        value = 0x80
        while value > 0:
            if value & number != 0:
                self.on_by_value(value)
            value = value >> 1

    def set(self, operand, macro):
        number, result = macro.get_value(operand)
        if result == Error.NO_ERROR:
            result = Error.NO_ERROR if isinstance(number, int) and 0 <= number <= 255 else Error.BITS_INVALID_NUMBER
            if result == Error.NO_ERROR:
                self.set_from_number(number)
                # Add the name from the expression
                for expression in re.split(f"[+-]", operand):
                    value, data_type, result = macro.evaluate(expression)
                    if result == Error.NO_ERROR and data_type == macro.FIELD_LOOKUP:
                        if value in self.VALID_VALUE:
                            self.set_name(expression, value)
                        else:
                            result = Error.BITS_INVALID_BIT
        return result
