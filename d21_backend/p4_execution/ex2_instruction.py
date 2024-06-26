from copy import deepcopy
from datetime import datetime, timedelta
from typing import List

from d21_backend.config import config
from d21_backend.p1_utils.data_type import DataType, Register, PDataType
from d21_backend.p1_utils.errors import PackExecutionError, BctExecutionError, ExExecutionError
from d21_backend.p2_assembly.seg3_ins_type import RegisterRegister, RegisterFieldIndex, RegisterData, RegisterDataField, \
    RegisterRegisterField, FieldLenField, FieldData, BranchCondition, RegisterBranch, BranchConditionRegister, \
    FieldBits, FieldLenFieldLen, FieldSingle, RegisterRegisterBranch, FieldSingleBaseDsp,FieldLenFieldData
from d21_backend.p4_execution.ex1_state import State


class LoadStore(State):
    def load_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.trace_data.set_signed_value1(value)
        return node.fall_down

    def load_positive_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        value = value if value >= 0 else value * -1
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        self.trace_data.set_signed_value1(value)
        return node.fall_down

    def load_negative_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        value = value if value <= 0 else value * -1
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        self.trace_data.set_signed_value1(value)
        return node.fall_down

    def load_complement_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        value = value * -1
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        self.trace_data.set_signed_value1(value)
        return node.fall_down

    def load_test_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        self.trace_data.set_signed_value1(value)
        return node.fall_down

    def load_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 4)
        self.regs.set_value(value, node.reg)
        self.trace_data.set_signed_value1(value)
        if self.vm.is_address_valid(value):
            self.trace_data.set_reg_pointer(self.vm.get_value(value))
        return node.fall_down

    def load_grande(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 8)
        self.regs.set_value64(value, node.reg)
        return node.fall_down

    def load_address(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        self.regs.set_value(address, node.reg)
        self.trace_data.set_signed_value1(address)
        if self.vm.is_address_valid(address):
            self.trace_data.set_reg_pointer(self.vm.get_value(address))
        return node.fall_down

    def store_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 4)
        self.trace_data.set_signed_value1(value)
        return node.fall_down

    def store_grande(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 8)
        return node.fall_down

    def load_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 2)
        self.regs.set_value(value, node.reg)
        self.trace_data.set_signed_value1(value)
        return node.fall_down

    def load_halfword_immediate(self, node: RegisterData) -> str:
        self.regs.set_value(node.data, node.reg)
        self.trace_data.set_signed_value1(node.data)
        return node.fall_down

    def store_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 2)
        self.trace_data.set_signed_value1(value)
        return node.fall_down

    def insert_character(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte: bytearray = self.vm.get_bytes(address)
        self.regs.set_bytes_from_mask(byte, node.reg, 0b0001)
        self.trace_data.set_byte_array1(byte)
        return node.fall_down

    def load_logical_character(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte: int = self.vm.get_unsigned_value(address, length=1)
        self.regs.set_value(byte, node.reg)
        self.trace_data.set_unsigned_value1(byte, 1)
        return node.fall_down

    def insert_character_mask(self, node: RegisterDataField) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        byte: bytearray = self.vm.get_bytes(address, bin(node.data).count('1'))
        self.regs.set_bytes_from_mask(byte, node.reg, node.data)
        self.set_number_cc(DataType('F', bytes=byte).value)
        self.trace_data.set_byte_array1(byte)
        return node.fall_down

    def store_character(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.regs.get_bytes_from_mask(node.reg, 0b0001)
        self.vm.set_bytes(byte, address)
        self.trace_data.set_byte_array1(byte)
        return node.fall_down

    def store_character_mask(self, node: RegisterDataField) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        byte = self.regs.get_bytes_from_mask(node.reg, node.data)
        self.vm.set_bytes(byte, address, bin(node.data).count('1'))
        self.trace_data.set_byte_array1(byte)
        return node.fall_down

    # noinspection DuplicatedCode
    def load_multiple(self, node: RegisterRegisterField) -> str:
        reg = node.reg1.reg
        address = self.regs.get_address(node.field.base, node.field.dsp)
        while True:
            value = self.vm.get_value(address)
            self.regs.set_value(value, reg)
            if reg == node.reg2.reg:
                break
            address += config.REG_BYTES
            reg = self.regs.next_reg(reg)
        return node.fall_down

    # noinspection DuplicatedCode
    def store_multiple(self, node: RegisterRegisterField) -> str:
        reg = node.reg1.reg
        address = self.regs.get_address(node.field.base, node.field.dsp)
        while True:
            value = self.regs.get_value(reg)
            self.vm.set_value(value, address)
            if reg == node.reg2.reg:
                break
            address += config.REG_BYTES
            reg = self.regs.next_reg(reg)
        return node.fall_down


class ArithmeticShiftAlgebraic(State):
    def add_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1) + self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        return node.fall_down

    def add_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg) + self.vm.get_value(address, 2)
        self.regs.set_value(value, node.reg)
        self.set_number_cc(value)
        return node.fall_down

    def add_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg) + self.vm.get_value(address, 4)
        self.regs.set_value(value, node.reg)
        self.set_number_cc(value)
        return node.fall_down

    def add_halfword_immediate(self, node: RegisterData) -> str:
        value = self.regs.get_value(node.reg) + node.data
        self.regs.set_value(value, node.reg)
        self.set_number_cc(value)
        return node.fall_down

    def subtract_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1) - self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        return node.fall_down

    def subtract_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg) - self.vm.get_value(address, 4)
        self.regs.set_value(value, node.reg)
        self.set_number_cc(value)
        return node.fall_down

    def subtract_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg) - self.vm.get_value(address, 2)
        self.regs.set_value(value, node.reg)
        self.set_number_cc(value)
        return node.fall_down

    def multiply_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        odd_reg = self.regs.next_reg(node.reg)
        value = self.regs.get_value(odd_reg) * self.vm.get_value(address, 4)
        self.regs.set_double_value(value, node.reg)
        return node.fall_down

    def multiply_register(self, node: RegisterRegister) -> str:
        odd_reg = self.regs.next_reg(node.reg1)
        value = self.regs.get_value(odd_reg) * self.regs.get_value(node.reg2)
        self.regs.set_double_value(value, node.reg1)
        return node.fall_down

    def multiply_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg) * self.vm.get_value(address, 2)
        self.regs.set_value(value, node.reg)
        return node.fall_down

    def multiply_halfword_immediate(self, node: RegisterData) -> str:
        value = self.regs.get_value(node.reg) * node.data
        self.regs.set_value(value, node.reg)
        return node.fall_down

    def divide_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        dividend = self.regs.get_double_value(node.reg)
        divisor = self.vm.get_value(address, 4)
        remainder = dividend % divisor
        quotient = dividend // divisor
        odd_reg = self.regs.next_reg(node.reg)
        self.regs.set_value(remainder, node.reg)
        self.regs.set_value(quotient, odd_reg)
        return node.fall_down

    def divide_register(self, node: RegisterRegister) -> str:
        dividend = self.regs.get_double_value(node.reg1)
        divisor = self.regs.get_value(node.reg2)
        remainder = dividend % divisor
        quotient = dividend // divisor
        odd_reg = self.regs.next_reg(node.reg1)
        self.regs.set_value(remainder, node.reg1)
        self.regs.set_value(quotient, odd_reg)
        return node.fall_down

    def shift_right_double_algebraic(self, node: RegisterFieldIndex) -> str:
        factor = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        value = self.regs.get_double_value(node.reg) >> factor
        self.regs.set_double_value(value, node.reg)
        return node.fall_down

    def shift_left_double_algebraic(self, node: RegisterFieldIndex) -> str:
        factor = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        value = self.regs.get_double_value(node.reg) << factor
        self.regs.set_double_value(value, node.reg)
        return node.fall_down

    def shift_left_algebraic(self, node: RegisterFieldIndex):
        factor = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        value = self.regs.get_value(node.reg) << factor
        self.regs.set_value(value, node.reg)
        return node.fall_down

    def shift_right_algebraic(self, node: RegisterFieldIndex):
        factor = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        value = self.regs.get_value(node.reg) >> factor
        self.regs.set_value(value, node.reg)
        return node.fall_down


