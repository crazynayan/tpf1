from copy import deepcopy

from assembly2.seg3_ins_type import RegisterRegister, RegisterFieldIndex, RegisterData, RegisterDataField, \
    RegisterRegisterField, FieldLenField, FieldData, BranchCondition, RegisterBranch, BranchConditionRegister, \
    FieldBits, RegisterLabel, FieldLenFieldLen
from execution.state import State
from utils.data_type import DataType
from utils.errors import PackExecutionError


class LoadStore(State):
    def load_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        return self.next_label(node)

    def load_test_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        return self.next_label(node)

    def load_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 4)
        self.regs.set_value(value, node.reg)
        return self.next_label(node)

    def load_address(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        self.regs.set_value(address, node.reg)
        return self.next_label(node)

    def store_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 4)
        return self.next_label(node)

    def load_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 2)
        self.regs.set_value(value, node.reg)
        return self.next_label(node)

    def load_halfword_immediate(self, node: RegisterData) -> str:
        self.regs.set_value(node.data, node.reg)
        return self.next_label(node)

    def store_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 2)
        return self.next_label(node)

    def insert_character(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.vm.get_bytes(address)
        self.regs.set_bytes_from_mask(byte, node.reg, 0b0001)
        return self.next_label(node)

    def insert_character_mask(self, node: RegisterDataField) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        byte = self.vm.get_bytes(address, bin(node.data).count('1'))
        self.regs.set_bytes_from_mask(byte, node.reg, node.data)
        self.set_number_cc(DataType('F', bytes=byte).value)
        return self.next_label(node)

    def store_character(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.regs.get_bytes_from_mask(node.reg, 0b0001)
        self.vm.set_bytes(byte, address)
        return self.next_label(node)

    def store_character_mask(self, node: RegisterDataField) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        byte = self.regs.get_bytes_from_mask(node.reg, node.data)
        self.vm.set_bytes(byte, address, bin(node.data).count('1'))
        return self.next_label(node)

    # noinspection DuplicatedCode
    def load_multiple(self, node: RegisterRegisterField) -> str:
        reg = node.reg1.reg
        address = self.regs.get_address(node.field.base, node.field.dsp)
        while True:
            value = self.vm.get_value(address)
            self.regs.set_value(value, reg)
            if reg == node.reg2.reg:
                break
            address += self.regs.LEN
            reg = self.regs.next_reg(reg)
        return self.next_label(node)

    # noinspection DuplicatedCode
    def store_multiple(self, node: RegisterRegisterField) -> str:
        reg = node.reg1.reg
        address = self.regs.get_address(node.field.base, node.field.dsp)
        while True:
            value = self.regs.get_value(reg)
            self.vm.set_value(value, address)
            if reg == node.reg2.reg:
                break
            address += self.regs.LEN
            reg = self.regs.next_reg(reg)
        return self.next_label(node)


class ArithmeticShiftAlgebraic(State):
    def add_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1) + self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        return self.next_label(node)

    def add_halfword_immediate(self, node: RegisterData) -> str:
        value = self.regs.get_value(node.reg) + node.data
        self.regs.set_value(value, node.reg)
        self.set_number_cc(value)
        return self.next_label(node)

    def subtract_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1) - self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        return self.next_label(node)


class MoveLogicControl(State):
    def move_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index)
            self.vm.set_byte(byte, target_address + index)
        return self.next_label(node)

    def move_immediate(self, node: FieldData) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.set_value(node.data, address, 1)
        return self.next_label(node)

    @staticmethod
    def branch(node: BranchCondition) -> str:
        return node.branch.name

    def branch_on_count_register(self, node: RegisterRegister) -> str:
        if node.reg2.reg != 'R0':
            raise TypeError
        value = self.regs.get_value(node.reg1) - 1
        self.regs.set_value(value, node.reg1)
        return self.next_label(node)

    def branch_and_save(self, node: RegisterBranch) -> str:
        bas = self.seg.bas
        value = bas.dumps(node.fall_down)
        self.regs.set_value(value, node.reg)
        return node.branch.name

    def branch_return(self, node: BranchConditionRegister) -> str:
        bas = self.seg.bas
        value = self.regs.get_value(node.reg)
        return bas.loads(value)


