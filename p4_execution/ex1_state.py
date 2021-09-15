from base64 import b64encode, b64decode
from copy import deepcopy
from datetime import datetime
from typing import Callable, Optional, Tuple, Dict, List, Set

from config import config
from p1_utils.data_type import DataType, Register
from p1_utils.errors import SegmentNotFoundError, EcbLevelFormatError, InvalidBaseRegError, TpfdfError, \
    PartitionError, FileItemSpecificationError, PoolFileSpecificationError, BaseAddressError, ExecutionError, \
    TPFServerMemoryError, LevtaExecutionError, NotImplementedExecutionError
from p2_assembly.mac0_generic import LabelReference
from p2_assembly.mac2_data_macro import macros
from p2_assembly.seg2_ins_operand import FieldIndex
from p2_assembly.seg3_ins_type import InstructionType
from p2_assembly.seg6_segment import Segment, segments
from p3_db.flat_file import FlatFile
from p3_db.pnr import Pnr
from p3_db.stream import Stream
from p3_db.test_data import TestData
from p3_db.test_data_elements import Output
from p3_db.tpfdf import Tpfdf
from p4_execution.debug import Debug
from p4_execution.ex0_regs_store import Registers, Storage


class State:

    def __init__(self):
        self.seg: Optional[Segment] = None
        self.regs: Registers = Registers()
        self.vm: Storage = Storage()
        self.cc: int = 0
        self._ex: Dict[str, Callable] = dict()
        self.detac_stack: Dict[str, List] = {level: list() for level in config.ECB_LEVELS}
        self.messages: List[str] = list()
        self.dumps: List[str] = list()
        self.heap: Dict[str, Dict[str, int]] = {"old": dict(), "new": dict()}
        self.call_stack: List[Tuple[str, str]] = list()
        self.loaded_seg: Dict[str, Tuple[Segment, int]] = dict()
        self.tpfdf_ref: Dict[str, int] = dict()
        self.errors: Set[str] = set()
        self.debug: Debug = Debug()
        self.fields: dict = {"CE3ENTPGM": bytearray()}
        self.stop_segments: List[str] = list()

    def __repr__(self) -> str:
        return f"State:{self.seg}:{self.regs}:{self.vm}"

    def _init_seg(self, seg_name: str) -> None:
        if seg_name in self.loaded_seg:
            self.regs.R8 = self.loaded_seg[seg_name][1]
            self.seg = self.loaded_seg[seg_name][0]
        else:
            self.seg = segments[seg_name]
            self.seg.assemble()
            self.regs.R8 = self.vm.allocate()  # Constant
            literal = self.vm.allocate()  # Literal is immediately the next frame
            self.vm.set_frame(self.seg.data.constant, self.regs.R8)
            self.vm.set_frame(self.seg.data.literal, literal)
            self.loaded_seg[seg_name] = (self.seg, self.regs.R8)

    def init_debug(self, seg_list: List[str]) -> None:
        for seg_name in seg_list:
            segments[seg_name].assemble()
            self.debug.add_trace(segments[seg_name].nodes, seg_name)
        return

    @staticmethod
    def get_ecb_address(d_level: str, ecb_label: str) -> int:
        level = d_level if d_level in config.ECB_LEVELS else str()
        if not level:
            if not d_level.startswith("D") or len(d_level) != 2 or d_level[1] not in config.ECB_LEVELS:
                # For DECB=(R1) DECB=L1ADR
                raise EcbLevelFormatError
            # level is from D0 to DF, ecb_label is the partial label to which the level number (0-F) to be appended
            level = d_level[1]
        ecb_label_level = f"{ecb_label}{level}"
        dsp = macros["EB0EB"].evaluate(ecb_label_level)
        return config.ECB + dsp

    def _init_ecb(self) -> None:
        self.regs.R9 = config.ECB
        for level in config.ECB_LEVELS:
            ce1ct = self.get_ecb_address(f"D{level}", "CE1CT")
            self.vm.set_value(1, ce1ct + 1, 1)

    def _init_globals(self) -> None:
        for global_name in ("@MH00C", "@APCIB"):
            address = config.GLOBAL + macros["GLOBAL"].evaluate(global_name)
            self.vm.set_value(self.vm.allocate(), address)
        haalc = config.GLOBAL + macros["GLOBAL"].evaluate("@HAALC")
        self.vm.set_bytes(bytearray([0xC1, 0xC1]), haalc, 2)
        u1dmo = config.GLOBAL + macros["GLOBAL"].evaluate("@U1DMO")
        now = datetime.utcnow()
        today = datetime(year=now.year, month=now.month, day=now.day)
        pars_today = (today - config.PARS_DAY_1).days
        self.vm.set_value(pars_today, u1dmo, 2)
        tjord = config.GLOBAL + macros["GLOBAL"].evaluate("@TJORD")
        self.vm.set_value(0x00088EDC, tjord)
        multi_host = config.GLOBAL + macros["GLOBAL"].evaluate("@MHSTC")
        self.vm.set_value(config.MULTI_HOST, multi_host)
        u1tym = config.GLOBAL + macros["GLOBAL"].evaluate("@U1TYM")
        time: str = f"{now.hour:02}{now.minute:02}"
        time_bytes: bytearray = DataType("C", input=time).to_bytes()
        self.vm.set_bytes(time_bytes, u1tym, len(time_bytes))

    def init_run(self, seg_name) -> None:
        self.__init__()
        self._init_seg(seg_name)
        self._init_ecb()
        self._init_globals()
        self._core_block(config.AAA, "D1")
        self._core_block(config.IMG, "D0")

    def run(self, seg_name: str, test_data: TestData) -> TestData:
        if seg_name not in segments:
            raise SegmentNotFoundError
        outputs = list()
        for test_data_variant in test_data.yield_variation():
            self.init_run(seg_name)
            self._set_from_test_data(test_data_variant)
            label = self.seg.root_label()
            node: InstructionType = self.seg.nodes[label]
            try:
                for _ in range(10000000):
                    label = self._ex_command(node)
                    if label is None:
                        break
                    node = self.seg.nodes[label]
                if label is not None:
                    self.dumps.append("000010")
                    self.messages.append("INFINITE LOOP ERROR")
            except ExecutionError:
                self.dumps.append("000003")
                self.messages.append("EXECUTION ERROR")
            except KeyError:
                raise ExecutionError(node)
            except TPFServerMemoryError:
                self.dumps.append("000004")
                self.messages.append("MEMORY ERROR")
            self._capture_output(test_data_variant.output, node)
            outputs.append(test_data_variant.output)
        output_test_data = deepcopy(test_data)
        output_test_data.outputs = outputs
        return output_test_data

    def _ex_command(self, node: InstructionType, execute_label: Optional[str] = None) -> str:
        seg_name = self.seg.seg_name
        if node.command not in self._ex:
            raise NotImplementedExecutionError(node)
        label = self._ex[node.command](node)
        next_label = str() if execute_label else label
        self.debug.hit(node, next_label, seg_name)
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
        haalc = config.GLOBAL + macros["GLOBAL"].evaluate("@HAALC")
        ce1uid = config.ECB + macros["EB0EB"].evaluate("CE1$UID")
        self.vm.set_bytes(DataType("C", input=partition).to_bytes(), haalc, 2)
        self.vm.set_value(config.PARTITION[partition], ce1uid, 1)
        # TODO Switch MH Base

    def get_partition(self) -> str:
        airline_code = self.vm.get_bytes(config.GLOBAL + macros["GLOBAL"].evaluate("@HAALC"), 2)
        return DataType("X", bytes=airline_code).decode

    def is_error(self, label: str) -> bool:
        return label in self.errors

    def index_to_label(self, field: FieldIndex) -> str:
        if field.index.reg == "R0":
            return field.name
        dsp = self.regs.get_address(field.index, field.dsp)
        label = self.seg.get_field_name(Register("R8"), dsp, config.INSTRUCTION_LEN_DEFAULT)
        return label

    def _core_block(self, address: int, level: str, block_type: Optional[str] = None) -> None:
        level_address = self.get_ecb_address(level, "CE1CR")
        control_address = self.get_ecb_address(level, "CE1CT")
        size_address = self.get_ecb_address(level, "CE1CC")
        control_value = config.BLOCK_TYPE[block_type] if block_type in config.BLOCK_TYPE else config.BLOCK_TYPE["L4"]
        size_value = config.BLOCK_SIZE[block_type] if block_type in config.BLOCK_SIZE else config.BLOCK_SIZE["L4"]
        self.vm.set_value(address, level_address)
        self.vm.set_value(control_value, control_address, 2)
        self.vm.set_value(size_value, size_address, 2)

    def _is_level_present(self, level: str) -> bool:
        if level not in config.ECB_LEVELS:
            raise LevtaExecutionError
        control_value = self.vm.get_value(self.get_ecb_address(f"D{level}", "CE1CT"), 2)
        return False if control_value == 0x01 or control_value == 0x00 else True

    @staticmethod
    def _field_data_to_bytearray(field_data: List[dict]):
        return {field_dict["field"]: bytearray(b64decode(field_dict["data"])) for field_dict in field_data}

    def _set_from_test_data(self, test_data: TestData) -> None:
        self.errors = set(test_data.errors)
        self.stop_segments = test_data.stop_segments
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

    def _capture_file(self, test_data: TestData):
        FlatFile.init_db()
        for fixed_file in test_data.fixed_files:
            fixed_dict = dict()
            for pool_file in fixed_file.pool_files:
                item_list = list()
                count_field = None
                item_field = None
                macros[pool_file.macro_name].load()
                for item in pool_file.file_items:
                    if not macros[pool_file.macro_name].check(item.field):
                        raise FileItemSpecificationError
                    if item.count_field:
                        if not macros[pool_file.macro_name].check(item.count_field):
                            raise FileItemSpecificationError
                        count_field = item.count_field
                    item_field = item.field
                    for _ in range(item.repeat):
                        item_list.append(self._field_data_to_bytearray(item.field_data))
                pool_file_bytes_dict = self._field_data_to_bytearray(pool_file.field_data) if pool_file.field_data \
                    else None
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
                    fch_dict = {pool_file.forward_chain_label: DataType("F", input=str(pool_address)).to_bytes()}
                    if pool_file_bytes_dict:
                        fch_dict = {**fch_dict, **pool_file_bytes_dict}
                    data_bytes = Stream(macros[pool_file.macro_name]).item_to_bytes(empty_items, item_field,
                                                                                    count_field, fch_dict)
                    pool_address = FlatFile.add_pool(data_bytes, pool_file.rec_id)
                index_dict = {pool_file.index_field: DataType("F", input=str(pool_address)).to_bytes()}
                fixed_dict = {**fixed_dict, **index_dict}
            # Fixed File
            fixed_dict = {**fixed_dict, **self._field_data_to_bytearray(fixed_file.field_data)} \
                if fixed_file.field_data else fixed_dict
            if fixed_file.file_items:
                item_list = list()
                for item in fixed_file.file_items:
                    if not macros[fixed_file.macro_name].check(item.field):
                        raise FileItemSpecificationError
                    if item.count_field:
                        if not macros[fixed_file.macro_name].check(item.count_field):
                            raise FileItemSpecificationError
                    for _ in range(item.repeat):
                        item_list.append(self._field_data_to_bytearray(item.field_data))
                data_bytes = Stream(macros[fixed_file.macro_name]) \
                    .item_to_bytes(item_list, fixed_file.file_items[0].field, fixed_file.file_items[0].count_field,
                                   fixed_dict, fixed_file.file_items[0].adjust)
            elif fixed_dict:
                data_bytes = Stream(macros[fixed_file.macro_name]).to_bytes(fixed_dict)
            else:
                raise PoolFileSpecificationError
            FlatFile.add_fixed(data_bytes, fixed_file.rec_id, fixed_file.fixed_type, fixed_file.fixed_ordinal)
            # TODO multiple level indexes to be coded later when scenario is with us
        return

    def _set_core(self, field_data: List[dict], macro_name: str, base_address: int) -> None:
        field_byte_array: Dict[str, bytearray] = self._field_data_to_bytearray(field_data)
        for field, byte_array in field_byte_array.items():
            address = macros[macro_name].evaluate(field) + base_address
            self.vm.set_bytes(byte_array, address, len(byte_array))
        return

    def _capture_output(self, output: Output, last_node: InstructionType) -> None:
        output.messages = self.messages.copy()
        output.dumps.extend(self.dumps)
        output.last_line = last_node.label
        output.last_node = str(last_node)
        if output.debug:
            output.debug = self.debug.get_traces(hit=True)
            output.debug_missed = self.debug.get_traces(hit=False)
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
        self._capture_output_pnr(output)
        return

    @staticmethod
    def _capture_output_pnr(output: Output) -> None:
        for pnr_output in output.pnr_outputs:
            key = Pnr.get_attribute_by_name(pnr_output.key).key
            item_number = pnr_output.position
            pnr_locator = config.AAAPNR if not pnr_output.locator else pnr_output.locator
            data = Pnr.get_pnr_data(pnr_locator=pnr_locator, key=key, item_number=item_number, packed=True)
            pnr_data: bytearray = data[0]
            if not pnr_data:
                continue
            for field, length in pnr_output.field_len.items():
                if not macros["PR001W"].check(field):
                    continue
                label_ref: LabelReference = macros["PR001W"].lookup(field)
                if not isinstance(length, int):
                    continue
                field_len: int = length if length > 0 else label_ref.length
                start: int = label_ref.dsp
                end: int = start + field_len
                if len(pnr_data) < end:
                    continue
                field_byte = dict()
                field_byte["field"] = field
                field_byte["data"] = b64encode(pnr_data[start:end]).decode()
                pnr_output.field_data.append(field_byte)
        return

    def _capture_core(self, field_data: List[dict], macro_name: str, base_address: int) -> None:
        for field_byte in field_data:
            field: LabelReference = macros[macro_name].lookup(field_byte["field"].upper())
            address = field.dsp + base_address
            length = field_byte["length"] if field_byte["length"] > 0 else field.length
            field_byte["data"] = b64encode(self.vm.get_bytes(address, length)).decode()
        return
