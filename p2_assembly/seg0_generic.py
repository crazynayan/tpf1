from typing import Optional, Tuple, Dict, List, Set

from config import config
from p1_utils.data_type import Register
from p1_utils.errors import UsingInvalidError
from p2_assembly.mac0_generic import LabelReference
from p2_assembly.mac1_implementation import DataMacroImplementation, Dc
from p2_assembly.mac2_data_macro import macros


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
        self._using: Dict[str, Register] = dict()  # Key is macro name and Value is Reg
        self._using_stack: List[Dict[str, Register]] = list()  # A stack of using dicts
        self.data_macro: Set[str] = set()  # Set of data macro names which are already loaded.
        self.data: Data = Data()
        self.dc_list: List[Dc] = list()
        self.literal_list: List[Dc] = list()

    def root_label(self, name: Optional[str] = None) -> str:
        return "$$" + self.seg_name + "$$" if name is None else "$$" + name + "$$"

    def load_macro(self, name: str, base: str = None, suffix: Optional[str] = None, override: bool = True) -> None:
        macros[name].load()
        suffix_name = name + suffix if suffix else name
        if suffix_name not in self.data_macro:
            new_symbol_table: Dict[str, LabelReference] = {
                f"{label}{suffix}": LabelReference(f"{label}{suffix}", label_ref.dsp, label_ref.length, suffix_name)
                for label, label_ref in macros[name].all_labels.items()
            } if suffix else macros[name].all_labels
            self._symbol_table = {**self.all_labels, **new_symbol_table}
            self.data_macro.add(suffix_name)
        if base:
            self.set_using(suffix_name, base, override)
        return

    def set_using(self, dsect: str, base_reg: str, override: bool = True) -> None:
        reg = Register(base_reg)
        if not reg.is_valid():
            raise UsingInvalidError
        using_name = next((name for name, using_reg in self._using.items() if using_reg.reg == reg.reg), None)
        if reg.reg == "R8" and using_name is not None:  # Do not set R8 (to fix issue of listing using overriding)
            return
        if override and using_name is not None:
            del self._using[using_name]
        self._using[dsect] = reg

    def get_macro_name(self, base: Register) -> Optional[str]:
        return next((name for name, reg in self._using.items() if reg.reg == base.reg), None)

    def get_base(self, macro_name: str) -> Register:
        return self._using[macro_name] if macro_name in self._using else Register("R0")

    def get_field_name(self, base: Register, dsp: int, length: Optional[int]) -> Optional[str]:
        length = 1 if length is None else length
        name = self.get_macro_name(base)
        if not name:
            return None
        indexed_data = self._index if name == self.seg_name else macros[name].indexed_data
        index_label = name + str(dsp)
        if index_label not in indexed_data:
            return None
        matches = indexed_data[index_label]
        field = min(matches, key=lambda item: abs(item[1] - length))[0]
        return field

    def is_branch(self, label: str) -> bool:
        return self.check(label) and self.lookup(label).is_branch
