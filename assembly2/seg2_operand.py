import re
from typing import Optional, List

from assembly2.seg1_directive import DirectiveImplementation
from utils.data_type import Register
from utils.errors import RegisterInvalidError, FieldDspInvalidError, FieldLengthInvalidError, BitsInvalidError


class Bit:
    def __init__(self, name: str, value: int, on: bool = False):
        self.name = name
        self.value = value
        self.on = on

    def __repr__(self) -> str:
        return f"{self.name}=0x{self.value:02x}"


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
        bit_text = [str(bit) for _, bit in self.__dict__.items() if bit.on]
        if len(bit_text) < 5:
            return ' + '.join(bit_text)
        else:
            bit_text = [str(bit) for _, bit in self.__dict__.items() if not bit.on]
            return self.PREFIX + 'A - ' + ' - '.join(bit_text)

    @property
    def value(self) -> int:
        return sum(bit.value for _, bit in self.__dict__.items() if bit.on)

    def set_name(self, name: str, value: int) -> None:
        bit = next((bit for _, bit in self.__dict__.items() if bit.value == value), None)
        if bit is not None:
            bit.name = name
        return


class FieldBaseDsp:
    def __init__(self, name: str, base: Register, dsp: int):
        self.name: str = name
        self.base: Register = base
        self.dsp: int = dsp


class InstructionOperand(DirectiveImplementation):
    def __init__(self, name):
        super().__init__(name)

    @staticmethod
    def split_operand(operand: str) -> List[str]:
        # Returns up to 3 elements that are first divided by ( and then by a , and then by a )
        return next(iter(re.findall(r"^([^(]+)\(*([^,)]*),*([^)]*)\)*", operand)))

    def _get_field_by_name(self, name: str) -> FieldBaseDsp:
        dsp = self.get_value(name)
        possible_name = next(iter(re.split(r"['+-]", name)))
        if self.check(possible_name):
            # Field type of NAME+L'NAME or NAME
            base = self.get_base(self.lookup(possible_name).name)
            name = possible_name
        else:
            base = Register('R0')
            name = 'R0_AREA'
        return FieldBaseDsp(name, base, dsp)

    def _get_field_by_base_dsp(self, base: str, dsp: str, length: Optional[int] = None) -> FieldBaseDsp:
        # Set base register
        base = Register(base)
        if not base.is_valid():
            raise RegisterInvalidError
        # Set displacement
        dsp = self.get_value(dsp)
        if not 0 <= dsp <= 4095:
            raise FieldDspInvalidError
        # Set name
        possible_name = self.get_field_name(base, dsp, length)
        name = base.reg + '_AREA' if possible_name is None else possible_name
        return FieldBaseDsp(name, base, dsp)

    def field_base_dsp(self, operand: str) -> FieldBaseDsp:
        operand1, operand2, error = self.split_operand(operand)
        if error:
            raise FieldLengthInvalidError
        return self._get_field_by_name(operand1) if not operand2 else self._get_field_by_base_dsp(operand2, operand1)

    def get_bits(self, operand: str) -> Bits:
        number = self.get_value(operand)
        if not 0 <= number <= 255:
            raise BitsInvalidError
        # Initialize bits and turn ON relevant bits
        bits = Bits()
        for index, bit in enumerate(f'{number:08b}'):
            if bit == '1':
                bit_n = getattr(bits, 'bit' + str(index))
                bit_n.on = True
        # Set the name
        for expression in re.split(f"[+-]", operand):
            if self.check(expression):
                value = self.evaluate(expression)
                bits.set_name(expression, value)
        return bits
