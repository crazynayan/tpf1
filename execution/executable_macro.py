from typing import Optional

from execution.state import State
from v2.data_type import DataType, Register
from v2.instruction_type import KeyValue, SegmentCall


class RealTimeMacro(State):
    def getcc(self, node: KeyValue) -> str:
        address = self.vm.allocate()
        ecb_address = self.get_ecb_address(node.keys[0], 'CE1CR')
        self.vm.set_value(address, ecb_address)
        self.regs.R14 = address
        return self.next_label(node)

    def detac(self, node: KeyValue) -> str:
        level = node.keys[0]
        core_address = self.get_ecb_address(level, 'CE1CR')
        file_address = self.get_ecb_address(level, 'CE1FA')
        core_bytes = self.vm.get_bytes(core_address, 8)
        file_bytes = self.vm.get_bytes(file_address, 8)
        self.detac_stack[level[1]].append((core_bytes, file_bytes))
        return self.next_label(node)

    def attac(self, node: KeyValue) -> str:
        level = node.keys[0]
        core_address = self.get_ecb_address(level, 'CE1CR')
        file_address = self.get_ecb_address(level, 'CE1FA')
        core_bytes, file_bytes = self.detac_stack[level[1]].pop()
        self.vm.set_bytes(core_bytes, core_address)
        self.vm.set_bytes(file_bytes, file_address)
        return self.next_label(node)

    def senda(self, node: KeyValue) -> str:
        self.message = node.get_value('MSG')
        return self.next_label(node)

    def sysra(self, node: KeyValue) -> Optional[str]:
        return_code = node.get_value('P1')
        dump = node.get_value('P2')
        self.dumps.append(dump)
        if return_code == 'R':
            return self.next_label(node)
        elif return_code == 'E':
            return None
        else:
            raise TypeError

    def serrc(self, node: KeyValue) -> Optional[str]:
        return_code = node.keys[0]
        dump = node.keys[1]
        self.dumps.append(dump)
        if return_code == 'R':
            return self.next_label(node)
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
        return self.next_label(node)

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
        return self.next_label(node)


class ExecutableMacro(RealTimeMacro, UserDefinedMacro):
    pass