class MoveLogicControl(State):
    def move_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        byte_list: List[int] = list()
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index)
            self.vm.set_byte(byte, target_address + index)
            byte_list.append(byte)
        self.trace_data.set_byte_array1(bytearray(byte_list))
        return node.fall_down

    def move_character_long(self, node: RegisterRegister) -> str:
        target_address = self.regs.get_unsigned_value(node.reg1)
        target_reg = self.regs.next_reg(node.reg1)
        target_length = self.regs.get_unsigned_value(target_reg) & 0x00FFFFFF
        source_address = self.regs.get_unsigned_value(node.reg2)
        source_reg = self.regs.next_reg(node.reg2)
        source_length = self.regs.get_unsigned_value(source_reg) & 0x00FFFFFF
        pad_character: int = self.regs.get_bytes_from_mask(source_reg, 0b1000)[0]
        for index in range(source_length):
            byte = self.vm.get_byte(source_address + index)
            self.vm.set_byte(byte, target_address + index)
        for index in range(source_length, target_length):
            self.vm.set_byte(pad_character, target_address + index)
        self.regs.set_value(target_address + target_length, node.reg1)
        self.regs.set_value(source_address + source_length, node.reg2)
        self.regs.set_value(0, target_reg)
        truncated_count = source_length - target_length if source_length > target_length else 0
        self.regs.set_value(truncated_count, source_reg)
        self.regs.set_bytes_from_mask(bytearray([pad_character]), source_reg, 0b1000)
        self.set_number_cc(target_length - source_length)
        return node.fall_down

    def move_numeric(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            source_byte = self.vm.get_byte(source_address + index)
            source_byte &= 0x0F  # Zeroes the zone nibble
            target_byte = self.vm.get_byte(target_address + index)
            target_byte &= 0xF0  # Zeroes the numeric nibble
            target_byte |= source_byte  # OR the numeric nibble from source to target
            self.vm.set_byte(target_byte, target_address + index)
        return node.fall_down

    def move_zone(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            source_byte = self.vm.get_byte(source_address + index)
            source_byte &= 0xF0  # Zeroes the numeric nibble
            target_byte = self.vm.get_byte(target_address + index)
            target_byte &= 0x0F  # Zeroes the zone nibble
            target_byte |= source_byte  # OR the zone nibble from source to target
            self.vm.set_byte(target_byte, target_address + index)
        return node.fall_down

    def move_with_offset(self, node: FieldLenFieldLen) -> str:
        source_length: int = node.field_len2.length + 1
        target_length: int = node.field_len1.length + 1
        # source_address points to the last byte of the source
        source_address: int = self.regs.get_address(node.field_len2.base, node.field_len2.dsp) + source_length - 1
        # target_address points to the last byte of the target
        target_address: int = self.regs.get_address(node.field_len1.base, node.field_len1.dsp) + target_length - 1
        # The loop will copy one nibble at a time form source_address to target_address
        # The loop will execute target_length * 2 - 1 times. If target_length is 5 then the loop will execute 9 times and copy 9 nibbles
        for loop_index in range(target_length * 2 - 1):
            # If loop_index >= source_length * 2 (all source bytes already read), then source_nibble is set to 0 (padding).
            if loop_index >= source_length * 2:
                source_nibble: int = 0
            else:
                source_nibble: int = self.vm.get_byte(source_address)
                # On even loop_index (0,2,4...), read the right nibble from the source_address as the source_nibble.
                if loop_index % 2 == 0:
                    source_nibble &= 0x0F
                else:  # On odd loop_index (1,3,5...), read the left nibble from the source_address and decrement the source_address by 1
                    source_nibble &= 0xF0
                    source_nibble = source_nibble >> 4
                    source_address -= 1
            target_nibble: int = self.vm.get_byte(target_address)
            # On even loop index, write at the left nibble of the target_address and decrement target_address by one
            if loop_index % 2 == 0:
                target_nibble &= 0x0F
                source_nibble = source_nibble << 4
                target_nibble |= source_nibble
                self.vm.set_byte(target_nibble, target_address)
                target_address -= 1
            else:  # On odd loop index, write at the right nibble of the target_address.
                target_nibble &= 0xF0
                target_nibble |= source_nibble
                self.vm.set_byte(target_nibble, target_address)
        return node.fall_down

    def move_immediate(self, node: FieldData) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.set_value(node.data, address, 1)
        self.trace_data.set_signed_value1(node.data)
        return node.fall_down

    def move_halfword_immediate(self, node: FieldData) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.set_value(node.data, address, 2)
        self.trace_data.set_signed_value1(node.data)
        return node.fall_down

    def branch(self, node: BranchCondition) -> str:
        if node.mask & (1 << 3 - self.cc) != 0:
            label = self.index_to_label(node.branch)
        else:
            label = node.fall_down
        return label

    def branch_on_count_register(self, node: RegisterRegister) -> str:
        dsp = self.regs.get_address(node.reg2)
        if dsp > 0:
            dsp -= self.regs.R8
        value = self.regs.get_value(node.reg1) - 1
        self.regs.set_value(value, node.reg1)
        if dsp == 0 or value == 0:
            return node.fall_down
        else:
            return self._branch_to(dsp)

    def branch_on_count(self, node: RegisterBranch) -> str:
        value = self.regs.get_value(node.reg)
        if value <= 0:
            raise BctExecutionError
        value -= 1
        self.regs.set_value(value, node.reg)
        if value > 0:
            return self.index_to_label(node.branch)
        return node.fall_down

    def _branch_to(self, branch_add: int) -> str:
        label = self.seg.get_field_name(Register('R8'), branch_add, 4)
        if label is None:
            branch_add += 0x078
            label = self.seg.get_field_name(Register('R8'), branch_add, 4)
            if label is None:
                raise BctExecutionError
        return label

    def branch_and_save(self, node: RegisterBranch) -> str:
        value = self.seg.evaluate(node.fall_down) + self.regs.R8
        self.regs.set_value(value, node.reg)
        return self.index_to_label(node.branch)

    def branch_and_save_register(self, node: RegisterRegister) -> str:
        value = self.seg.evaluate(node.fall_down) + self.regs.R8
        self.regs.set_value(value, node.reg1)
        register: str = node.reg2.reg
        if register == "R0":
            return node.fall_down
        branch_address: int = self.regs.get_address(node.reg2)
        if branch_address > 0:
            branch_address -= self.regs.R8
        return self._branch_to(branch_address)

    def branch_return(self, node: BranchConditionRegister) -> str:
        if node.mask & (1 << 3 - self.cc) != 0:
            value = self.regs.get_address(node.reg) - self.regs.R8
            return self._branch_to(value)
        else:
            return node.fall_down

    def branch_on_index_low_or_equal(self, node: RegisterRegisterBranch) -> str:
        increment: Register = node.reg2
        comparator: Register = node.reg2.get_next_register() if node.reg2.is_even() else node.reg2
        compare_value: int = self.regs.get_value(comparator)
        sum_value: int = self.regs.get_value(node.reg1) + self.regs.get_value(increment)
        self.regs.set_value(sum_value, node.reg1)
        if sum_value <= compare_value:
            return self.index_to_label(node.branch)
        return node.fall_down

    def branch_on_index_high(self, node: RegisterRegisterBranch) -> str:
        increment: Register = node.reg2
        comparator: Register = node.reg2.get_next_register() if node.reg2.is_even() else node.reg2
        compare_value: int = self.regs.get_value(comparator)
        sum_value: int = self.regs.get_value(node.reg1) + self.regs.get_value(increment)
        self.regs.set_value(sum_value, node.reg1)
        if sum_value > compare_value:
            return self.index_to_label(node.branch)
        return node.fall_down


class CompareLogical(State):
    def compare_logical_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        length = node.field_len.length + 1
        source_value = self.vm.get_unsigned_value(source_address, length)
        target_value = self.vm.get_unsigned_value(target_address, length)
        self.set_number_cc(target_value - source_value)
        self.trace_data.set_unsigned_value1(target_value, length)
        self.trace_data.set_unsigned_value2(source_value, length)
        return node.fall_down

    def compare_logical_immediate(self, node: FieldData) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        value = self.vm.get_unsigned_value(address, 1)
        self.set_number_cc(value - node.data)
        self.trace_data.set_unsigned_value1(value, 1)
        self.trace_data.set_unsigned_value2(node.data, 1)
        return node.fall_down

    def compare_logical_halfword_immediate(self, node: FieldData) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        value = self.vm.get_unsigned_value(address, 2)
        self.set_number_cc(value - node.data)
        self.trace_data.set_unsigned_value1(value, 2)
        self.trace_data.set_unsigned_value2(node.data, 2)
        return node.fall_down

    def compare_halfword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 2)
        reg_value = self.regs.get_value(node.reg)
        self.set_number_cc(reg_value - value)
        self.trace_data.set_signed_value1(reg_value)
        self.trace_data.set_signed_value2(value)
        return node.fall_down

    def compare_halfword_immediate(self, node: RegisterData) -> str:
        reg_value = self.regs.get_value(node.reg)
        self.set_number_cc(reg_value - node.data)
        self.trace_data.set_signed_value1(reg_value)
        self.trace_data.set_signed_value2(node.data)
        return node.fall_down

    def compare_logical_register(self, node: RegisterRegister) -> str:
        reg_value1: int = self.regs.get_unsigned_value(node.reg1)
        reg_value2: int = self.regs.get_unsigned_value(node.reg2)
        self.set_number_cc(reg_value1 - reg_value2)
        return node.fall_down

    def compare_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 4)
        reg_value = self.regs.get_value(node.reg)
        self.set_number_cc(reg_value - value)
        self.trace_data.set_signed_value1(reg_value)
        self.trace_data.set_signed_value2(value)
        return node.fall_down

    def compare_logical_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_unsigned_value(address, 4)
        reg_value = self.regs.get_unsigned_value(node.reg)
        self.set_number_cc(reg_value - value)
        self.trace_data.set_unsigned_value1(reg_value, 4)
        self.trace_data.set_unsigned_value2(value, 4)
        return node.fall_down

    def compare_register(self, node: RegisterRegister) -> str:
        reg_value1 = self.regs.get_value(node.reg1)
        reg_value2 = self.regs.get_value(node.reg2)
        self.set_number_cc(reg_value1 - reg_value2)
        self.trace_data.set_signed_value1(reg_value1)
        self.trace_data.set_signed_value2(reg_value2)
        return node.fall_down

    def compare_logical_character_mask(self, node: RegisterDataField) -> str:
        if node.data == 0:
            self.set_number_cc(0)
            return node.fall_down
        bytes1: bytearray = self.regs.get_bytes_from_mask(node.reg, node.data)
        address: int = self.regs.get_address(node.field.base, node.field.dsp)
        bytes2: bytearray = self.vm.get_bytes(address, bin(node.data).count('1'))
        value1: int = DataType('X', bytes=bytes1).value
        value2: int = DataType('X', bytes=bytes2).value
        self.set_number_cc(value1 - value2)
        return node.fall_down

    def compare_logical_character_long(self, node: RegisterRegister) -> str:
        target_address: int = self.regs.get_unsigned_value(node.reg1)
        target_reg: str = self.regs.next_reg(node.reg1)
        target_length: int = self.regs.get_unsigned_value(target_reg) & 0x00FFFFFF
        source_address: int = self.regs.get_unsigned_value(node.reg2)
        source_reg = self.regs.next_reg(node.reg2)
        source_length: int = self.regs.get_unsigned_value(source_reg) & 0x00FFFFFF
        pad_character: int = self.regs.get_bytes_from_mask(source_reg, 0b1000)[0]
        max_length: int = max(target_length, source_length)
        target_byte: int = 0
        source_byte: int = 0
        for index in range(max_length):
            source_byte: int = self.vm.get_byte(source_address) if source_length > 0 else pad_character
            target_byte: int = self.vm.get_byte(target_address) if target_length > 0 else pad_character
            if source_byte != target_byte:
                break
            if source_length > 0:
                source_address += 1
                source_length -= 1
            if target_length > 0:
                target_address += 1
                target_length -= 1
        source_length |= pad_character << 24
        self.regs.set_unsigned_value(target_address, node.reg1)
        self.regs.set_unsigned_value(source_address, node.reg2)
        self.regs.set_unsigned_value(target_length, target_reg)
        self.regs.set_unsigned_value(source_length, source_reg)
        self.set_number_cc(target_byte - source_byte)
        return node.fall_down

    def shift_left_logical(self, node: RegisterFieldIndex):
        factor = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        value = self.regs.get_unsigned_value(node.reg) << factor & config.REG_MAX
        self.regs.set_value(value, node.reg)
        return node.fall_down

    def shift_right_logical(self, node: RegisterFieldIndex):
        factor = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        value = self.regs.get_unsigned_value(node.reg) >> factor
        self.regs.set_value(value, node.reg)
        return node.fall_down

    def shift_left_double_logical(self, node: RegisterFieldIndex):
        factor = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        value = self.regs.get_unsigned_double_value(node.reg) << factor
        self.regs.set_double_value(value, node.reg)
        return node.fall_down

    def shift_right_double_logical(self, node: RegisterFieldIndex):
        factor = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        value = self.regs.get_unsigned_double_value(node.reg) >> factor
        self.regs.set_double_value(value, node.reg)
        return node.fall_down

    def add_logical_register(self, node: RegisterRegister) -> str:
        value: int = self.regs.get_unsigned_value(node.reg1) + self.regs.get_unsigned_value(node.reg2)
        self.regs.set_unsigned_value(value, node.reg1)
        sum1: int = self.regs.get_unsigned_value(node.reg1)
        if value <= config.REG_MAX:
            self.set_zero_cc(sum1)
        else:
            self.cc = 2 if sum1 == 0 else 3
        return node.fall_down

    def add_logical_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value: int = self.regs.get_unsigned_value(node.reg) + self.vm.get_unsigned_value(address, 4)
        self.regs.set_unsigned_value(value, node.reg)
        sum1: int = self.regs.get_unsigned_value(node.reg)
        if value <= config.REG_MAX:
            self.set_zero_cc(sum1)
        else:
            self.cc = 2 if sum1 == 0 else 3
        return node.fall_down

    def subtract_logical_register(self, node: RegisterRegister) -> str:
        op1: int = self.regs.get_unsigned_value(node.reg1)
        op2: int = self.regs.get_unsigned_value(node.reg2)
        diff: int = op1 - op2
        self.regs.set_unsigned_value(diff, node.reg1)
        if op1 < op2:
            self.cc = 1
        elif op1 == op2:
            self.cc = 2
        else:
            self.cc = 3
        return node.fall_down

    def subtract_logical_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        op1: int = self.regs.get_unsigned_value(node.reg)
        op2: int = self.vm.get_unsigned_value(address, 4)
        diff: int = op1 - op2
        self.regs.set_unsigned_value(diff, node.reg)
        if op1 < op2:
            self.cc = 1
        elif op1 == op2:
            self.cc = 2
        else:
            self.cc = 3
        return node.fall_down


