from typing import Optional, Tuple, Dict, List, Set

from assembly.mac0_generic import LabelReference
from assembly.mac1_implementation import DataMacroImplementation
from assembly.mac2_data_macro import macros
from config import config
from utils.data_type import Register
from utils.errors import RegisterInvalidError


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

    def root_label(self, name: Optional[str] = None) -> str:
        return '$$' + self.seg_name + '$$' if name is None else '$$' + name + '$$'

    def load_macro(self, name: str, base: Optional[str] = None, suffix: Optional[str] = None) -> None:
        macros[name].load()
        if suffix is not None:
            original_name = name
            name = name + suffix
            new_symbol_table = {label + suffix: LabelReference(label + suffix, label_ref.dsp, label_ref.length, name)
                                for label, label_ref in macros[original_name].all_labels.items()}
            self._symbol_table = {**self.all_labels, **new_symbol_table}
        elif name not in self.data_macro:
            self._symbol_table = {**self.all_labels, **macros[name].all_labels}
            self.data_macro.add(name)
        if base is not None:
            base = Register(base)
            if base.is_valid():
                self.set_using(name, base)
            else:
                raise RegisterInvalidError
        return

    def set_using(self, dsect: str, reg: Register) -> None:
        using_name = next((name for name, using_reg in self._using.items() if using_reg.reg == reg.reg), None)
        if using_name is not None:
            del self._using[using_name]
        self._using[dsect] = reg

    def get_macro_name(self, base: Register) -> Optional[str]:
        return next((name for name, reg in self._using.items() if reg.reg == base.reg), None)

    def get_base(self, macro_name: str) -> Register:
        return self._using[macro_name] if macro_name in self._using else None

    def get_field_name(self, base: Register, dsp: int, length: Optional[int]) -> Optional[str]:
        length = 1 if length is None else length
        name = self.get_macro_name(base)
        if not name:
            return None
        if name == self.seg_name or name in macros:
            indexed_data = self._index if name == self.seg_name else macros[name].indexed_data
            index_label = name + str(dsp)
            if index_label not in indexed_data:
                return None
            matches = indexed_data[index_label]
            field = min(matches, key=lambda item: abs(item[1] - length))[0]
        else:
            matches = {label: label_ref for label, label_ref in self.all_labels.items()
                       if label_ref.dsp == dsp and label_ref.name == name}
            field = min(matches, key=lambda label: abs(matches[label].length - length)) if matches else None
        return field

    def is_branch(self, label: str) -> bool:
        return self.check(label) and self.lookup(label).is_branch

    def add_label(self, label: str, dsp: int, length: int, name: str) -> LabelReference:
        label_ref = super().add_label(label, dsp, length, name)
        return label_ref
