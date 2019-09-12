import re
from typing import Optional, Tuple

from v2.data_type import Register
from v2.errors import Error
from v2.macro import SegmentMacro


class Field:
    def __init__(self):
        self.name: Optional[str] = None
        self.base: Optional[Register] = None
        self.dsp: int = -1

    def __repr__(self) -> str:
        return f"{self.name}:{self.base}+{self.dsp}"

    @staticmethod
    def split_operand(operand: str) -> list:
        # Returns up to 3 elements that are first divided by ( and then by a , and then by a )
        return next(iter(re.findall(r"^([^(]+)\(*([^,)]*),*([^)]*)\)*", operand)))

    def set_base_dsp_by_name(self, name: str, macro: SegmentMacro) -> Tuple[int, str]:
        length = 0
        if name.isdigit() or set("'+-").intersection(set(name)):
            dsp, result = macro.get_value(name)
            if result != Error.NO_ERROR:
                return length, result
            possible_name = next(iter(re.split(r"['+-]", name)))
            if not name.isdigit() and possible_name in macro.data_map:
                # Field type of NAME+L'NAME
                base = Register(macro.get_base(macro.data_map[possible_name].name))
                name = possible_name
            else:
                base = Register('R0')
                name = 'R0_AREA'
        else:
            try:
                dsp = macro.data_map[name].dsp
            except KeyError:
                return length, Error.FBD_INVALID_KEY
            length = macro.data_map[name].length
            try:
                base = Register(macro.get_base(macro.data_map[name].name))
            except (KeyError, StopIteration):
                return length, Error.FBD_INVALID_KEY_BASE
        self.name = name
        self.dsp = dsp
        self.base = base
        return length, Error.NO_ERROR

    def set_base_dsp_by_operands(self, base: str, dsp: str, macro: SegmentMacro, length: int) -> str:
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

    def set(self, operand: str, macro: SegmentMacro, length: int = 1) -> str:
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

    def set(self, operand: str, macro: SegmentMacro, length: int) -> str:
        operand1, operand2, operand3 = self.split_operand(operand)
        if not operand2 and not operand3:
            # Single label like EBW000
            _, result = self.set_base_dsp_by_name(name=operand1, macro=macro)
        elif not operand3:
            # Note: In TPF these types are with no base but with index register set.
            # In our tool we have flipped this. So there would be no index but the base would be present.
            if operand1.isdigit() or set("+-*").intersection(operand1):
                # Base_dsp 34(R5) or expression with base EBW008-EBW000(R9)
                result = self.set_base_dsp_by_operands(base=operand2, dsp=operand1, macro=macro, length=length)
            else:
                # Label with index EBW000(R14) or EBW000(R14,)
                _, result = self.set_base_dsp_by_name(name=operand1, macro=macro)
                if result == Error.NO_ERROR:
                    self.index = Register(operand2)
                    result = Error.NO_ERROR if self.index.is_valid() else Error.FX_INVALID_INDEX
        elif not operand2:
            # Base_dsp with no index 10(,R5)
            result = self.set_base_dsp_by_operands(operand3, operand1, macro, length)
        else:
            # Base_dsp with index 10(R3,R5)
            result = self.set_base_dsp_by_operands(operand3, operand1, macro, length)
            if result == Error.NO_ERROR:
                self.index = Register(operand2)
                result = Error.NO_ERROR if self.index.is_valid() else Error.FX_INVALID_INDEX
        return result


class FieldLen(Field):
    def __init__(self):
        super().__init__()
        self.length = 0

    def set(self, operand: str, macro: SegmentMacro, max_len: int) -> str:
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
    def __init__(self, name: str, value: int, on: bool = False):
        self.name = name
        self.value = value
        self.on = on

    def __repr__(self) -> str:
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

    def __repr__(self) -> str:
        bit_text = [str(bit) for _, bit in self.__dict__.items()]
        return '+'.join(bit_text)

    @property
    def value(self) -> int:
        return sum(bit.value for _, bit in self.__dict__.items() if bit.on)

    @property
    def text(self) -> str:
        bit_text = [bit.name for _, bit in self.__dict__.items() if bit.on]
        if len(bit_text) < 5:
            return '+'.join(bit_text)
        else:
            bit_text = [bit.name for _, bit in self.__dict__.items() if not bit.on]
            return f"#BITA-{'-'.join(bit_text)}"

    def set_name(self, name: str, value: int) -> None:
        bit = next(bit for _, bit in self.__dict__.items() if bit.value == value)
        bit.name = name

    def bit_by_name(self, name: str) -> Bit:
        return next(bit for _, bit in self.__dict__.items() if bit.name == name)

    def on_by_name(self, name: str) -> None:
        bit = next(bit for _, bit in self.__dict__.items() if bit.name == name)
        bit.on = True

    def off_by_name(self, name: str) -> None:
        bit = next(bit for _, bit in self.__dict__.items() if bit.name == name)
        bit.on = False

    def on_by_value(self, value: int) -> None:
        bit = next(bit for _, bit in self.__dict__.items() if bit.value == value)
        bit.on = True

    def off_by_value(self, value: int) -> None:
        bit = next(bit for _, bit in self.__dict__.items() if bit.value == value)
        bit.on = False

    def set_from_number(self, number: int) -> None:
        value = 0x80
        while value > 0:
            if value & number != 0:
                self.on_by_value(value)
            value = value >> 1

    def set(self, operand: str, macro: SegmentMacro) -> str:
        number, result = macro.get_value(operand)
        if result == Error.NO_ERROR:
            result = Error.NO_ERROR if isinstance(number, int) and 0 <= number <= 255 else Error.BITS_INVALID_NUMBER
            if result == Error.NO_ERROR:
                self.set_from_number(number)
                # Add the name from the expression
                for expression in re.split(f"[+-]", operand):
                    field, lookup_result = macro.lookup(expression)
                    if lookup_result == Error.NO_ERROR:
                        if field.dsp in self.VALID_VALUE:
                            self.set_name(expression, field.dsp)
                        else:
                            result = Error.BITS_INVALID_BIT
        return result
