from typing import Optional, Dict, Callable

import v2.instruction_type as ins
from config import config
from v2.data_type import DataType
from v2.segment import Program
from v2.state import State


class Execute(State):
    def __init__(self, global_program: Program, seg_name: Optional[str] = None):
        super().__init__(global_program, seg_name)
        self.ex: Dict[str, Callable] = {
            'AR': self.add_register,
            'AHI': self.add_halfword_immediate,
            'SR': self.subtract_register,
            'LR': self.load_register,
            # LTR
            'L': self.load_fullword,
            'ST': self.store_fullword,
            'LA': self.load_address,
            'LH': self.load_halfword,
            'LHI': self.load_halfword_immediate,
            'STH': self.store_halfword,
            'IC': self.insert_character,
            'ICM': self.insert_character_mask,
            'STC': self.store_character,
            'STCM': self.store_character_mask,
            'LM': self.load_multiple,
            'STM': self.store_multiple,
            'MVC': self.move_character,
            'MVI': self.move_immediate,
            # CH
            # CLC
            # CLI
            # TM
            # CHI - Not in ETA5
            'PACK': self.pack,
            'CVB': self.convert_binary,
            'CVD': self.convert_decimal,
            'UNPK': self.unpack,
            # NR - Not in ETA5
            # XR - Not in ETA5
            # OR - Not in ETA5
            'N': self.and_fullword,
            # O - Not in ETA5
            # X - Not in ETA5
            'NC': self.and_character,
            'OC': self.or_character,
            'XC': self.xor_character,
            'NI': self.and_immediate,
            'OI': self.or_immediate,
            # XI - Not in ETA5 (Need to check the status of flipped bits via is_updated_bit)
            'BCTR': self.branch_on_count_register,
            # BCT - Not in ETA5
            # BAS
            # EX
            'EQU': self.no_operation,
            'DS': self.no_operation,
            'BACKC': self.no_operation,
        }

    def run(self) -> None:
        self.regs.R9 = config.ECB
        seg = self.init_seg(self.seg_name)
        label = seg.root_label
        while label:
            node = seg.nodes[label]
            try:
                self.ex[node.command](node)
            except (AttributeError, KeyError):
                self.errors.append(f"{seg.nodes[label]}")
            label = node.fall_down

    def add_register(self, node: ins.RegisterRegister) -> None:
        value = self.regs.get_value(node.reg1) + self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)

    def add_halfword_immediate(self, node: ins.RegisterData) -> None:
        value = self.regs.get_value(node.reg) + node.data
        self.regs.set_value(value, node.reg)

    def subtract_register(self, node: ins.RegisterRegister) -> None:
        value = self.regs.get_value(node.reg1) - self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)

    def load_register(self, node: ins.RegisterRegister) -> None:
        value = self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)

    def load_fullword(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 4)
        value = self.validate(value)
        self.regs.set_value(value, node.reg)

    def load_address(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        self.regs.set_value(address, node.reg)

    def store_fullword(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 4)

    def load_halfword(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 2)
        self.regs.set_value(value, node.reg)

    def load_halfword_immediate(self, node: ins.RegisterData) -> None:
        self.regs.set_value(node.data, node.reg)

    def store_halfword(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 2)

    def insert_character(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.vm.get_bytes(address)
        self.regs.set_bytes_from_mask(byte, node.reg, 0b0001)

    def insert_character_mask(self, node: ins.RegisterDataField) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        byte = self.vm.get_bytes(address, bin(node.data).count('1'))
        self.regs.set_bytes_from_mask(byte, node.reg, node.data)

    def store_character(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.regs.get_bytes_from_mask(node.reg, 0b0001)
        self.vm.set_bytes(byte, address)

    def store_character_mask(self, node: ins.RegisterDataField) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        byte = self.regs.get_bytes_from_mask(node.reg, node.data)
        self.vm.set_bytes(byte, address, bin(node.data).count('1'))

    def load_multiple(self, node: ins.RegisterRegisterField) -> None:
        reg = node.reg1.reg
        address = self.regs.get_address(node.field.base, node.field.dsp)
        while True:
            value = self.vm.get_value(address)
            self.regs.set_value(value, reg)
            if reg == node.reg2.reg:
                break
            address += self.regs.LEN
            reg = self.regs.next_reg(reg)

    def store_multiple(self, node: ins.RegisterRegisterField) -> None:
        reg = node.reg1.reg
        address = self.regs.get_address(node.field.base, node.field.dsp)
        while True:
            value = self.regs.get_value(reg)
            self.vm.set_value(value, address)
            if reg == node.reg2.reg:
                break
            address += self.regs.LEN
            reg = self.regs.next_reg(reg)

    def branch_on_count_register(self, node: ins.RegisterRegister) -> None:
        if node.reg2.reg != 'R0':
            raise TypeError
        value = self.regs.get_value(node.reg1) - 1
        self.regs.set_value(value, node.reg1)

    def move_character(self, node: ins.FieldLenField) -> None:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length):
            byte = self.vm.get_byte(source_address + index)
            self.vm.set_byte(byte, target_address + index)

    def move_immediate(self, node: ins.FieldData) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.set_value(node.data, address, 1)

    def pack(self, node: ins.FieldLenFieldLen) -> None:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        source_bytes = self.vm.get_bytes(source_address, node.field_len2.length)
        number = DataType('X', bytes=source_bytes).decode
        packed_bytes = DataType('P', input=number).to_bytes(node.field_len1.length)
        self.vm.set_bytes(packed_bytes, target_address, node.field_len1.length)

    def convert_binary(self, node: ins.RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        packed_bytes = self.vm.get_bytes(address, 8)
        value = DataType('P', bytes=packed_bytes).value
        self.regs.set_value(value, node.reg)

    def convert_decimal(self, node: ins.RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        packed_bytes = DataType('P', input=str(value)).to_bytes(8)
        self.vm.set_bytes(packed_bytes, address, 8)

    def unpack(self, node: ins.FieldLenFieldLen) -> None:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        packed_bytes = self.vm.get_bytes(source_address, node.field_len2.length)
        value = DataType('P', bytes=packed_bytes).value
        zoned_bytes = DataType('Z', input=str(value)).to_bytes(node.field_len1.length)
        self.vm.set_bytes(zoned_bytes, target_address, node.field_len1.length)

    def and_fullword(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 4)
        value &= self.regs.get_value(node.reg)
        self.regs.set_value(value, node.reg)

    def xor_character(self, node: ins.FieldLenField) -> None:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length):
            byte = self.vm.get_byte(source_address + index) ^ self.vm.get_byte(target_address + index)
            self.vm.set_byte(byte, target_address + index)

    def or_character(self, node: ins.FieldLenField) -> None:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length):
            target_byte = self.vm.get_byte(target_address + index)
            byte = self.vm.get_byte(source_address + index) | target_byte
            if byte != target_byte:
                self.vm.set_byte(byte, target_address + index)

    def and_character(self, node: ins.FieldLenField) -> None:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length):
            byte = self.vm.get_byte(source_address + index) & self.vm.get_byte(target_address + index)
            self.vm.set_byte(byte, target_address + index)

    def or_immediate(self, node: ins.FieldBits) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.or_bit(address, node.bits.value)

    def and_immediate(self, node: ins.FieldBits) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.and_bit(address, node.bits.value)

    def no_operation(self, node: Optional[ins.InstructionGeneric] = None) -> None:
        pass
