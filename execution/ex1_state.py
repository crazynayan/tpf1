from base64 import b64encode, b64decode
from copy import deepcopy
from typing import Callable, Optional, Tuple, Dict, List, Set

from assembly.mac0_generic import LabelReference
from assembly.mac2_data_macro import macros
from assembly.seg2_ins_operand import FieldIndex
from assembly.seg3_ins_type import InstructionType
from assembly.seg6_segment import Segment, segments
from config import config
from db.flat_file import FlatFile
from db.pnr import Pnr
from db.stream import Stream
from db.test_data import TestData
from db.test_data_elements import Output
from db.tpfdf import Tpfdf
from execution.debug import Debug
from execution.ex0_regs_store import Registers, Storage
from test import FieldByte
from utils.data_type import DataType, Register
from utils.errors import SegmentNotFoundError, EcbLevelFormatError, InvalidBaseRegError, TpfdfError, PartitionError, \
    FileItemSpecificationError, PoolFileSpecificationError, BaseAddressError


class State:
    DEBUG: Debug = Debug()

    def __init__(self):
        self.seg: Optional[Segment] = None
        self.regs: Registers = Registers()
        self.vm: Storage = Storage()
        self.cc: Optional[int] = None
        self._ex: Dict[str, Callable] = dict()
        self.detac_stack: Dict[str, List] = {level: list() for level in config.ECB_LEVELS}
        self.messages: List[str] = list()
        self.dumps: List[str] = list()
        self.heap: Dict[str, int] = dict()
        self.call_stack: List[Tuple[str, str]] = list()
        self.loaded_seg: Dict[str, Tuple[Segment, int]] = dict()
        self.tpfdf_ref: Dict[str, int] = dict()
        self.errors: Set[str] = set()

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

    def init_run(self) -> None:
        self.__init__()

    def run(self, seg_name: str, test_data: TestData) -> TestData:
        if seg_name not in segments:
            raise SegmentNotFoundError
        outputs = list()
        for test_data_variant in test_data.yield_variation():
            self.init_run()
            self._init_seg(seg_name)
            self.regs.R9 = config.ECB
            self._core_block(config.AAA, 'D1')
            self._core_block(config.IMG, 'D0')
            self._set_from_test_data(test_data_variant)
            label = self.seg.root_label()
            node = self.seg.nodes[label]
            while True:
                label = self._ex_command(node)
                if label is None:
                    break
                node = self.seg.nodes[label]
            self._capture_output(test_data_variant.output, node.label)
            outputs.append(test_data_variant.output)
        test_data = deepcopy(test_data)
        test_data.outputs = outputs
        return test_data

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
        if partition not in config.PARTITION:
            raise PartitionError
        haalc = config.GLOBAL + macros['GLOBAL'].evaluate('@HAALC')
        ce1uid = config.ECB + macros['EB0EB'].evaluate('CE1$UID')
        self.vm.set_bytes(DataType('C', input=partition).to_bytes(), haalc, 2)
        self.vm.set_value(config.PARTITION[partition], ce1uid, 1)

    def is_error(self, label: str) -> bool:
        return label in self.errors

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

    @staticmethod
    def _field_data_to_bytearray(field_data: List[dict]):
        return {field_dict['field']: bytearray(b64decode(field_dict['data'])) for field_dict in field_data}

    def _set_from_test_data(self, test_data: TestData) -> None:
        self.errors = set(test_data.errors)
        if test_data.output.debug:
            self.init_debug(test_data.output.debug)
        if test_data.partition:
            self.set_partition(test_data.partition)
        for core in test_data.cores:
            macro_name = core.macro_name.upper()
            if macro_name in config.DEFAULT_MACROS:
                self._set_core(core.field_data, macro_name, config.DEFAULT_MACROS[macro_name])
        for reg, value in test_data.regs.items():
            self.regs.set_value(value, reg)
        Pnr.init_db()
        for pnr in test_data.pnr:
            pnr_locator = pnr.locator if pnr.locator else config.AAAPNR
            if pnr.data:
                Pnr.add_from_data(pnr.data, pnr.key, pnr_locator)
            else:
                Pnr.add_from_byte_array(self._field_data_to_bytearray(pnr.field_data), pnr.key, pnr_locator)
        Tpfdf.init_db()
        for lrec in test_data.tpfdf:
            if lrec.macro_name not in macros:
                raise TpfdfError
            lrec_data = self._field_data_to_bytearray(lrec.field_data)
            Tpfdf.add(lrec_data, lrec.key, lrec.macro_name)
        self._capture_file(test_data)
        return

    @staticmethod
    def _capture_file(test_data: TestData):
        FlatFile.init_db()
        for fixed_file in test_data.fixed_files:
            fixed_dict = dict()
            for pool_file in fixed_file.pool_files:
                item_list = list()
                count_field = None
                item_field = None
                for item in pool_file.file_items:
                    if not macros[pool_file.macro_name].check(item.field):
                        raise FileItemSpecificationError
                    if item.count_field:
                        if not macros[pool_file.macro_name].check(item.count_field):
                            raise FileItemSpecificationError
                        count_field = item.count_field
                    item_field = item.field
                    item_list.append(FieldByte.to_dict(item.field_bytes))
                pool_file_bytes_dict = FieldByte.to_dict(pool_file.field_bytes) if pool_file.field_bytes else None
                if item_field:
                    data_bytes = Stream(macros[pool_file.macro_name]).item_to_bytes(item_list, item_field, count_field,
                                                                                    pool_file_bytes_dict)
                elif pool_file_bytes_dict:
                    data_bytes = Stream(macros[pool_file.macro_name]).to_bytes(pool_file_bytes_dict)
                else:
                    raise PoolFileSpecificationError
                pool_address = FlatFile.add_pool(data_bytes, pool_file.rec_id)
                if pool_file.forward_chain_count and not item_field:
                    raise PoolFileSpecificationError
                empty_items = [{field: bytearray([config.ZERO] * len(byte_array))
                                for field, byte_array in item_dict.items()}
                               for item_dict in item_list]
                for _ in range(pool_file.forward_chain_count):
                    fch_dict = {pool_file.forward_chain_label: DataType('F', input=str(pool_address)).to_bytes()}
                    if pool_file_bytes_dict:
                        fch_dict = {**fch_dict, **pool_file_bytes_dict}
                    data_bytes = Stream(macros[pool_file.macro_name]).item_to_bytes(empty_items, item_field,
                                                                                    count_field, fch_dict)
                    pool_address = FlatFile.add_pool(data_bytes, pool_file.rec_id)
                index_dict = {pool_file.index_field: DataType('F', input=str(pool_address)).to_bytes()}
                fixed_dict = {**fixed_dict, **index_dict}
            # Fixed File
            if fixed_file.field_bytes:
                fixed_dict = {**fixed_dict, **FieldByte.to_dict(fixed_file.field_bytes)}
            if not fixed_dict:
                raise PoolFileSpecificationError
            data_bytes = Stream(macros[fixed_file.macro_name]).to_bytes(fixed_dict)
            FlatFile.add_fixed(data_bytes, fixed_file.rec_id, fixed_file.fixed_type, fixed_file.fixed_ordinal)
            # TODO Fixed File items and multiple level indexes to be coded later when scenario is with us
        return

    def _set_core(self, field_bytes: List[dict], macro_name: str, base_address: int) -> None:
        field_byte_array: Dict[str, bytearray] = self._field_data_to_bytearray(field_bytes)
        for field, byte_array in field_byte_array.items():
            address = macros[macro_name].evaluate(field) + base_address
            self.vm.set_bytes(byte_array, address, len(byte_array))
        return

    def _capture_output(self, output: Output, last_line: str) -> None:
        output.messages = self.messages.copy()
        output.dumps.extend(self.dumps)
        output.last_line = last_line
        if output.debug:
            output.debug = self.DEBUG.get_trace()
        for core in output.cores:
            macro_name = core.macro_name.upper()
            if macro_name in config.DEFAULT_MACROS:
                self._capture_core(core.field_data, macro_name, config.DEFAULT_MACROS[macro_name])
            elif macro_name in macros:
                if not Register(core.base_reg).is_valid():
                    raise InvalidBaseRegError
                self._capture_core(core.field_data, macro_name, self.regs.get_unsigned_value(core.base_reg))
        for reg in output.regs:
            output.regs[reg] = self.regs.get_value(reg)
        for reg in output.reg_pointers:
            try:
                output.reg_pointers[reg] = self.vm.get_bytes(self.regs.get_unsigned_value(reg),
                                                             output.reg_pointers[reg]).hex().upper()
            except BaseAddressError:
                continue
        return

    def _capture_core(self, field_bytes: List[dict], macro_name: str, base_address: int) -> None:
        for field_byte in field_bytes:
            field: LabelReference = macros[macro_name].lookup(field_byte['field'].upper())
            address = field.dsp + base_address
            length = field_byte['length'] if field_byte['length'] > 0 else field.length
            field_byte['data'] = b64encode(self.vm.get_bytes(address, length)).decode()
        return
