from datetime import datetime, timedelta
from typing import Optional

from assembly.instruction_type import KeyValue, SegmentCall
from execution.state import State
from utils.data_type import DataType, Register
from db.pnr import PnrLocator


class RealTimeMacro(State):
    def getcc(self, node: KeyValue) -> str:
        address = self.vm.allocate()
        ecb_address = self.get_ecb_address(node.keys[0], 'CE1CR')
        self.vm.set_value(address, ecb_address)
        self.regs.R14 = address
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
        self.init_seg(node.seg_name)
        return node.branch.name

    def entnc(self, node: SegmentCall) -> str:
        self.init_seg(node.seg_name)
        return node.branch.name

    def entdc(self, node: SegmentCall) -> str:
        self.init_seg(node.seg_name)
        del self.call_stack[:]
        self.init_seg(node.seg_name)
        return node.branch.name

    def backc(self, _) -> str:
        branch, seg_name = self.call_stack.pop()
        self.init_seg(seg_name)
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
        return node.fall_down

    def pnrcc(self, node: KeyValue) -> str:
        action = node.get_value('ACTION')
        reg = Register(node.get_value('REG'))
        if not reg.is_valid():
            raise TypeError
        pnrcm_base = self.regs.get_value(reg)
        self.seg.macro.load('PNRCM')
        if action in ['CRLON']:
            pnr_locator_bytes = self.vm.get_bytes(pnrcm_base + self.seg.macro.data_map['PM1LOC'].dsp, 6)
            pnr_locator = DataType('X', bytes=pnr_locator_bytes).decode
            ordinal = PnrLocator.to_ordinal(pnr_locator)
            self.vm.set_value(ordinal, pnrcm_base + self.seg.macro.data_map['PM1ORN'].dsp)
            self.vm.set_value(ordinal, pnrcm_base + self.seg.macro.data_map['PM1FAD'].dsp)
        return node.fall_down

    def pars_date(self, node: KeyValue) -> str:
        # Some constants
        gross_days = 333
        start = datetime(1966, 1, 2)
        today = datetime.today()
        today = datetime(year=today.year, month=today.month, day=today.day)
        # Get the option_byte and do the conversion
        option_byte = self.vm.get_byte(self.regs.R6)
        if option_byte == 0x00:
            # Date to PARS day number. 03OCT (2019) -> 4CB0
            date_bytes = self.vm.get_bytes(self.regs.R7, 5)
            date_str = DataType('X', bytes=date_bytes).decode
            try:
                date = datetime.strptime(date_str, '%d%b')
                date = date.replace(year=today.year)
                days_from_today = (date - today).days
                past_days_allowed = gross_days - (datetime(today.year, 12, 31) - datetime(today.year, 1, 1)).days
                if days_from_today < past_days_allowed:
                    date = date.replace(year=date.year + 1)
                self.regs.R6 = (date - start).days
                self.regs.R7 = (date - today).days
            except ValueError:
                self.regs.R6 = 0
        elif option_byte == 0xFF:
            # PARS day number to Date. 4CB0 -> 03OCT
            days_from_start = self.vm.get_value(self.regs.R7, 2)
            if 0 <= days_from_start <= 0x7FFF:
                date = start + timedelta(days=days_from_start)
                date_str = date.strftime('%d%b')
                date_bytes = DataType('C', input=date_str).to_bytes()
                self.regs.R7 = self.regs.R6
                self.vm.set_bytes(date_bytes, self.regs.R7)
            else:
                self.regs.R6 = 0
        else:
            self.regs.R6 = 0
        return node.fall_down


class ExecutableMacro(RealTimeMacro, UserDefinedMacro):
    pass
