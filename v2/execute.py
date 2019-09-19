from typing import Optional, Dict, Callable

import v2.instruction_type as ins
from config import config
from v2.data_type import DataType, Register
from v2.segment import Program
from v2.state import State


class Execute(State):
    def __init__(self, global_program: Program):
        super().__init__(global_program)
        self.cc: Optional[int] = None
        self.ex: Dict[str, Callable] = {

            # S03 - Load & Store
            'LR': self.load_register,
            'LTR': self.load_test_register,
            # LPR - Not in ETA5
            # LNR - Not in ETA5
            # LCR - Not in ETA5
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

            # S04 - Arithmetic & Shift Algebraic
            'AR': self.add_register,
            # A - Not in ETA5
            # AH - Not in ETA5
            'AHI': self.add_halfword_immediate,
            'SR': self.subtract_register,
            # S - Not in ETA5
            # SH - Not in ETA5
            # MH, MHI, M, MR, DR, D - Not in ETA5
            # SLA, SRA, SLDA, SRDA - Not in ETA5

            # S05 - Moving Store & Logic Control
            'MVC': self.move_character,
            'MVI': self.move_immediate,
            # MVCL - Not in ETA5
            # MVZ, MVO, MVN - Not in ETA5
            'B': self.branch,
            'J': self.branch,
            # BCT - Not in ETA5
            'BCTR': self.branch_on_count_register,
            # BXH, BXLE - Not in ETA5
            'BAS': self.branch_and_save,
            'BR': self.branch_return,
            # BASR - Not in ETA5

            # S06 -  Compare & Logical
            # CR - Not in ETA5
            # C - Not in ETA5
            'CH': self.compare_halfword,
            # CHI - Not in ETA5
            # CL, CLR - Not in ETA5
            'CLI': self.compare_logical_immediate,
            'CLC': self.compare_logical_character,
            # CLM, CLCL - Not in ETA5
            # SLL, SRL, SLDL, SRDL - Not in ETA5
            # ALR, AL, SLR, SL - Not in ETA5


            # S07 - And/Or/Xor, TM, EX, Data Conversion
            # NR - Not in ETA5
            # XR - Not in ETA5
            'OR': self.or_register,
            'N': self.and_fullword,
            # O - Not in ETA5
            # X - Not in ETA5
            'NC': self.and_character,
            'OC': self.or_character,
            'XC': self.xor_character,
            'NI': self.and_immediate,
            'OI': self.or_immediate,
            # XI - Not in ETA5 (Need to check the status of flipped bits via is_updated_bit)
            'TM': self.test_mask,
            'EX': self.execute,
            'PACK': self.pack,
            'CVB': self.convert_binary,
            'CVD': self.convert_decimal,
            'UNPK': self.unpack,

            # S08 - Decimal Arithmetic & Complex - Not in ETA5
            # ZAP
            # AP
            # SP
            # MP, DP, SRP
            # CP
            # TP
            # TR
            # TRT
            # ED, EDMK

            # Realtime Macros
            'GETCC': self.getcc,
            'MODEC': self.no_operation,
            'DETAC': self.detac,
            'ATTAC': self.attac,
            'RELCC': self.no_operation,
            'CRUSA': self.no_operation,
            'SENDA': self.senda,
            'SYSRA': self.sysra,
            'SERRC': self.serrc,
            'ENTRC': self.entrc,
            'ENTNC': self.entnc,
            'ENTDC': self.entdc,
            'BACKC': self.backc,

            # TPFDF Macros
            # DBOPN
            # DBRED
            # DBCLS
            # DBIFB

            # User defined Macros
            'AAGET': self.aaget,
            'CFCMA': self.heapa,
            'HEAPA': self.heapa,
            # PNRCC
            # PDRED
            # PDCLS


            # No operation
            'EQU': self.no_operation,
            'DS': self.no_operation,
            'EXITC': self.no_operation,
        }

    def run(self, seg_name: Optional[str] = None) -> None:
        seg_name = self.seg.name if seg_name is None else seg_name
        self.init_seg(seg_name)
        self.regs.R9 = config.ECB
        label = self.seg.root_label
        while label:
            node = self.seg.nodes[label]
            label = self.ex[node.command](node)

    def next_label(self, node: ins.InstructionGeneric) -> Optional[str]:
        for condition in node.conditions:
            if condition.is_check_cc:
                if condition.mask & (1 << 3 - self.cc) != 0:
                    if condition.branch:
                        return self.branch(condition)
                    else:
                        return self.branch_return(condition)
            else:
                self.ex[condition.command](condition)
        return node.fall_down

    def set_number_cc(self, number: int) -> None:
        if number > 0:
            self.cc = 2
        elif number == 0:
            self.cc = 0
        else:
            self.cc = 1

    def set_zero_cc(self, number: int) -> None:
        self.cc = 1 if number else 0

    # S03 - Load & Store

    def load_register(self, node: ins.RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        return self.next_label(node)

    def load_test_register(self, node: ins.RegisterRegister) -> str:
        value = self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        return self.next_label(node)

    def load_fullword(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 4)
        value = self.validate(value)
        self.regs.set_value(value, node.reg)
        return self.next_label(node)

    def load_address(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        self.regs.set_value(address, node.reg)
        return self.next_label(node)

    def store_fullword(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 4)
        return self.next_label(node)

    def load_halfword(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 2)
        self.regs.set_value(value, node.reg)
        return self.next_label(node)

    def load_halfword_immediate(self, node: ins.RegisterData) -> str:
        self.regs.set_value(node.data, node.reg)
        return self.next_label(node)

    def store_halfword(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        self.vm.set_value(value, address, 2)
        return self.next_label(node)

    def insert_character(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.vm.get_bytes(address)
        self.regs.set_bytes_from_mask(byte, node.reg, 0b0001)
        return self.next_label(node)

    def insert_character_mask(self, node: ins.RegisterDataField) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        byte = self.vm.get_bytes(address, bin(node.data).count('1'))
        self.regs.set_bytes_from_mask(byte, node.reg, node.data)
        self.set_number_cc(DataType('F', bytes=byte).value)
        return self.next_label(node)

    def store_character(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        byte = self.regs.get_bytes_from_mask(node.reg, 0b0001)
        self.vm.set_bytes(byte, address)
        return self.next_label(node)

    def store_character_mask(self, node: ins.RegisterDataField) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        byte = self.regs.get_bytes_from_mask(node.reg, node.data)
        self.vm.set_bytes(byte, address, bin(node.data).count('1'))
        return self.next_label(node)

    def load_multiple(self, node: ins.RegisterRegisterField) -> str:
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

    def store_multiple(self, node: ins.RegisterRegisterField) -> str:
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

    # S04 - Arithmetic & Shift Algebraic

    def add_register(self, node: ins.RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1) + self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        return self.next_label(node)

    def add_halfword_immediate(self, node: ins.RegisterData) -> str:
        value = self.regs.get_value(node.reg) + node.data
        self.regs.set_value(value, node.reg)
        self.set_number_cc(value)
        return self.next_label(node)

    def subtract_register(self, node: ins.RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1) - self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_number_cc(value)
        return self.next_label(node)

    # S05 - Moving Store & Logic Control

    def move_character(self, node: ins.FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index)
            self.vm.set_byte(byte, target_address + index)
        return self.next_label(node)

    def move_immediate(self, node: ins.FieldData) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.set_value(node.data, address, 1)
        return self.next_label(node)

    @staticmethod
    def branch(node: ins.BranchCondition) -> str:
        return node.branch.name

    def branch_on_count_register(self, node: ins.RegisterRegister) -> str:
        if node.reg2.reg != 'R0':
            raise TypeError
        value = self.regs.get_value(node.reg1) - 1
        self.regs.set_value(value, node.reg1)
        return self.next_label(node)

    def branch_and_save(self, node: ins.RegisterBranch):
        bas = self.seg.bas
        value = bas.dumps(node.fall_down)
        self.regs.set_value(value, node.reg)
        return node.branch.name

    def branch_return(self, node: ins.BranchConditionRegister):
        bas = self.seg.bas
        value = self.regs.get_value(node.reg)
        return bas.loads(value)

    # S06 -  Compare & Logical

    def compare_logical_character(self, node: ins.FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        source_value = self.vm.get_unsigned_value(target_address, node.field_len.length + 1)
        target_value = self.vm.get_unsigned_value(source_address, node.field_len.length + 1)
        self.set_number_cc(target_value - source_value)
        return self.next_label(node)

    def compare_logical_immediate(self, node: ins.FieldData) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        value = self.vm.get_unsigned_value(address, 1)
        self.set_number_cc(value - node.data)
        return self.next_label(node)

    def compare_halfword(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address, 2)
        reg_value = self.regs.get_value(node.reg)
        self.set_number_cc(reg_value - value)
        return self.next_label(node)

    # S07 - AND/OR/XOR, TM, EX, PACK/UNPK

    def or_register(self, node: ins.RegisterRegister) -> str:
        value = self.regs.get_value(node.reg1)
        value |= self.regs.get_value(node.reg2)
        self.regs.set_value(value, node.reg1)
        self.set_zero_cc(value)
        return self.next_label(node)

    def and_fullword(self, node: ins.RegisterFieldIndex) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.vm.get_value(address)
        value &= self.regs.get_value(node.reg)
        self.regs.set_value(value, node.reg)
        self.set_zero_cc(value)
        return self.next_label(node)

    def xor_character(self, node: ins.FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index) ^ self.vm.get_byte(target_address + index)
            self.vm.set_byte(byte, target_address + index)
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return self.next_label(node)

    def or_character(self, node: ins.FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            target_byte = self.vm.get_byte(target_address + index)
            byte = self.vm.get_byte(source_address + index) | target_byte
            if byte != target_byte:
                self.vm.set_byte(byte, target_address + index)
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return self.next_label(node)

    def and_character(self, node: ins.FieldLenField) -> str:
        source_address = self.regs.get_address(node.field.base, node.field.dsp)
        target_address = self.regs.get_address(node.field_len.base, node.field_len.dsp)
        for index in range(node.field_len.length + 1):
            byte = self.vm.get_byte(source_address + index) & self.vm.get_byte(target_address + index)
            self.vm.set_byte(byte, target_address + index)
        self.set_zero_cc(self.vm.get_value(target_address, node.field_len.length + 1))
        return self.next_label(node)

    def or_immediate(self, node: ins.FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.or_bit(address, node.bits.value)
        self.set_zero_cc(self.vm.get_value(address, 1))
        return self.next_label(node)

    def and_immediate(self, node: ins.FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        self.vm.and_bit(address, node.bits.value)
        self.set_zero_cc(self.vm.get_value(address, 1))
        return self.next_label(node)

    def test_mask(self, node: ins.FieldBits) -> str:
        address = self.regs.get_address(node.field.base, node.field.dsp)
        if self.vm.all_bits_off(address, node.bits.value):
            self.cc = 0
        elif self.vm.all_bits_on(address, node.bits.value):
            self.cc = 3
        else:
            self.cc = 1
        return self.next_label(node)

    def execute(self, node: ins.RegisterLabel) -> str:
        exec_node = self.seg.nodes[node.label]
        value = self.regs.get_value(node.reg) & 0xFF if node.reg.reg != 'R0' else 0
        if isinstance(exec_node, ins.FieldLenField):
            save = exec_node.field_len.length
            exec_node.field_len.length |= value
            self.ex[exec_node.command](exec_node)
            exec_node.field_len.length = save
        elif isinstance(exec_node, ins.FieldLenFieldLen):
            save1, save2 = exec_node.field_len1.length, exec_node.field_len2.length
            value1 = value >> 4
            exec_node.field_len1.length |= value1
            value2 = value & 0x0F
            exec_node.field_len2.length |= value2
            self.ex[exec_node.command](exec_node)
            exec_node.field_len1.length, exec_node.field_len2.length = save1, save2
        elif isinstance(exec_node, ins.FieldData):
            save = exec_node.data
            exec_node.data |= value
            self.ex[exec_node.command](exec_node)
            exec_node.data = save
        elif isinstance(exec_node, ins.FieldBits):
            save = exec_node.bits.value
            value |= exec_node.bits.value
            exec_node.bits.set_from_number(value)
            self.ex[exec_node.command](exec_node)
            exec_node.bits.set_from_number(save)
        else:
            raise TypeError
        return self.next_label(node)

    def pack(self, node: ins.FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        source_bytes = self.vm.get_bytes(source_address, node.field_len2.length + 1)
        number = DataType('X', bytes=source_bytes).decode
        packed_bytes = DataType('P', input=number).to_bytes(node.field_len1.length + 1)
        self.vm.set_bytes(packed_bytes, target_address, node.field_len1.length + 1)
        return self.next_label(node)

    def convert_binary(self, node: ins.RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        packed_bytes = self.vm.get_bytes(address, 8)
        value = DataType('P', bytes=packed_bytes).value
        self.regs.set_value(value, node.reg)
        return self.next_label(node)

    def convert_decimal(self, node: ins.RegisterFieldIndex):
        address = self.regs.get_address(node.field.base, node.field.dsp, node.field.index)
        value = self.regs.get_value(node.reg)
        packed_bytes = DataType('P', input=str(value)).to_bytes(8)
        self.vm.set_bytes(packed_bytes, address, 8)
        return self.next_label(node)

    def unpack(self, node: ins.FieldLenFieldLen) -> str:
        source_address = self.regs.get_address(node.field_len2.base, node.field_len2.dsp)
        target_address = self.regs.get_address(node.field_len1.base, node.field_len1.dsp)
        packed_bytes = self.vm.get_bytes(source_address, node.field_len2.length + 1)
        value = DataType('P', bytes=packed_bytes).value
        zoned_bytes = DataType('Z', input=str(value)).to_bytes(node.field_len1.length + 1)
        self.vm.set_bytes(zoned_bytes, target_address, node.field_len1.length + 1)
        return self.next_label(node)

    # Realtime Macros

    def getcc(self, node: ins.KeyValue) -> str:
        address = self.vm.allocate()
        ecb_address = self.get_ecb_address(node.keys[0], 'CE1CR')
        self.vm.set_value(address, ecb_address)
        self.regs.R14 = address
        return self.next_label(node)

    def detac(self, node: ins.KeyValue) -> str:
        level = node.keys[0]
        core_address = self.get_ecb_address(level, 'CE1CR')
        file_address = self.get_ecb_address(level, 'CE1FA')
        core_bytes = self.vm.get_bytes(core_address, 8)
        file_bytes = self.vm.get_bytes(file_address, 8)
        self.detac_stack[level[1]].append((core_bytes, file_bytes))
        return self.next_label(node)

    def attac(self, node: ins.KeyValue) -> str:
        level = node.keys[0]
        core_address = self.get_ecb_address(level, 'CE1CR')
        file_address = self.get_ecb_address(level, 'CE1FA')
        core_bytes, file_bytes = self.detac_stack[level[1]].pop()
        self.vm.set_bytes(core_bytes, core_address)
        self.vm.set_bytes(file_bytes, file_address)
        return self.next_label(node)

    def senda(self, node: ins.KeyValue) -> str:
        self.message = node.get_value('MSG')
        return self.next_label(node)

    def sysra(self, node: ins.KeyValue) -> Optional[str]:
        return_code = node.get_value('P1')
        dump = node.get_value('P2')
        self.dumps.append(dump)
        if return_code == 'R':
            return self.next_label(node)
        elif return_code == 'E':
            return None
        else:
            raise TypeError

    def serrc(self, node: ins.KeyValue) -> Optional[str]:
        return_code = node.keys[0]
        dump = node.keys[1]
        self.dumps.append(dump)
        if return_code == 'R':
            return self.next_label(node)
        elif return_code == 'E':
            return None
        else:
            raise TypeError

    def entrc(self, node: ins.SegmentCall) -> str:
        self.call_stack.append((node.fall_down, self.seg.name))
        self.init_seg(node.seg_name)
        return node.branch.name

    def entnc(self, node: ins.SegmentCall) -> str:
        self.init_seg(node.seg_name)
        return node.branch.name

    def entdc(self, node: ins.SegmentCall) -> str:
        self.init_seg(node.seg_name)
        self.call_stack = list()
        self.init_seg(node.seg_name)
        return node.branch.name

    def backc(self, _) -> str:
        branch, seg_name = self.call_stack.pop()
        self.init_seg(seg_name)
        return branch

    # TPFDF Macros

    # User Defined Macros
    def aaget(self, node: ins.KeyValue) -> str:
        address = self.vm.allocate()
        ecb_address = self.get_ecb_address('D1', 'CE1CR')
        self.vm.set_value(address, ecb_address)
        reg = Register(node.get_value('BASEREG'))
        if reg.is_valid():
            self.regs.set_value(address, reg)
        return self.next_label(node)

    def heapa(self, node: ins.KeyValue) -> str:
        command = node.keys[0]
        ref = node.get_value('REF')
        if ref is None:
            sref = node.get_value('SREF')
            if sref is None:
                raise TypeError
            ref_bytes = self.seg.get_constant_bytes(sref, 8)
            ref = DataType('X', bytes=ref_bytes).decode
        if command == 'ALLOCATE':
            address = self.vm.allocate()
            self.heap[ref] = address
            reg = Register(node.get_value('REG'))
            if reg.is_valid():
                self.regs.set_value(address, reg)
        elif command == 'LOADADD':
            address = self.heap[ref] if ref in self.heap else 0
            reg = Register(node.get_value('REG'))
            if reg.is_valid():
                self.regs.set_value(address, reg)
            if address == 0:
                if node.is_key('ERROR'):
                    return node.get_value('ERROR')
                elif node.is_key('NOTFOUND'):
                    return node.get_value('NOTFOUND')
        elif command == 'FREE':
            pass
        else:
            raise TypeError
        return self.next_label(node)

    def no_operation(self, node: Optional[ins.InstructionGeneric] = None) -> str:
        return self.next_label(node)
