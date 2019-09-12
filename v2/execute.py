from typing import Optional, Dict, Callable

import v2.instruction_type as ins
from config import config
from v2.segment import Program
from v2.state import State


class Execute(State):
    def __init__(self, global_program: Program, seg_name: Optional[str] = None):
        super().__init__(global_program, seg_name)
        self.ex: Dict[str, Callable] = {
            'L': self.load_fullword,
            'LH': self.load_halfword,
            'N': self.and_fullword,
            'STH': self.store_halfword,
            'LHI': self.load_halfword_immediate,
            'STC': self.store_character,
            'LR': self.load_register,
            'AR': self.add_register,
            'SR': self.subtract_register,
            'IC': self.insert_character,
            'BCTR': self.branch_on_count_register,
            'LA': self.load_address,
            'MVC': self.move_character,
            'MVI': self.move_immediate,
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

    def load_fullword(self, node: ins.RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 4)
        value = self.validate(value)
        self.regs.set_value(value, node.reg)

    def load_halfword(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 2)
        self.regs.set_value(value, node.reg)

    def and_fullword(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 4)
        value &= self.regs.get_value(node.reg)
        self.regs.set_value(value, node.reg)

    def store_halfword(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 2)

    def load_halfword_immediate(self, node: ins.RegisterData) -> None:
        self.regs.set_value(node.data, node.reg)

    def store_character(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.regs.get_bytes_from_mask(node.reg, 0b0001)
        self.vm.set_bytes(byte, address)

    def load_register(self, node: ins.RegisterRegister) -> None:
        value = self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)

    def add_register(self, node: ins.RegisterRegister) -> None:
        value = self.regs.get_value(node.reg1) + self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)

    def subtract_register(self, node: ins.RegisterRegister) -> None:
        value = self.regs.get_value(node.reg1) - self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)

    def insert_character(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.vm.get_bytes(address)
        self.regs.set_bytes_from_mask(byte, node.reg, 0b0001)

    def branch_on_count_register(self, node: ins.RegisterRegister) -> None:
        if node.reg2.reg != 'R0':
            raise TypeError
        value = self.regs.get_value(node.reg1) - 1
        self.regs.set_value(value, node.reg1)

    def load_address(self, node: ins.RegisterFieldIndex) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        self.regs.set_value(address, node.reg)

    def move_character(self, node: ins.FieldLenField) -> None:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length):
            byte = self.vm.get_bytes(source_address + index)
            self.vm.set_bytes(byte, target_address + index)

    def move_immediate(self, node: ins.FieldData) -> None:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.set_value(node.data, address, 1)

    def no_operation(self, node: Optional[ins.InstructionGeneric] = None) -> None:
        pass
