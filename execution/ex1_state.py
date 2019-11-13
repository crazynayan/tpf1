from base64 import b64decode, b64encode
from typing import Callable, Optional, Tuple, Dict, List, Set

from assembly.mac0_generic import LabelReference
from assembly.mac2_data_macro import macros
from assembly.seg2_ins_operand import FieldIndex
from assembly.seg3_ins_type import InstructionType
from assembly.seg6_segment import Segment, segments
from config import config
from db.pnr import PnrElement
from execution.debug import Debug
from execution.ex0_regs_store import Registers, Storage
from firestore.test_data import TestData, FieldByte, Output
from utils.data_type import DataType, Register
from utils.errors import SegmentNotFoundError, EcbLevelFormatError, PnrElementError, InvalidBaseRegError


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

    def _init_seg(self, seg_name: str) -> None:
        if seg_name in self.loaded_seg:
            self.regs.R8 = self.loaded_seg[seg_name][1]
            self.seg = self.loaded_seg[seg_name][0]
        else:
            self.seg = segments[seg_name]
            self.seg.assemble()
            self.regs.R8 = self.vm.allocate()   # Constant
            literal = self.vm.allocate()  # Literal is immediately the next frame
            self.vm.set_frame(self.seg.data.constant, self.regs.R8)
            self.vm.set_frame(self.seg.data.literal, literal)
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
            raise EcbLevelFormatError
        level = f"{ecb_label}{level[1]}"
        dsp = macros['EB0EB'].evaluate(level)
        return config.ECB + dsp

    def _setup(self) -> None:
        for byte_array, address in self.setup.yield_data():
            self.vm.set_bytes(byte_array, address, len(byte_array))

    def init_run(self) -> None:
        self.__init__()

    def run(self, seg_name: str, test_data: TestData = None) -> str:
        if seg_name not in segments:
            raise SegmentNotFoundError
        self._init_seg(seg_name)
        self.regs.R9 = config.ECB
        self._core_block(config.AAA, 'D1')
        self._core_block(config.IMG, 'D0')
        self._setup()
        if test_data:
            self._set_from_test_data(test_data)
        label = self.seg.root_label()
        node = self.seg.nodes[label]
        while True:
            label = self._ex_command(node)
            if label is None:
                break
            node = self.seg.nodes[label]
        if test_data:
            self._capture_output(test_data.outputs, node.label)
        return node.label

    def _ex_command(self, node: InstructionType) -> str:
        label = self._ex[node.command](node)
        self.DEBUG.hit(node, label)
        return label

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
        label = self.seg.get_field_name(Register('R8'), dsp, config.INSTRUCTION_LEN_DEFAULT)
        return label

    def _core_block(self, address: int, level: str, block_type: Optional[str] = None) -> None:
        level_address = self.get_ecb_address(level, 'CE1CR')
        control_address = self.get_ecb_address(level, 'CE1CT')
        size_address = self.get_ecb_address(level, 'CE1CC')
        control_value = config.BLOCK_TYPE[block_type] if block_type in config.BLOCK_TYPE else config.BLOCK_TYPE['L4']
        size_value = config.BLOCK_SIZE[block_type] if block_type in config.BLOCK_SIZE else config.BLOCK_SIZE['L4']
        self.vm.set_value(address, level_address)
        self.vm.set_value(control_value, control_address, 2)
        self.vm.set_value(size_value, size_address, 2)

    def _set_from_test_data(self, test_data: TestData) -> None:
        self.setup.errors = set(test_data.errors)
        for core in test_data.cores:
            macro_name = core.macro_name.upper()
            if macro_name == 'WA0AA':
                self._set_core(core.field_bytes, macro_name, config.AAA)
            elif macro_name == 'EB0EB':
                self._set_core(core.field_bytes, macro_name, config.ECB)
            elif macro_name == 'MI0MI':
                self._set_core(core.field_bytes, macro_name, config.IMG)
        PnrElement.init_db()
        for pnr in test_data.pnr:
            if pnr.key not in PnrElement.ADD:
                raise PnrElementError
            pnr_locator = pnr.locator if pnr.locator else config.AAAPNR
            if PnrElement.ADD[pnr.key]['field_bytes']:
                pnr_data = self._convert_field_bytes(pnr.field_bytes)
            else:
                pnr_data = pnr.data
            pnr_data = [pnr_data]
            PnrElement.ADD[pnr.key]['function'](pnr_locator, pnr_data)
        return

    def _set_core(self, field_bytes: List[FieldByte], macro_name: str, base_address: int) -> None:
        field_byte_array: Dict[str, bytearray] = self._convert_field_bytes(field_bytes)
        for field, byte_array in field_byte_array.items():
            address = macros[macro_name].evaluate(field) + base_address
            self.vm.set_bytes(byte_array, address, len(byte_array))
        return

    @staticmethod
    def _convert_field_bytes(field_bytes: List[FieldByte]) -> Dict[str, bytearray]:
        return {field_byte.field.upper(): bytearray(b64decode(field_byte.data)) for field_byte in field_bytes}

    def _capture_output(self, outputs: List[Output], last_line: str) -> None:
        if not outputs:
            output = Output()
            outputs.append(output)
        output = outputs[0]
        output.message = self.message if self.message else str()
        output.dumps.extend(self.dumps)
        output.last_line = last_line
        for core in output.cores:
            macro_name = core.macro_name.upper()
            if macro_name == 'WA0AA':
                self._capture_core(core.field_bytes, macro_name, config.AAA)
            elif macro_name == 'EB0EB':
                self._capture_core(core.field_bytes, macro_name, config.ECB)
            elif macro_name == 'MI0MI':
                self._capture_core(core.field_bytes, macro_name, config.IMG)
            elif macro_name in macros:
                if not Register(core.base_reg).is_valid():
                    raise InvalidBaseRegError
                self._capture_core(core.field_bytes, macro_name, self.regs.get_unsigned_value(core.base_reg))
        for reg in output.regs:
            if not Register(reg).is_valid():
                raise InvalidBaseRegError
            output.regs[reg] = self.regs.get_value(reg)

    def _capture_core(self, field_bytes: List[FieldByte], macro_name: str, base_address: int) -> None:
        for field_byte in field_bytes:
            field: LabelReference = macros[macro_name].lookup(field_byte.field.upper())
            address = field.dsp + base_address
            length = field_byte.length if field_byte.length > 0 else field.length
            field_byte.data = b64encode(self.vm.get_bytes(address, length)).decode()
        return


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
