import os
from typing import Dict, List, Tuple, Optional

from config import config
from p1_utils.errors import EquDataTypeHasAmpersandError, NotFoundInSymbolTableError
from p1_utils.file_line import Line, File
from p2_assembly.mac0_generic import LabelReference
from p2_assembly.mac1_implementation import DataMacroImplementation


class DataMacro(DataMacroImplementation):
    def __init__(self, name: str, filename: str = None, default_macros: Dict[str, LabelReference] = None):
        super().__init__(name)
        self.file_name: str = filename if filename else str()
        self.default_macros: Dict[str, LabelReference] = default_macros if default_macros else dict()

    def __repr__(self) -> str:
        return f"{self.name} ({len(self._symbol_table)})"

    def _second_pass(self, second_list: List[Tuple[Line, int]]):
        for line, location_counter in second_list:
            if line.command not in {"EQU", "DS"}:
                continue
            self._location_counter = location_counter
            try:
                self._command[line.command](line)
            except NotFoundInSymbolTableError:
                raise NotFoundInSymbolTableError(line)
        return

    def load(self) -> None:
        if self.all_labels:
            return
        # Load default macros
        self._symbol_table = {**self.all_labels, **self.default_macros}
        # Create a list of Line objects from file or listing
        file_lines = File(self.file_name).lines
        lines = Line.from_file(file_lines)
        # Remove suffix like &CG1 from label and only keep the accepted commands.
        lines = [line.remove_suffix() for line in lines if line.command in self._command]
        # Add the macro name in symbol table
        line = Line.from_line(f"{self.name} EQU *")
        lines.insert(0, line)
        # Create LabelReference for each label and add it to dummy macro data_map.
        second_list: List[Tuple[Line, int]] = list()
        for line in lines:
            try:
                self._command[line.command](line)
            except EquDataTypeHasAmpersandError:
                pass
            except NotFoundInSymbolTableError:
                second_list.append((line, self._location_counter))
        self._second_pass(second_list)
        return

    @property
    def loaded(self):
        return self.all_labels != dict()

    @classmethod
    def get_label_reference(cls, field_name) -> Optional[LabelReference]:
        for _, data_macro in macros.items():
            data_macro.load()
            if data_macro.check(field_name):
                return data_macro.lookup(field_name)
        return None


class _DataMacroCollection:
    MAC_EXT = {".mac", ".txt"}
    DEFAULT_MACROS = ("AASEQ", "SYSEQ", "SYSEQC", "EB0EB", "UATKW", "UXTEQ", "TRMEQ", "CUSTOM")

    def __init__(self):
        self.macros: Dict[str, DataMacro] = dict()
        self.indexed_labels: Dict[str, str] = dict()
        self.default_macros: Dict[str, LabelReference] = dict()
        # Load default macros
        default_macros_dict: Dict[str, str] = dict()
        non_default_macros_dict: Dict[str, str] = dict()
        for file_name in os.listdir(config.MAC_FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.MAC_EXT:
                continue
            macro_name = file_name[:-4].upper()
            file_name = os.path.join(config.MAC_FOLDER_NAME, file_name)
            if macro_name in self.DEFAULT_MACROS:
                default_macros_dict[macro_name] = file_name
            else:
                non_default_macros_dict[macro_name] = file_name
        # Initialize default macros in hierarchical order
        for macro_name in self.DEFAULT_MACROS:
            self.macros[macro_name] = DataMacro(name=macro_name, filename=default_macros_dict[macro_name],
                                                default_macros=self.default_macros)
            self.macros[macro_name].load()
            self.default_macros = {**self.default_macros, **self.macros[macro_name].all_labels}
        # Initialize non default macros
        for macro_name, file_name in non_default_macros_dict.items():
            self.macros[macro_name] = DataMacro(name=macro_name, filename=file_name, default_macros=self.default_macros)
        for macro_name, data_macro in self.macros.items():
            data_macro.load()
            self.indexed_labels = {**self.indexed_labels,
                                   **{label: label_ref.name for label, label_ref in data_macro.all_labels.items()}}


_collection = _DataMacroCollection()
macros = _collection.macros
indexed_macros = _collection.indexed_labels


def get_global_ref(global_name: str) -> Optional[LabelReference]:
    global_macros = ["GLOBAS", "GLOBYS", "GL0BS"]
    global_macro = next((macros[macro_name] for macro_name in global_macros if macros[macro_name].check(global_name)),
                        None)
    if not global_macro:
        return None
    return global_macro.lookup(global_name)


def get_global_address(global_name: str) -> int:
    global_ref: LabelReference = get_global_ref(global_name)
    if not global_ref:
        raise NotFoundInSymbolTableError
    address = config.DEFAULT_MACROS[global_ref.name] + global_ref.dsp
    return address
