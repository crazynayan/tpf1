from typing import Callable, Optional, Tuple, Dict, List, Set

from assembly.mac2_data_macro import macros
from assembly.seg2_ins_operand import FieldIndex
from assembly.seg3_ins_type import InstructionType
from assembly.seg6_segment import Segment, segments
from config import config
from execution.debug import Debug
from execution.ex0_regs_store import Registers, Storage
from utils.data_type import DataType, Register


class State:
    DEBUG: Debug = Debug()

    def __init__(self):
        self.seg: Optional[Segment] = None
        self.regs: Registers = Registers()
        self.vm: Storage = Storage()
        self.cc: Optional[int] = None
        self._ex: Dict[str, Callable] = dict()
        self.detac_stack: Dict[str, List] = {level: list() for level in config.ECB_LEVELS}
        self.message: Optional[str] = None
        self.dumps: List[str] = list()
        self.heap: Dict[str, int] = dict()
        self.call_stack: List[Tuple[str, str]] = list()
        self.loaded_seg: Dict[str, Tuple[Segment, int]] = dict()
        self.tpfdf_ref: Dict[str, int] = dict()
        self.setup: Setup = Setup()

    def __repr__(self) -> str:
        return f"State:{self.seg}:{self.regs}:{self.vm}"

    def init_seg(self, seg_name: str) -> None:
        if seg_name in self.loaded_seg:
            self.regs.R8 = self.loaded_seg[seg_name][1]
            self.seg = self.loaded_seg[seg_name][0]
        else:
            self.seg = segments[seg_name]
            self.seg.assemble()
            self.regs.R8 = self.vm.allocate()   # Constant
            literal = self.vm.allocate()        # Literal is immediately the next frame
            self.vm.set_bytes(self.seg.data.constant, self.regs.R8, len(self.seg.data.constant))
            self.vm.set_bytes(self.seg.data.literal, literal, len(self.seg.data.literal))
            self.loaded_seg[seg_name] = (self.seg, self.regs.R8)

    def init_debug(self, seg_list: List[str]) -> None:
        nodes = dict()
        for seg_name in seg_list:
            segments[seg_name].assemble()
            nodes = {**nodes, **segments[seg_name].nodes}
        self.DEBUG.init_trace(nodes, seg_list)

    @staticmethod
    def get_ecb_address(level: str, ecb_label: str) -> int:
        # level is from D0 to DF, ecb_label is the partial label to which the level number (0-F) to be appended
        if not level.startswith('D') or len(level) != 2 or level[1] not in config.ECB_LEVELS:
            # For DECB=(R1) DECB=L1ADR
            raise TypeError
        level = f"{ecb_label}{level[1]}"
        dsp = macros['EB0EB'].evaluate(level)
        return config.ECB + dsp

    def _setup(self) -> None:
        for byte_array, address in self.setup.yield_data():
            self.vm.set_bytes(byte_array, address, len(byte_array))

    def init_run(self) -> None:
        self.__init__()

    def restart(self, seg_name: str, aaa: bool = False) -> None:
        self.init_run()
        self.run(seg_name, aaa)

    def run(self, seg_name: Optional[str] = None, aaa: bool = False) -> str:
        seg_name = self.seg.name if seg_name is None else seg_name
        self.init_seg(seg_name)
        self.regs.R9 = config.ECB
        if aaa:
            self.vm.set_value(config.AAA, config.ECB + 0x170)  # Save AAA address in CE1CR1
        self._setup()
        label = self.seg.root_label()
        while True:
            node = self.seg.nodes[label]
            label = self.ex_command(node)
            if label is None:
                return node.label

    def ex_command(self, node: InstructionType) -> str:
        label = self._ex[node.command](node)
        self.DEBUG.hit(node, label)
        return label

    @staticmethod
    def branch(_) -> str:
        pass

    def branch_return(self, _) -> str:
        pass

    def set_number_cc(self, number: int) -> None:
        if number > 0:
            self.cc = 2
        elif number == 0:
            self.cc = 0
        else:
            self.cc = 1

    def set_zero_cc(self, number: int) -> None:
        self.cc = 1 if number else 0

    def set_partition(self, partition: str) -> None:
        haalc = config.GLOBAL + macros['GLOBAL'].evaluate('@HAALC')
        ce1uid = config.ECB + macros['EB0EB'].evaluate('CE1$UID')
        self.vm.set_bytes(DataType('C', input=partition).to_bytes(), haalc, 2)
        self.vm.set_value(config.PARTITION[partition], ce1uid, 1)

    def is_error(self, label: str) -> bool:
        return label in self.setup.errors

    def index_to_label(self, field: FieldIndex) -> str:
        if field.index.reg == 'R0':
            return field.name
        dsp = self.regs.get_address(field.index, field.dsp)
        label = self.seg.get_field_name(Register('R8'), dsp, 4)
        return label


class Setup:
    def __init__(self):
        self.ecb: Dict[str, bytearray] = dict()
        self.img: Dict[str, bytearray] = dict()
        self.aaa: Dict[str, bytearray] = dict()
        self.errors: Set[str] = set()

    def yield_data(self) -> Tuple[bytearray, int]:
        for label, byte_array in self.ecb.items():
            dsp = macros['EB0EB'].evaluate(label)
            yield byte_array, config.ECB + dsp
        for label, byte_array in self.img.items():
            dsp = macros['MI0MI'].evaluate(label)
            yield byte_array, config.IMG + dsp
        for label, byte_array in self.aaa.items():
            dsp = macros['WA0AA'].evaluate(label)
            yield byte_array, config.AAA + dsp
