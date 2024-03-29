from base64 import b64encode, b64decode
from copy import deepcopy
from datetime import datetime
from itertools import groupby
from typing import Callable, Optional, Tuple, Dict, List, Set

from d21_backend.config import config
from d21_backend.p1_utils.data_type import DataType, Register
from d21_backend.p1_utils.errors import SegmentNotFoundError, EcbLevelFormatError, InvalidBaseRegError, TpfdfError, \
    PartitionError, FileItemSpecificationError, PoolFileSpecificationError, BaseAddressError, ExecutionError, \
    TPFServerMemoryError, LevtaExecutionError, NotImplementedExecutionError, BctExecutionError, \
    NotFoundInSymbolTableError
from d21_backend.p1_utils.file_line import Line
from d21_backend.p2_assembly.mac0_generic import LabelReference
from d21_backend.p2_assembly.mac2_data_macro import get_macros, get_global_address
from d21_backend.p2_assembly.seg2_ins_operand import FieldIndex
from d21_backend.p2_assembly.seg3_ins_type import InstructionType
from d21_backend.p2_assembly.seg5_exec_macro import KeyValue
from d21_backend.p2_assembly.seg6_segment import Segment, get_assembled_startup_seg
from d21_backend.p2_assembly.seg9_collection import get_seg_collection
from d21_backend.p3_db.flat_file import FlatFile
from d21_backend.p3_db.pnr import Pnr
from d21_backend.p3_db.stream import Stream
from d21_backend.p3_db.test_data import TestData
from d21_backend.p3_db.test_data_elements import Output, Core
from d21_backend.p3_db.tpfdf import Tpfdf
from d21_backend.p4_execution.debug import Debug
from d21_backend.p4_execution.ex0_regs_store import Registers, Storage
from d21_backend.p4_execution.profiler import SegmentProfiler
from d21_backend.p4_execution.trace import TraceList, TraceData


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
        self.trace_list: TraceList = TraceList()
        self.trace_data: TraceData = TraceData()
        self.fields: dict = {"CE3ENTPGM": bytearray()}
        self.stop_segments: List[str] = list()
        self.instruction_counter: int = 0
        self.aaa_field_data: List[dict] = list()
        self._ex: Dict[str, callable] = dict()

    def __repr__(self) -> str:
        return f"State:{self.seg}:{self.regs}:{self.vm}"

    def _init_seg(self, seg_name: str) -> None:
        self.instruction_counter = 0
        if seg_name in self.loaded_seg:
            self.regs.R8 = self.loaded_seg[seg_name][1]
            self.seg = self.loaded_seg[seg_name][0]
        else:
            if seg_name != Segment.STARTUP:
                self.seg = get_seg_collection().get_seg(seg_name)
                if not self.seg:
                    raise SegmentNotFoundError
                self.seg.assemble()
            self.regs.R8 = self.vm.allocate()  # Constant
            literal = self.vm.allocate()  # Literal is immediately the next frame
            self.vm.set_frame(self.seg.data.constant, self.regs.R8)
            self.vm.set_frame(self.seg.data.literal, literal)
            self.loaded_seg[seg_name] = (self.seg, self.regs.R8)

    def init_debug(self, test_data: TestData) -> None:
        if test_data.output.debug:
            self.trace_list.seg_list = [seg_name for seg_name in test_data.output.debug]
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
        dsp = get_macros()["EB0EB"].evaluate(ecb_label_level)
        return config.ECB + dsp

    def _init_ecb(self) -> None:
        self.regs.R9 = config.ECB
        for level in config.ECB_LEVELS:
            ce1ct = self.get_ecb_address(f"D{level}", "CE1CT")
            self.vm.set_value(1, ce1ct + 1, 1)

    @staticmethod
    def _evaluate_global(name: str) -> int:
        try:
            return get_global_address(name)
        except NotFoundInSymbolTableError:
            raise ExecutionError

    def _init_globals(self) -> None:
        ce1gla = self.seg.evaluate("CE1GLA") if self.seg.check("CE1GLA") else 0x300
        ce1gly = self.seg.evaluate("CE1GLY") if self.seg.check("CE1GLY") else 0x304
        gbsbc = self._evaluate_global("@GBSBC")
        multi_host = self._evaluate_global("@MHSTC")
        self.vm.set_value(config.GLOBAS, self.regs.R9 + ce1gla)
        self.vm.set_value(config.GLOBYS, self.regs.R9 + ce1gly)
        self.vm.set_value(config.GL0BS, gbsbc)
        self.vm.set_value(config.MULTI_HOST, multi_host)
        haalc = self._evaluate_global("@HAALC")
        self.vm.set_bytes(bytearray([0xC1, 0xC1]), haalc, 2)
        u1dmo = self._evaluate_global("@U1DMO")
        now = datetime.utcnow()
        today = datetime(year=now.year, month=now.month, day=now.day)
        pars_today = (today - config.PARS_DAY_1).days
        self.vm.set_value(pars_today, u1dmo, 2)
        u1tym = self._evaluate_global("@U1TYM")
        time: str = f"{now.hour:02}{now.minute:02}"
        time_bytes: bytearray = DataType("C", input=time).to_bytes()
        self.vm.set_bytes(time_bytes, u1tym, len(time_bytes))

    def init_run(self, seg_name) -> None:
        self.__init__()
        self._init_seg(seg_name)
        self._init_ecb()
        self._init_globals()
        self._core_block(config.IMG, "D0")
        Pnr.init_db()
        Tpfdf.init_db()
        FlatFile.init_db()

    def run(self, seg_name: str, test_data: TestData, profiler: SegmentProfiler = None) -> TestData:
        if not get_seg_collection().is_seg_present(seg_name):
            raise SegmentNotFoundError
        outputs = list()
        startup_seg: Segment = get_assembled_startup_seg(test_data.startup_script)
        startup_error: str = startup_seg.error_line or startup_seg.error_constant
        for test_data_variant in test_data.yield_variation():
            self.init_run(seg_name)
            self.init_debug(test_data_variant)
            if test_data.startup_script and not startup_error:
                self.seg = startup_seg
                self._init_seg(startup_seg.seg_name)
                node = self.run_seg()
            if not self.dumps:
                self._init_seg(seg_name)
                self.init_aaa_field_data(test_data_variant)
                self.init_aaa()
                self._set_from_test_data(test_data_variant)
                node = self.run_seg(profiler)
            # noinspection PyUnboundLocalVariable
            self._capture_output(test_data_variant.output, node)
            outputs.append(test_data_variant.output)
        output_test_data = deepcopy(test_data)
        for index, output in enumerate(outputs):
            output.result_id = index + 1
        output_test_data.outputs = outputs
        return output_test_data

    def run_seg(self, profiler: SegmentProfiler = None) -> InstructionType:
        label = self.seg.root_label()
        node = self.seg.equ(Line.from_line(f"{label} EQU 0"))
        try:
            if not self.seg.nodes:
                raise ExecutionError
            node: InstructionType = self.seg.nodes[label]
            while self.instruction_counter < 2000:
                label = self._ex_command(node, profiler)
                if label is None:
                    break
                node = self.seg.nodes[label]
                self.instruction_counter += 1
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
        return node

    def _ex_command(self, node: InstructionType, profiler: SegmentProfiler = None) -> str:
        seg_name = self.seg.seg_name
        self.trace_data = TraceData()
        if node.command not in self._ex:
            raise NotImplementedExecutionError(node)
        label = self._ex[node.command](node)
        self.trace_list.hit(self.trace_data, node, seg_name)
        if profiler:
            profiler.hit(node, label)
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

    def init_aaa(self) -> None:
        getfc_node: KeyValue = self.seg.key_value(Line.from_line(" GETFC D1,ID=C'AA',BLOCK=YES"))
        self._ex["GETFC"](getfc_node)
        self._set_core(self.aaa_field_data, config.AAA_MACRO_NAME, self.aaa_address)
        filnc_node: KeyValue = self.seg.key_value(Line.from_line(" FLINC D1"))
        self._ex["FILNC"](filnc_node)
        return

    def init_aaa_field_data(self, test_data):
        aaa_core = next((core for core in test_data.cores if core.macro_name == config.AAA_MACRO_NAME), None)
        if aaa_core:
            self.aaa_field_data = aaa_core.field_data
        return

    def set_partition(self, partition: str) -> None:
        if partition not in config.PARTITION:
            raise PartitionError
        haalc = self._evaluate_global("@HAALC")
        ce1uid = config.ECB + get_macros()["EB0EB"].evaluate("CE1$UID")
        self.vm.set_bytes(DataType("C", input=partition).to_bytes(), haalc, 2)
        self.vm.set_value(config.PARTITION[partition], ce1uid, 1)
        # TODO Switch MH Base

    def get_partition(self) -> str:
        airline_code = self.vm.get_bytes(self._evaluate_global("@HAALC"), 2)
        return DataType("X", bytes=airline_code).decode

    def is_error(self, label: str) -> bool:
        return label in self.errors

    def index_to_label(self, field: FieldIndex) -> str:
        if field.index.reg == "R0":
            return field.name
        dsp = self.regs.get_address(field.index, field.dsp)
        label = self.seg.get_field_name(Register("R8"), dsp, config.INSTRUCTION_LEN_DEFAULT)
        if not self.seg.is_branch(label):
            raise BctExecutionError
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

    @property
    def aaa_address(self) -> int:
        ce1cr1: int = self.get_ecb_address("D1", "CE1CR")
        return self.vm.get_value(ce1cr1)

    @staticmethod
    def _field_data_to_bytearray(field_data: List[dict]):
        return {field_dict["field"]: bytearray(b64decode(field_dict["data"])) for field_dict in field_data}

    def _set_from_test_data(self, test_data: TestData) -> None:
        self.errors = set(test_data.errors)
        self.stop_segments = test_data.stop_segments
        if test_data.partition:
            self.set_partition(test_data.partition)
        for core in test_data.cores:
            if core.link_status == "inactive":
                continue
            if core.heap_name:
                address: int = self.vm.allocate()
                self.heap["old"][core.heap_name] = address
                self._set_from_core_hex_and_field_data(core, address)
            elif core.ecb_level:
                address: int = self.vm.allocate()
                self._core_block(address, core.ecb_level)
                self._set_from_core_hex_and_field_data(core, address)
            elif core.macro_name:
                macro_name = core.macro_name.upper()
                if macro_name in config.FIXED_MACROS and macro_name != config.AAA_MACRO_NAME:
                    self._set_core(core.field_data, macro_name, config.FIXED_MACROS[macro_name])
            elif core.global_name:
                address: int = self._evaluate_global(core.global_name)
                if core.is_global_record:
                    new_address: int = self.vm.allocate()
                    self.vm.set_value(new_address, address)
                    address = new_address  # initialize the field_data at the new_address
                self._set_from_core_hex_and_field_data(core, address)
        for reg, value in test_data.regs.items():
            self.regs.set_value(value, reg)
        for pnr in test_data.pnr:
            if pnr.link_status == "inactive":
                continue
            pnr_locator = pnr.locator if pnr.locator else config.AAAPNR
            if pnr.text:
                for pnr_text in pnr.text:
                    Pnr.add_from_data(pnr_text, pnr.key, pnr_locator)
            elif pnr.field_data_item:
                pnr.field_data_item.sort(key=lambda item: item["item_number"])
                for _, field_group in groupby(pnr.field_data_item, key=lambda item: item["item_number"]):
                    pnr_field_bytes: dict = self._field_data_to_bytearray(list(field_group))
                    Pnr.add_from_byte_array(pnr_field_bytes, pnr.key, pnr_locator)
        for lrec in test_data.tpfdf:
            if lrec.macro_name not in get_macros():
                raise TpfdfError
            lrec_data = self._field_data_to_bytearray(lrec.field_data)
            Tpfdf.add(lrec_data, lrec.key, lrec.macro_name)
        self._capture_file(test_data)
        return

    def _set_from_core_hex_and_field_data(self, core: Core, address: int):
        if core.hex_data:
            byte_array: bytearray = bytearray(b64decode(core.hex_data))
            self.vm.set_bytes(byte_array, address, len(byte_array))
        elif core.field_data:
            field_byte_array: Dict[str, bytearray] = self._field_data_to_bytearray(core.field_data)
            seg = get_seg_collection().get_seg(core.seg_name.upper())
            seg.assemble()
            for field, byte_array in field_byte_array.items():
                address_to_update = seg.evaluate(field.upper()) + address
                self.vm.set_bytes(byte_array, address_to_update, len(byte_array))
        return

    def _capture_file(self, test_data: TestData):
        macros = get_macros()
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
                pool_address = FlatFile.add_pool(data_bytes)
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
                    pool_address = FlatFile.add_pool(data_bytes)
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
            FlatFile.add_fixed(data_bytes, fixed_file.fixed_type, fixed_file.fixed_ordinal)
            # TODO multiple level indexes to be coded later when scenario is with us
        return

    def _set_core(self, field_data: List[dict], macro_name: str, base_address: int) -> None:
        field_byte_array: Dict[str, bytearray] = self._field_data_to_bytearray(field_data)
        for field, byte_array in field_byte_array.items():
            address = get_macros()[macro_name].evaluate(field) + base_address
            self.vm.set_bytes(byte_array, address, len(byte_array))
        return

    def _capture_output(self, output: Output, last_node: InstructionType) -> None:
        output.messages = self.messages.copy()
        output.dumps.extend(self.dumps)
        output.last_line = last_node.label
        output.last_node = str(last_node)
        if output.debug:
            output.debug = list()
            output.traces = self.trace_list.get_traces()
        for core in output.cores:
            macro_name = core.macro_name.upper()
            if macro_name in config.FIXED_MACROS:
                base_address = self.aaa_address if macro_name == config.AAA_MACRO_NAME \
                    else config.FIXED_MACROS[macro_name]
                self._capture_core(core.field_data, macro_name, base_address)
            elif macro_name in get_macros():
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
            pnr_locator = config.AAAPNR if not pnr_output.locator else pnr_output.locator
            for field_item_len in pnr_output.field_item_len:
                field = field_item_len["field"]
                item_number = field_item_len["item_number"]
                length = field_item_len["length"]
                field_byte = dict()
                pnr_output.field_data.append(field_byte)
                field_byte["field_text"] = f"{field} #{item_number}"
                field_byte["field"] = field
                data = Pnr.get_pnr_data(pnr_locator=pnr_locator, key=key, item_number=item_number, packed=True)
                pnr_data: bytearray = data[0]
                if not pnr_data:
                    field_byte["data"] = str()
                    continue
                start: int = Pnr.get_field_dsp(field)
                end: int = start + length
                field_byte["data"] = b64encode(pnr_data[start:end]).decode()
        return

    def _capture_core(self, field_data: List[dict], macro_name: str, base_address: int) -> None:
        for field_byte in field_data:
            field: LabelReference = get_macros()[macro_name].lookup(field_byte["field"].upper())
            address = field.dsp + base_address
            length = field_byte["length"] if field_byte["length"] > 0 else field.length
            try:
                field_byte["data"] = b64encode(self.vm.get_bytes(address, length)).decode()
            except BaseAddressError:
                field_byte["data"] = str()
        return