class LogicalUsefulConversion(State):
    def or_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1)
        self.trace_data.set_unsigned_value2(value, 4)
        value |= self.regs.get_value(node.reg2)
        self.trace_data.set_unsigned_value1(value, 4)
        self.regs.set_value(value, node.reg1)
        self.set_zero_cc(value)
        return node.fall_down

    def and_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1)
        self.trace_data.set_unsigned_value2(value, 4)
        value &= self.regs.get_value(node.reg2)
        self.trace_data.set_unsigned_value1(value, 4)
        self.regs.set_value(value, node.reg1)
        self.set_zero_cc(value)
        return node.fall_down

    def xor_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1)
        self.trace_data.set_unsigned_value2(value, 4)
        value ^= self.regs.get_value(node.reg2)
        self.trace_data.set_unsigned_value1(value, 4)
        self.regs.set_value(value, node.reg1)
        self.set_zero_cc(value)
        return node.fall_down

    def xor_grande_register(self, node: RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1)
        self.trace_data.set_unsigned_value2(value, 8)
        value ^= self.regs.get_value(node.reg2)
        self.trace_data.set_unsigned_value1(value, 8)
        self.regs.set_value64(value, node.reg1)
        self.set_zero_cc(value)
        return node.fall_down

    def and_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address)
        self.trace_data.set_unsigned_value2(value, 4)
        value &= self.regs.get_value(node.reg)
        self.trace_data.set_unsigned_value1(value, 4)
        self.regs.set_value(value, node.reg)
        self.set_zero_cc(value)
        return node.fall_down

    def or_fullword(self, node: RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address)
        self.trace_data.set_unsigned_value2(value, 4)
        value |= self.regs.get_value(node.reg)
        self.trace_data.set_unsigned_value1(value, 4)
        self.regs.set_value(value, node.reg)
        self.set_zero_cc(value)
        return node.fall_down

    def xor_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        byte_list: List[int] = list()
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index) ^ self.vm.get_byte(target_address + index)
            self.vm.set_byte(byte, target_address + index)
            byte_list.append(byte)
        self.trace_data.set_byte_array1(bytearray(byte_list))
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return node.fall_down

    def or_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        byte_list: List[int] = list()
        for index in range(node.field_len.length + 1):
            target_byte = self.vm.get_byte(target_address + index)
            byte = self.vm.get_byte(source_address + index) | target_byte
            if byte != target_byte:
                self.vm.set_byte(byte, target_address + index)
            byte_list.append(byte)
        self.trace_data.set_byte_array1(bytearray(byte_list))
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return node.fall_down

    def and_character(self, node: FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        byte_list: List[int] = list()
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index) & self.vm.get_byte(target_address + index)
            self.vm.set_byte(byte, target_address + index)
            byte_list.append(byte)
        self.trace_data.set_byte_array1(bytearray(byte_list))
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return node.fall_down

    def or_immediate(self, node: FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.or_bit(address, node.bits.value)
        value = self.vm.get_byte(address)
        self.trace_data.set_unsigned_value1(value, 1)
        self.trace_data.set_unsigned_value2(node.bits.value, 1)
        self.set_zero_cc(value)
        return node.fall_down

    def and_immediate(self, node: FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.and_bit(address, node.bits.value)
        value = self.vm.get_byte(address)
        self.trace_data.set_unsigned_value1(value, 1)
        self.trace_data.set_unsigned_value2(node.bits.value, 1)
        self.set_zero_cc(value)
        return node.fall_down

    def xor_immediate(self, node: FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.xor_bit(address, node.bits.value)
        value = self.vm.get_byte(address)
        self.trace_data.set_unsigned_value1(value, 1)
        self.trace_data.set_unsigned_value2(node.bits.value, 1)
        self.set_zero_cc(value)
        return node.fall_down

    def test_mask(self, node: FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        if self.vm.all_bits_off(address, node.bits.value):
            self.cc = 0
        elif self.vm.all_bits_on(address, node.bits.value):
            self.cc = 3
        else:
            self.cc = 1
        self.trace_data.set_unsigned_value1(self.vm.get_byte(address), 1)
        self.trace_data.set_unsigned_value2(node.bits.value, 1)
        return node.fall_down

    def execute(self, node: RegisterFieldIndex) -> str:
        value = self.regs.get_address(node.reg) & 0xFF
        dsp = self.regs.get_address(node.field.index, node.field.dsp)
        name = self.seg.get_field_name(node.field.base, dsp, 4)
        exec_node = self.seg.nodes[name]
        if exec_node.command in ['EQU', 'DS']:
            exec_node = self.seg.nodes[exec_node.fall_down]
        exec_node = deepcopy(exec_node)
        if isinstance(exec_node, FieldLenField):
            exec_node.field_len.length |= value
            self._ex_command(exec_node)
        elif isinstance(exec_node, FieldLenFieldLen):
            value1 = value >> 4
            exec_node.field_len1.length |= value1
            value2 = value & 0x0F
            exec_node.field_len2.length |= value2
            self._ex_command(exec_node)
        elif isinstance(exec_node, FieldData):
            exec_node.data |= value
            self._ex_command(exec_node)
        elif isinstance(exec_node, FieldBits):
            value |= exec_node.bits.value
            exec_node.bits.set_value(value)
            self._ex_command(exec_node)
        elif value == 0:
            self._ex_command(exec_node)
        else:
            raise ExExecutionError
        return node.fall_down

    def pack(self, node: FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        source_bytes = self.vm.get_bytes(source_address, node.field_len2.length + 1)
        number = DataType('X', bytes=source_bytes).decode
        if not number.isdigit():
            raise PackExecutionError
        packed_bytes = DataType('P', input=number).to_bytes(node.field_len1.length + 1)
        self.vm.set_bytes(packed_bytes, target_address, node.field_len1.length + 1)
        return node.fall_down

    def convert_binary(self, node: RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        packed_bytes = self.vm.get_bytes(address, 8)
        value = DataType('P', bytes=packed_bytes).value
        self.regs.set_value(value, node.reg)
        return node.fall_down

    def convert_decimal(self, node: RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        packed_bytes = DataType('P', input=str(value)).to_bytes(8)
        self.vm.set_bytes(packed_bytes, address, 8)
        return node.fall_down

    def unpack(self, node: FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        packed_bytes = self.vm.get_bytes(source_address, node.field_len2.length + 1)
        value = DataType('P', bytes=packed_bytes).value
        zoned_bytes = DataType('Z', input=str(value)).to_bytes(node.field_len1.length + 1)
        self.vm.set_bytes(zoned_bytes, target_address, node.field_len1.length + 1)
        return node.fall_down


class DecimalArithmeticComplex(State):

    def zap(self, node: FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        value = DataType('P', bytes=self.vm.get_bytes(source_address, node.field_len2.length + 1)).value
        self.vm.set_bytes(DataType('P', input=str(value)).to_bytes(node.field_len1.length + 1), target_address,
                          node.field_len1.length + 1)
        self.set_number_cc(value)
        return node.fall_down

    def tp(self, node: FieldSingle) -> str:
        packed_type = PDataType()
        address = self.regs.get_address(node.field.base, node.field.dsp)
        packed_type.bytes = self.vm.get_bytes(address, node.field.length + 1)
        self.cc = 0
        if not packed_type.is_packed_digit():
            self.cc += 2
        if not packed_type.is_sign_valid():
            self.cc += 1
        return node.fall_down

    def ap(self, node: FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        value = DataType('P', bytes=self.vm.get_bytes(target_address, node.field_len1.length + 1)).value
        value += DataType('P', bytes=self.vm.get_bytes(source_address, node.field_len2.length + 1)).value
        self.vm.set_bytes(DataType('P', input=str(value)).to_bytes(node.field_len1.length + 1), target_address,
                          node.field_len1.length + 1)
        self.set_number_cc(value)
        return node.fall_down

    def sp(self, node: FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        value = DataType('P', bytes=self.vm.get_bytes(target_address, node.field_len1.length + 1)).value
        value -= DataType('P', bytes=self.vm.get_bytes(source_address, node.field_len2.length + 1)).value
        packed_bytes = DataType('P', input=str(value)).to_bytes(node.field_len1.length + 1)
        self.vm.set_bytes(packed_bytes, target_address, node.field_len1.length + 1)
        self.set_number_cc(value)
        return node.fall_down

    def mp(self, node: FieldLenFieldLen) -> str:
        if node.field_len2.length + 1 > 8:
            raise PackExecutionError
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        value = DataType('P', bytes=self.vm.get_bytes(target_address, node.field_len1.length + 1)).value
        value *= DataType('P', bytes=self.vm.get_bytes(source_address, node.field_len2.length + 1)).value
        packed_bytes = DataType('P', input=str(value)).to_bytes(node.field_len1.length + 1)
        self.vm.set_bytes(packed_bytes, target_address, node.field_len1.length + 1)
        return node.fall_down

    def dp(self, node: FieldLenFieldLen) -> str:
        if node.field_len2.length + 1 > 8:
            raise PackExecutionError
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        dividend = DataType('P', bytes=self.vm.get_bytes(target_address, node.field_len1.length + 1)).value
        divisor = DataType('P', bytes=self.vm.get_bytes(source_address, node.field_len2.length + 1)).value
        quotient = int(dividend // divisor)
        remainder = dividend % divisor
        remainder_len = node.field_len2.length + 1
        quotient_len = node.field_len1.length + 1 - remainder_len
        self.vm.set_bytes(DataType('P', input=str(quotient)).to_bytes(quotient_len), target_address, quotient_len)
        self.vm.set_bytes(DataType('P', input=str(remainder)).to_bytes(remainder_len), target_address + quotient_len,
                          remainder_len)
        return node.fall_down

    def srp(self, node: FieldLenFieldData) -> str:
        def convert_six_bit_ubi_to_sbi(value1: int) -> int:
            number_of_bits: int = 6
            max_6_bit_ubi: int = (1 << number_of_bits) - 1
            min_6_bit_sbi: int = 1 << number_of_bits - 1
            return value1 - (max_6_bit_ubi + 1) if value1 & min_6_bit_sbi != 0 else value1

        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        value: int = DataType('P', bytes=self.vm.get_bytes(target_address, node.field_len.length + 1)).value
        shift_by = self.regs.get_address(node.field.base, node.field.dsp) & 0x3F
        shift_by = convert_six_bit_ubi_to_sbi(shift_by)
        if shift_by > 0:
            # perform left shift
            value = value * 10 ** shift_by
            packed_data = DataType('P', input=str(value)).to_bytes(node.field_len.length + 1)
            self.vm.set_bytes(packed_data, target_address, node.field_len.length + 1)
        else:
            # perform right shift
            shift_by = abs(shift_by)
            rounding = node.data
            last_byte = str(value)
            first_digit = int (last_byte[-1])
            sum1 = rounding + first_digit
            if sum1 > 9:
                value = value // (10 ** shift_by) + 1
            else:
                value = value // (10 ** shift_by)
            packed_data = DataType('P', input=str(value)).to_bytes(node.field_len.length + 1)
            self.vm.set_bytes(packed_data, target_address, node.field_len.length + 1)
        self.set_number_cc(value)
        return node.fall_down

    def cp(self, node: FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        value: int = DataType('P', bytes=self.vm.get_bytes(target_address, node.field_len1.length + 1)).value
        value -= DataType('P', bytes=self.vm.get_bytes(source_address, node.field_len2.length + 1)).value
        self.set_number_cc(value)
        return node.fall_down

    def tr(self, node: FieldLenField) -> str:
        table_address = self.regs.get_address(node.field.base, node.field.dsp)
        address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            dsp = self.vm.get_byte(address + index)
            byte = self.vm.get_byte(table_address + dsp)
            self.vm.set_byte(byte, address + index)
        return node.fall_down

    def trt(self, node: FieldLenField) -> str:
        table_address = self.regs.get_address(node.field.base, node.field.dsp)
        address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            dsp = self.vm.get_byte(address + index)
            byte = self.vm.get_byte(table_address + dsp)
            if byte != 0:
                self.cc = 2 if index == node.field_len.length else 1
                self.regs.set_value(address + index, "R1")
                self.regs.set_bytes_from_mask(bytearray([byte]), "R2", 0b0001)
                return node.fall_down
        self.cc = 0
        return node.fall_down

    def stck(self, node: FieldSingleBaseDsp) -> str:
        current_time: datetime = datetime.now()
        start_time: datetime = datetime(year=1936, month=2, day=7, hour=0, minute=28, second=16)
        difference: timedelta = current_time - start_time
        seconds = difference.days * 60 * 60 * 24 + difference.seconds
        microseconds = seconds * 10 ** 6 + difference.microseconds
        value = microseconds * 2 ** 12
        address = self.regs.get_value(node.field.base) + node.field.dsp
        byte_value = bytearray(int.to_bytes(value, length=8, byteorder="big"))
        self.vm.set_bytes(byte_value, address, length=8)
        return node.fall_down


class Instruction(LoadStore, ArithmeticShiftAlgebraic, MoveLogicControl, CompareLogical, LogicalUsefulConversion,
                  DecimalArithmeticComplex):
    pass
