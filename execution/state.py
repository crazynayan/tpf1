from typing import Callable, Optional, Tuple, Dict, List

from assembly.instruction_type import InstructionGeneric
from assembly.program import program
from assembly.segment import Segment
from config import config
from execution.regs_store import Registers, Storage


class State:
    def __init__(self):
        self.seg: Optional[Segment] = None
        self.regs: Registers = Registers()
        self.vm: Storage = Storage()
        self.cc: Optional[int] = None
        self.ex: Dict[str, Callable] = dict()
        self.detac_stack: Dict[str, List] = {level: list() for level in config.ECB_LEVELS}
        self.message: Optional[str] = None
        self.dumps: List[str] = list()
        self.heap: Dict[str, int] = dict()
        self.call_stack: List[Tuple[str, str]] = list()
        self.loaded_seg: Dict[str, Tuple[Segment, int]] = dict()
        self.tpfdf_ref: Dict[str, int] = dict()
        self.setup: Dict[str, Dict[str, bytearray]] = {'EB0EB': dict(), 'GLOBAL': dict(), 'WA0AA': dict()}

    def __repr__(self) -> str:
        return f"State:{self.seg}:{self.regs}:{self.vm}"

    def init_seg(self, seg_name: str) -> None:
        if seg_name in self.loaded_seg:
            self.regs.R8 = self.loaded_seg[seg_name][1]
            self.seg = self.loaded_seg[seg_name][0]
        else:
            program.load(seg_name)
            self.regs.R8 = self.vm.allocate()   # Constant
            literal = self.vm.allocate()        # Literal is immediately the next frame
            self.seg = program.segments[seg_name]
            self.vm.set_bytes(self.seg.data.constant, self.regs.R8, len(self.seg.data.constant))
            self.vm.set_bytes(self.seg.data.literal, literal, len(self.seg.data.literal))
            self.loaded_seg[seg_name] = (self.seg, self.regs.R8)

    @staticmethod
    def get_ecb_address(level: str, ecb_label: str) -> int:
        # level is from D0 to DF, ecb_label is the partial label to which the level number (0-F) to be appended
        if not level.startswith('D') or len(level) != 2 or level[1] not in config.ECB_LEVELS:
            # For DECB=(R1) DECB=L1ADR
            raise TypeError
        level = f"{ecb_label}{level[1]}"
        dsp = program.macros['EB0EB'].symbol_table[level].dsp
        return config.ECB + dsp

    def _setup(self, aaa_address: int) -> None:
        address_map: Dict[str, int] = {'EB0EB': config.ECB, 'GLOBAL': config.GLOBAL, 'WA0AA': aaa_address}
        for macro_name, update_items in self.setup.items():
            base = address_map[macro_name]
            for field_name, byte_array in update_items.items():
                dsp = program.macros[macro_name].symbol_table[field_name].dsp
                self.vm.set_bytes(byte_array, base + dsp, len(byte_array))

    def init_run(self) -> None:
        self.__init__()

    def restart(self, seg_name: str, aaa: bool = False) -> None:
        self.init_run()
        self.run(seg_name, aaa)

    def run(self, seg_name: Optional[str] = None, aaa: bool = False) -> str:
        seg_name = self.seg.name if seg_name is None else seg_name
        self.init_seg(seg_name)
        self.regs.R9 = config.ECB
        aaa_address = self.vm.allocate()
        if aaa:
            # Save AAA address in CE1CR1
            self.vm.set_value(aaa_address, config.ECB + 0x170)
        self._setup(aaa_address)
        label = self.seg.root_label
        while True:
            node = self.seg.nodes[label]
            label = self.ex[node.command](node)
            if label is None:
                return node.label

    @staticmethod
    def branch(_) -> str:
        pass

    def branch_return(self, _) -> str:
        pass

    def next_label(self, node: InstructionGeneric) -> Optional[str]:
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
