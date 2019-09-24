from typing import Callable, Optional, Tuple, Dict, List

from config import config
from execution.regs_store import Registers, Storage
from v2.instruction_type import InstructionGeneric
from v2.segment import Program, Segment


class State:
    def __init__(self, global_program: Program):
        self.global_program: Program = global_program
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

    def __repr__(self) -> str:
        return f"State:{self.seg}:{self.regs}:{self.vm}"

    def init_seg(self, seg_name: str) -> None:
        if seg_name in self.loaded_seg:
            self.regs.R8 = self.loaded_seg[seg_name][1]
            self.seg = self.loaded_seg[seg_name][0]
        else:
            self.global_program.load(seg_name)
            self.regs.R8 = self.vm.allocate()   # Constant
            literal = self.vm.allocate()        # Literal is immediately the next frame
            self.seg = self.global_program.segments[seg_name]
            self.vm.set_bytes(self.seg.data.constant, self.regs.R8, len(self.seg.data.constant))
            self.vm.set_bytes(self.seg.data.literal, literal, len(self.seg.data.literal))
            self.loaded_seg[seg_name] = (self.seg, self.regs.R8)

    def validate(self, address: int) -> int:
        return address if address else self.vm.allocate()

    def get_ecb_address(self, level: str, ecb_label: str) -> int:
        # level is from D0 to DF, ecb_label is the partial label to which the level number (0-F) to be appended
        if not level.startswith('D') or len(level) != 2 or level[1] not in config.ECB_LEVELS:
            # For DECB=(R1) DECB=L1ADR
            raise TypeError
        level = f"{ecb_label}{level[1]}"
        dsp = self.global_program.macros['EB0EB'].symbol_table[level].dsp
        return config.ECB + dsp

    def restart(self, seg_name: str) -> None:
        self.regs = Registers()
        self.vm = Storage()
        self.loaded_seg = dict()
        self.run(seg_name)

    def run(self, seg_name: Optional[str] = None) -> None:
        seg_name = self.seg.name if seg_name is None else seg_name
        self.init_seg(seg_name)
        self.regs.R9 = config.ECB
        label = self.seg.root_label
        while label:
            node = self.seg.nodes[label]
            label = self.ex[node.command](node)

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
