from typing import Dict, List, Optional

from d21_backend.p1_utils.data_type import DataType
from d21_backend.p2_assembly.mac2_data_macro import DataMacro
from d21_backend.p4_execution.ex0_regs_store import Storage


class Stream:

    def __init__(self, data_macro: DataMacro):
        self.data_macro = data_macro
        self.vm = Storage()
        self.address = self.vm.allocate()
        self.base_key = self.vm.base_key(self.address)
        self.data_macro.load()

    def to_bytes(self, data: Dict[str, bytearray]) -> bytearray:
        for field_name, byte_array in data.items():
            dsp = self.data_macro.evaluate(field_name)
            self.vm.set_bytes(byte_array, self.address + dsp, len(byte_array))
        return self.vm.frames[self.base_key]

    def item_to_bytes(self, item_list: List[Dict[str, bytearray]], item: str, count: Optional[str] = None,
                      data: Optional[Dict[str, bytearray]] = None, adjust: bool = False) -> bytearray:
        if data:
            self.to_bytes(data)
        if count:
            count_ref = self.data_macro.lookup(count)
            count_bytes = DataType('F', input=str(len(item_list))).to_bytes(count_ref.length)
            self.vm.set_bytes(count_bytes, self.address + count_ref.dsp, count_ref.length)
        item_ref = self.data_macro.lookup(item)
        item_start = item_ref.dsp
        for item_dict in item_list:
            for field_name, byte_array in item_dict.items():
                dsp = self.data_macro.evaluate(field_name)
                dsp = dsp - item_ref.dsp if adjust else dsp
                self.vm.set_bytes(byte_array, self.address + dsp + item_start, len(byte_array))
            item_start += item_ref.length
        return self.vm.frames[self.base_key]
