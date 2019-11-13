from typing import Optional

from assembly.seg5_exec_macro import KeyValue, SegmentCall
from db.pnr import PnrLocator
from execution.ex1_state import State
from utils.data_type import DataType, Register
from utils.ucdr import pars_to_date, date_to_pars


class RealTimeMacro(State):
    def getcc(self, node: KeyValue) -> str:
        address = self.vm.allocate()
        self._core_block(address, node.keys[0], node.keys[1])
        self.regs.R14 = address
        return node.fall_down

    def relcc(self, node: KeyValue) -> str:
        control_address = self.get_ecb_address(node.keys[0], 'CE1CT')
        size_address = self.get_ecb_address(node.keys[0], 'CE1CC')
        self.vm.set_value(0x01, control_address, 2)
        self.vm.set_value(0, size_address, 2)
        return node.fall_down

    def crusa(self, node: KeyValue) -> str:
        for index in range(16):
            level = node.get_value(f"S{index}")
            if level is None:
                break
            control_address = self.get_ecb_address(f"D{level}", 'CE1CT')
            size_address = self.get_ecb_address(f"D{level}", 'CE1CC')
            self.vm.set_value(0x01, control_address, 2)
            self.vm.set_value(0, size_address, 2)
        return node.fall_down

    def detac(self, node: KeyValue) -> str:
        level = node.keys[0]
        core_address = self.get_ecb_address(level, 'CE1CR')
        file_address = self.get_ecb_address(level, 'CE1FA')
        core_bytes = self.vm.get_bytes(core_address, 8)
        file_bytes = self.vm.get_bytes(file_address, 8)
        self.detac_stack[level[1]].append((core_bytes, file_bytes))
        return node.fall_down

    def attac(self, node: KeyValue) -> str:
        level = node.keys[0]
        core_address = self.get_ecb_address(level, 'CE1CR')
        file_address = self.get_ecb_address(level, 'CE1FA')
        core_bytes, file_bytes = self.detac_stack[level[1]].pop()
        self.vm.set_bytes(core_bytes, core_address, len(core_bytes))
        self.vm.set_bytes(file_bytes, file_address, len(file_bytes))
        return node.fall_down

    def senda(self, node: KeyValue) -> str:
        self.message = node.get_value('MSG')
        return node.fall_down

    def sysra(self, node: KeyValue) -> Optional[str]:
        return_code = node.get_value('P1')
        dump = node.get_value('P2')
        self.dumps.append(dump)
        if return_code == 'R':
            return node.fall_down
        elif return_code == 'E':
            return None
        else:
            raise TypeError

    def serrc(self, node: KeyValue) -> Optional[str]:
        return_code = node.keys[0]
        dump = node.keys[1]
        self.dumps.append(dump)
        if return_code == 'R':
            return node.fall_down
        elif return_code == 'E':
            return None
        else:
            raise TypeError

    def entrc(self, node: SegmentCall) -> str:
        self.call_stack.append((node.fall_down, self.seg.name))
        self._init_seg(node.keys[0])
        return node.goes

    def entnc(self, node: SegmentCall) -> str:
        self._init_seg(node.keys[0])
        return node.goes

    def entdc(self, node: SegmentCall) -> str:
        del self.call_stack[:]
        self._init_seg(node.keys[0])
        return node.goes

    def backc(self, _) -> str:
        branch, seg_name = self.call_stack.pop()
        self._init_seg(seg_name)
        return branch


class UserDefinedMacro(State):
    def aaget(self, node: KeyValue) -> str:
        address = self.vm.allocate()
        ecb_address = self.get_ecb_address('D1', 'CE1CR')
        self.vm.set_value(address, ecb_address)
        reg = Register(node.get_value('BASEREG'))
        if reg.is_valid():
            self.regs.set_value(address, reg)
        return node.fall_down

    def heapa(self, node: KeyValue) -> str:
        # REG, REF and SREF
        reg = Register(node.get_value('REG'))
        ref = node.get_value('REF')
        if ref is None:
            sref = node.get_value('SREF')
            if sref is None:
                raise TypeError
            ref_bytes = self.seg.get_constant_bytes(sref, 8)
            ref = DataType('X', bytes=ref_bytes).decode

        # ERROR= for forced errors
        error_label = node.get_value('ERROR')
        if error_label and self.is_error(node.label):
            if reg.is_valid():
                self.regs.set_value(0, reg)
            return error_label

        # HEAPA / CFCMA command types
        command = node.keys[0]
        if command == 'ALLOCATE':
            address = self.vm.allocate()
            self.heap[ref] = address
            if reg.is_valid():
                self.regs.set_value(address, reg)
        elif command == 'LOADADD':
            address = self.heap[ref] if ref in self.heap else 0
            if reg.is_valid():
                self.regs.set_value(address, reg)
            if address == 0 and error_label:
                return error_label
        elif command == 'FREE':
            pass
        else:
            raise TypeError
        return node.fall_down

    def pnrcc(self, node: KeyValue) -> str:
        action = node.get_value('ACTION')
        reg = Register(node.get_value('REG'))
        if not reg.is_valid():
            raise TypeError
        pnrcm_base = self.regs.get_value(reg)
        self.seg.load_macro('PNRCM')
        if self.is_error(node.label):
            error_code = self.seg.evaluate('#PM1ER5')
            self.vm.set_value(error_code, pnrcm_base + self.seg.evaluate('PM1ERR'), 1)
            return node.fall_down
        if action in ['CRLON']:
            pnr_locator_bytes = self.vm.get_bytes(pnrcm_base + self.seg.evaluate('PM1LOC'), 6)
            pnr_locator = DataType('X', bytes=pnr_locator_bytes).decode
            ordinal = PnrLocator.to_ordinal(pnr_locator)
            self.vm.set_value(ordinal, pnrcm_base + self.seg.evaluate('PM1ORN'))
            self.vm.set_value(ordinal, pnrcm_base + self.seg.evaluate('PM1FAD'))
        return node.fall_down

    def pars_date(self, node: KeyValue) -> str:
        # Get the option_byte and do the conversion
        option_byte = self.vm.get_byte(self.regs.R6)
        if option_byte == 0x00:
            # Date to PARS day number. 03OCT (2019) -> 4CB0
            date_bytes = self.vm.get_bytes(self.regs.R7, 5)
            try:
                days_from_start, days_from_today = date_to_pars(date_bytes)
                self.regs.R6 = days_from_start
                self.regs.R7 = days_from_today
            except ValueError:
                self.regs.R6 = 0
        elif option_byte == 0xFF:
            # PARS day number to Date. 4CB0 -> 03OCT
            days_from_start = self.regs.R7
            try:
                date_bytes = pars_to_date(days_from_start)
                self.regs.R7 = self.regs.R6
                self.vm.set_bytes(date_bytes, self.regs.R7, len(date_bytes))
            except ValueError:
                self.regs.R6 = 0
        else:
            self.regs.R6 = 0
        return node.fall_down

    def error_check(self, node: KeyValue) -> str:
        if self.is_error(node.label):
            field_name = node.get_value('FIELD')
            reg = Register(node.get_value('BASE'))
            address = self.regs.get_unsigned_value(reg) + self.seg.evaluate(field_name)
            byte_array = DataType('X', input=node.get_value('XVALUE')).to_bytes()
            self.vm.set_bytes(byte_array, address, len(byte_array))
        return node.fall_down


class ExecutableMacro(RealTimeMacro, UserDefinedMacro):
    pass
