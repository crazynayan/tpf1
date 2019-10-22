from typing import Dict

from assembly2.mac2_data_macro import DataMacro
from execution.state import Storage


class Stream:
    @staticmethod
    def to_bytes(data: Dict[str, bytearray], data_macro: DataMacro) -> bytearray:
        vm = Storage()
        address = vm.allocate()
        for field_name, byte_array in data.items():
            dsp = data_macro.evaluate(field_name)
            vm.set_bytes(byte_array, address + dsp, len(byte_array))
        return vm.frames[vm.base_key(address)]
