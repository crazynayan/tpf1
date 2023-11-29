from typing import Optional, Tuple, Dict, List, Set

from d21_backend.config import config
from d21_backend.p1_utils.data_type import Register
from d21_backend.p1_utils.errors import UsingInvalidError
from d21_backend.p2_assembly.mac0_generic import LabelReference
from d21_backend.p2_assembly.mac1_implementation import DataMacroImplementation, Dc
from d21_backend.p2_assembly.mac2_data_macro import get_macros


class Data:
    def __init__(self):
        self.constant: bytearray = bytearray()
        self.literal: bytearray = bytearray()

    @property
    def next_constant(self) -> int:
        return len(self.constant)

    @property
    def next_literal(self) -> int:
        return len(self.literal)

    def set_constant(self, byte_array: bytearray, dsp) -> None:
        end = len(byte_array) + dsp
        if end > self.next_constant:
            self.constant.extend(bytearray([config.ZERO] * (end - self.next_constant)))
        for index, byte in enumerate(byte_array):
            self.constant[dsp + index] = byte
        return


class SegmentGeneric(DataMacroImplementation):

    def __init__(self, name: str):
        super().__init__(name)
        self.seg_name: str = name
        self._counters: Optional[Tuple[int, int]] = None  # Tuple of location counter and max counter
        self._using: List[List[str]] = [list() for _ in range(16)]  # Each pos. indicates a reg and has a dsect name
        self._using_stack: List[list] = list()  # A stack of using list
        self.data_macro: Set[str] = set()  # Set of data macro names which are already loaded.
        self.data: Data = Data()
        self.dc_list: List[Dc] = list()
        self.literal_list: List[Dc] = list()

    def root_label(self, name: Optional[str] = None) -> str:
        return "$$" + self.seg_name + "$$" if name is None else "$$" + name + "$$"

    def load_macro(self, name: str, base: str = None, suffix: Optional[str] = None, using: bool = True) -> None:
        macros = get_macros()
        macros[name].load()
        suffix_name = name + suffix if suffix else name
        if suffix_name not in self.data_macro:
            new_symbol_table: Dict[str, LabelReference] = {
                f"{label}{suffix}": LabelReference(f"{label}{suffix}", label_ref.dsp, label_ref.length, suffix_name)
                for label, label_ref in macros[name].all_labels.items()
            } if suffix else macros[name].all_labels
            self._symbol_table = {**self.all_labels, **new_symbol_table}
            self.data_macro.add(suffix_name)
        if base and using:
            self.set_using(suffix_name, base)
        return

    def set_using(self, dsect: str, base_reg: str) -> None:
        reg = Register(base_reg)
        if not reg.is_valid():
            raise UsingInvalidError
        self._using[reg.value].append(dsect)

    def get_macro_name(self, base: Register) -> Optional[str]:
        using_reg_list = self._using[base.value]
        return using_reg_list[0] if using_reg_list else None

    def get_base(self, macro_name: str) -> Register:
        index = next((index for index, reg_using_list in enumerate(reversed(self._using))
                      if macro_name in reg_using_list), None)
        return Register.from_index(len(config.REGISTERS) - index - 1) if index is not None else Register("R0")

    def get_field_name(self, base: Register, dsp: int, length: Optional[int]) -> Optional[str]:
        length = 1 if length is None else length
        name = self.get_macro_name(base)
        if not name:
            return None
        indexed_data = self._index if name == self.seg_name else get_macros()[name].indexed_data
        index_label = name + str(dsp)
        if index_label not in indexed_data:
            return None
        matches = indexed_data[index_label]
        field = min(matches, key=lambda item: abs(item[1] - length))[0]
        return field

    def is_branch(self, label: str) -> bool:
        return self.check(label) and self.lookup(label).is_branch
