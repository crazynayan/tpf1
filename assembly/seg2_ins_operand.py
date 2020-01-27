import re
from typing import Optional, List

from assembly.mac0_generic import LabelReference
from assembly.seg1_directive import DirectiveImplementation
from config import config
from utils.data_type import Register
from utils.errors import RegisterInvalidError, FieldDspInvalidError, FieldLengthInvalidError, BitsInvalidError, \
    RegisterIndexInvalidError, BranchInvalidError


class Label:
    SEPARATOR = '.'

    def __init__(self, name: str, separator: Optional[str] = None):
        self.name: str = name
        self.index: int = 0
        self.separator: str = self.SEPARATOR if separator is None else separator

    def __repr__(self) -> str:
        return self.name if self.index == 0 else f"{self.name}{self.separator}{self.index}"


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
        if not bit_text:
            return '0'
        if len(bit_text) < 5:
            return '+'.join(bit_text)
        bit_text = [str(bit) for _, bit in self.__dict__.items() if not bit.on]
        return self.PREFIX + 'A-' + '-'.join(bit_text)

    @property
    def value(self) -> int:
        return sum(bit.value for _, bit in self.__dict__.items() if bit.on)

    def set_value(self, value: int) -> None:
        for index, bit in enumerate(f'{value:08b}'):
            bit_n = getattr(self, 'bit' + str(index))
            bit_n.on = True if bit == '1' else False

    def set_name(self, name: str, value: int) -> None:
        bit = next((bit for _, bit in self.__dict__.items() if bit.value == value), None)
        if bit is not None:
            bit.name = name
        return

    def bit_by_name(self, name: str) -> Optional[Bit]:
        return next((bit for _, bit in self.__dict__.items() if bit.name == name), None)


class FieldBaseDsp:

    def __init__(self, name: str, base: Register, dsp: int):
        self.name: str = name
        self.base: Register = base
        self.dsp: int = dsp

    def __repr__(self) -> str:
        return f"{self.name}({self.base}+{self.dsp})"


class FieldIndex(FieldBaseDsp):

    def __init__(self, field: FieldBaseDsp, index: Register):
        super().__init__(field.name, field.base, field.dsp)
        self.index: Register = index

    def __repr__(self) -> str:
        return f"{self.name}({self.base}+{self.dsp}+{self.index})"


class FieldLen(FieldBaseDsp):

    def __init__(self, field: FieldBaseDsp, length: int):
        super().__init__(field.name, field.base, field.dsp)
        self.length: int = length

    def __repr__(self) -> str:
        return f"{self.name}({self.base}+{self.dsp},{self.length + 1})"


class InstructionOperand(DirectiveImplementation):
    def __init__(self, name):
        super().__init__(name)

    @staticmethod
    def split_operand(operand: str) -> List[str]:
        # Returns up to 3 elements that are first divided by ( and then by a , and then by a )
        return next(iter(re.findall(r"^([^(]+)\(*([^,)]*),*([^)]*)\)*", operand)))

    def _get_field_by_name(self, name: str) -> FieldBaseDsp:
        dsp = self.get_value(name)
        possible_name = next(iter(re.split(r"['+*/-]", name)))
        if self.is_based(name):
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

    def _literal(self, operand: str) -> LabelReference:
        literal = self._dsdc(operand, literal=True)
        dsp = self.data.next_literal + config.F4K
        self.data.literal.extend(literal.data * literal.duplication_factor)
        label = f"L{Label.SEPARATOR * 2}{dsp:05X}"
        label_ref = self.add_label(label, dsp, literal.length, self.name)
        return label_ref

    def field_base_dsp(self, operand: str) -> FieldBaseDsp:
        if operand.startswith('='):
            label_ref = self._literal(operand[1:])
            return FieldBaseDsp(label_ref.label, self.get_base(self.name), label_ref.dsp)
        operand1, operand2, error = self.split_operand(operand)
        if error:
            raise FieldLengthInvalidError
        if operand2:
            return self._get_field_by_base_dsp(base=operand2, dsp=operand1)
        return self._get_field_by_name(operand1)

    def get_bits(self, operand: str) -> Bits:
        number = self.get_value(operand)
        if not 0 <= number <= 255:
            raise BitsInvalidError
        # Initialize bits and turn ON relevant bits
        bits = Bits()
        bits.set_value(number)
        # Set the name
        for expression in re.split(f"[+-]", operand):
            if self.check(expression):
                value = self.evaluate(expression)
                bits.set_name(expression, value)
        return bits

    def field_index(self, operand: str) -> FieldIndex:
        index = Register('R0')
        if operand.startswith('='):
            label_ref = self._literal(operand[1:])
            field = FieldBaseDsp(label_ref.label, self.get_base(self.name), label_ref.dsp)
            return FieldIndex(field, index)
        operand1, operand2, operand3 = self.split_operand(operand)
        if not operand2 and not operand3:
            # Single label like EBW000
            field: FieldBaseDsp = self._get_field_by_name(name=operand1)
        elif not operand3:
            # Note: In TPF these types are with no base but with index register set.
            # In our tool we have flipped this. So there would be no index but the base would be present.
            if operand1.isdigit() or set("+-*").intersection(operand1):
                # Base_dsp 34(R5) or expression with base EBW008-EBW000(R9)
                field: FieldBaseDsp = self._get_field_by_base_dsp(base=operand2, dsp=operand1)
            else:
                # Label with index EBW000(R14) or EBW000(R14,)
                field: FieldBaseDsp = self._get_field_by_name(name=operand1)
                index = Register(operand2)
                if not index.is_valid():
                    raise RegisterIndexInvalidError
        elif not operand2:
            # Base_dsp with no index 10(,R5)
            field: FieldBaseDsp = self._get_field_by_base_dsp(base=operand3, dsp=operand1)
        else:
            # Base_dsp with index 10(R3,R5)
            field = self._get_field_by_base_dsp(base=operand3, dsp=operand1)
            index = Register(operand2)
            if not index.is_valid():
                raise RegisterIndexInvalidError
        return FieldIndex(field, index)

    def field_len(self, operand: str, max_len: int) -> FieldLen:
        if operand.startswith('='):
            label_ref = self._literal(operand[1:])
            field = FieldBaseDsp(label_ref.label, self.get_base(self.name), label_ref.dsp)
            return FieldLen(field, label_ref.length - 1)
        operand1, operand2, operand3 = self.split_operand(operand)
        if not operand3:
            # EBW000 or EBW000(L'EBW000)
            field = self._get_field_by_name(operand1)
            if operand2:
                length = self.get_value(operand2)
            else:
                length = self.lookup(field.name).length
        elif not operand2:
            raise FieldLengthInvalidError
        else:
            # 10(3,R10)
            length = self.get_value(operand2)
            field = self._get_field_by_base_dsp(base=operand3, dsp=operand1)
        if 0 <= length <= max_len:
            # Length in machine code is always saved as 1 less.
            length = length - 1 if length else 0
        else:
            raise FieldLengthInvalidError
        return FieldLen(field, length)

    def get_branch(self, operand: str) -> FieldIndex:
        field = self.field_index(operand)
        if not self.is_branch(field.name):
            raise BranchInvalidError
        return field
