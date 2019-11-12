from base64 import b64decode
from typing import Callable, Optional, Tuple, Dict, List, Set

from assembly.mac2_data_macro import macros
from assembly.seg2_ins_operand import FieldIndex
from assembly.seg3_ins_type import InstructionType
from assembly.seg6_segment import Segment, segments
from config import config
from db.pnr import PnrElement
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
            literal = self.vm.allocate()  # Literal is immediately the next frame
            self.vm.frames[self.vm.base_key(self.regs.R8)] = self.seg.data.constant
            self.vm.frames[self.vm.base_key(literal)] = self.seg.data.literal
            # self.vm.set_bytes(self.seg.data.constant, self.regs.R8, len(self.seg.data.constant))
            # self.vm.set_bytes(self.seg.data.literal, literal, len(self.seg.data.literal))
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

    def get_core_block(self, level: str, block_type: Optional[str] = None) -> int:
        address = self.vm.allocate()
        level_address = self.get_ecb_address(level, 'CE1CR')
        control_address = self.get_ecb_address(level, 'CE1CT')
        size_address = self.get_ecb_address(level, 'CE1CC')
        control_value = config.BLOCK_TYPE[block_type] if block_type in config.BLOCK_TYPE else config.BLOCK_TYPE['L4']
        size_value = config.BLOCK_SIZE[block_type] if block_type in config.BLOCK_SIZE else config.BLOCK_SIZE['L4']
        self.vm.set_value(address, level_address)
        self.vm.set_value(control_value, control_address, 2)
        self.vm.set_value(size_value, size_address, 2)
        return address


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

    def set_from_dict(self, test_data: dict) -> None:
        PnrElement.init_db()
        if 'errors' in test_data and test_data['errors']:
            self.errors = set(test_data['errors'])
        if 'cores' in test_data and test_data['cores']:
            for macro_dict in test_data['cores']:
                if 'macro_name' not in macro_dict or 'field_bytes' not in macro_dict:
                    continue
                if macro_dict['macro_name'].upper() == 'EB0EB':
                    self.ecb = self._convert_field_bytes(macro_dict['field_bytes'])
                elif macro_dict['macro_name'].upper() == 'WA0AA':
                    self.aaa = self._convert_field_bytes(macro_dict['field_bytes'])
                elif macro_dict['macro_name'].upper() == 'MI0MI':
                    self.img = self._convert_field_bytes(macro_dict['field_bytes'])
        if 'pnr' in test_data and test_data['pnr']:
            for pnr_dict in test_data['pnr']:
                if 'key' not in pnr_dict or pnr_dict['key'] not in PnrElement.ADD:
                    continue
                pnr_locator = pnr_dict['locator'] if 'locator' in pnr_dict and pnr_dict['locator'] else config.AAAPNR
                if PnrElement.ADD[pnr_dict['key']]['field_bytes']:
                    if 'field_bytes' not in pnr_dict or not pnr_dict['field_bytes']:
                        continue
                    pnr_data = self._convert_field_bytes(pnr_dict['field_bytes'])
                else:
                    if 'data' not in pnr_dict or not pnr_dict['data']:
                        continue
                    pnr_data = pnr_dict['data']
                pnr_data = [pnr_data]
                PnrElement.ADD[pnr_dict['key']]['function'](pnr_locator, pnr_data)
        return

    @staticmethod
    def _convert_field_bytes(field_byte_list: list) -> Dict[str, bytearray]:
        return {field_byte_dict['field']: bytearray(b64decode(field_byte_dict['data']))
                for field_byte_dict in field_byte_list if 'field' in field_byte_dict and 'data' in field_byte_dict}
