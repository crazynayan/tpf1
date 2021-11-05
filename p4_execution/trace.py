from copy import copy
from typing import List

from config import config
from p2_assembly.seg3_ins_type import InstructionType


class TraceData:
    def __init__(self):
        self.read1: str = str()
        self.read2: str = str()
        self.reg_pointer: str = str()

    def set_signed_value1(self, value: int):
        self.read1 = f"{value & config.REG_MAX:08X}"

    def set_signed_value2(self, value: int):
        self.read2 = f"{value & config.REG_MAX:08X}"

    def set_unsigned_value1(self, value: int, length: int):
        self.read1 = f"{value:0{length * 2}X}"

    def set_unsigned_value2(self, value: int, length: int):
        self.read2 = f"{value:0{length * 2}X}"

    def set_reg_pointer(self, value: int):
        self.reg_pointer = f"{value & config.REG_MAX:08X}"

    def set_byte_array1(self, byte_array: bytearray):
        self.read1 = byte_array.hex().upper()


class TraceItem:
    def __init__(self, trace_data: TraceData, node: InstructionType, seg_name: str):
        self.data: TraceData = trace_data
        self.instruction: str = str(node)[7:]
        self.seg_name: str = seg_name


class TraceList:
    def __init__(self):
        self.trace_items: List[TraceItem] = list()
        self.seg_list: List[str] = list()

    def hit(self, trace_data, node: InstructionType, seg_name: str):
        if seg_name in self.seg_list:
            self.trace_items.append(TraceItem(copy(trace_data), node, seg_name))
        return

    def get_traces(self) -> List[dict]:
        return [{"seg_name": trace.seg_name, "instruction": trace.instruction, "read1": trace.data.read1,
                 "read2": trace.data.read2, "reg_pointer": trace.data.reg_pointer} for trace in self.trace_items]