class CompareLogical(State):
    def compare_logical_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        source_value = self.vm.get_unsigned_value(target_address, node.field_len.length + 1)
        target_value = self.vm.get_unsigned_value(source_address, node.field_len.length + 1)
        self.set_number_cc(target_value - source_value)
        return self.next_label(node)

    def compare_logical_immediate(self, node: FieldData) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        value = self.vm.get_unsigned_value(address, 1)
        self.set_number_cc(value - node.data)
        return self.next_label(node)

    def compare_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 2)
        reg_value = self.regs.get_value(node.reg)
        self.set_number_cc(reg_value - value)
        return self.next_label(node)


class LogicalUsefulConversion(State):
    def or_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1)
        value |= self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_zero_cc(value)
        return self.next_label(node)

    def and_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address)
        value &= self.regs.get_value(node.reg)
        self.regs.set_value(value, node.reg)
        self.set_zero_cc(value)
        return self.next_label(node)

    def xor_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index) ^ self.vm.get_byte(target_address + index)
            self.vm.set_byte(byte, target_address + index)
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return self.next_label(node)

    def or_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            target_byte = self.vm.get_byte(target_address + index)
            byte = self.vm.get_byte(source_address + index) | target_byte
            if byte != target_byte:
                self.vm.set_byte(byte, target_address + index)
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return self.next_label(node)

    def and_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index) & self.vm.get_byte(target_address + index)
            self.vm.set_byte(byte, target_address + index)
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return self.next_label(node)

    def or_immediate(self, node: FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.or_bit(address, node.bits.value)
        self.set_zero_cc(self.vm.get_value(address, 1))
        return self.next_label(node)

    def and_immediate(self, node: FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.and_bit(address, node.bits.value)
        self.set_zero_cc(self.vm.get_value(address, 1))
        return self.next_label(node)

    def test_mask(self, node: FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        if self.vm.all_bits_off(address, node.bits.value):
            self.cc = 0
        elif self.vm.all_bits_on(address, node.bits.value):
            self.cc = 3
        else:
            self.cc = 1
        return self.next_label(node)

    def execute(self, node: RegisterLabel) -> str:
        value = self.regs.get_value(node.reg) & 0xFF if node.reg.reg != 'R0' else 0
        exec_node = deepcopy(self.seg.nodes[node.ex_label])
        if isinstance(exec_node, FieldLenField):
            exec_node.field_len.length |= value
            self.ex_command(exec_node)
        elif isinstance(exec_node, FieldLenFieldLen):
            value1 = value >> 4
            exec_node.field_len1.length |= value1
            value2 = value & 0x0F
            exec_node.field_len2.length |= value2
            self.ex_command(exec_node)
        elif isinstance(exec_node, FieldData):
            exec_node.data |= value
            self.ex_command(exec_node)
        elif isinstance(exec_node, FieldBits):
            value |= exec_node.bits.value
            exec_node.bits.set_value(value)
            self.ex_command(exec_node)
        else:
            raise TypeError
        return self.next_label(node)

    def pack(self, node: FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        source_bytes = self.vm.get_bytes(source_address, node.field_len2.length + 1)
        number = DataType('X', bytes=source_bytes).decode
        if not number.isdigit():
            raise PackExecutionError
        packed_bytes = DataType('P', input=number).to_bytes(node.field_len1.length + 1)
        self.vm.set_bytes(packed_bytes, target_address, node.field_len1.length + 1)
        return self.next_label(node)

    def convert_binary(self, node: RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        packed_bytes = self.vm.get_bytes(address, 8)
        value = DataType('P', bytes=packed_bytes).value
        self.regs.set_value(value, node.reg)
        return self.next_label(node)

    def convert_decimal(self, node: RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        packed_bytes = DataType('P', input=str(value)).to_bytes(8)
        self.vm.set_bytes(packed_bytes, address, 8)
        return self.next_label(node)

    def unpack(self, node: FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        packed_bytes = self.vm.get_bytes(source_address, node.field_len2.length + 1)
        value = DataType('P', bytes=packed_bytes).value
        zoned_bytes = DataType('Z', input=str(value)).to_bytes(node.field_len1.length + 1)
        self.vm.set_bytes(zoned_bytes, target_address, node.field_len1.length + 1)
        return self.next_label(node)


class DecimalArithmeticComplex(State):
    pass


class Instruction(LoadStore, ArithmeticShiftAlgebraic, MoveLogicControl, CompareLogical, LogicalUsefulConversion,
                  DecimalArithmeticComplex):
    pass
