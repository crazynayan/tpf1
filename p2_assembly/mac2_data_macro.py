import os
from typing import Dict, List, Tuple, Optional

from config import config
from p1_utils.errors import EquDataTypeHasAmpersandError, NotFoundInSymbolTableError
from p1_utils.file_line import Line, File
from p2_assembly.mac0_generic import LabelReference
from p2_assembly.mac1_implementation import DataMacroImplementation


class DataMacro(DataMacroImplementation):
    def __init__(self, name: str, file_name: str, default_macros: Dict[str, LabelReference]):
        super().__init__(name)
        self.file_name: str = file_name
        self.default_macros: Dict[str, LabelReference] = default_macros

    def __repr__(self) -> str:
        return f"{self.name} ({len(self._symbol_table)})"

    def _second_pass(self, command: str, second_list: List[Tuple[Line, int]]):
        for line, location_counter in second_list:
            if line.command != command:
                continue
            self._location_counter = location_counter
            self._command[line.command](line)
        return

    def load(self) -> None:
        if self.all_labels:
            return
        # Load default macros
        self._symbol_table = {**self.all_labels, **self.default_macros}
        # Get the data from file after removing CVS and empty lines.
        file_lines = File.open(self.file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        # Remove suffix like &CG1 from label and only keep the accepted commands.
        lines = [line.remove_suffix() for line in lines if line.command in self._command]
        # Create LabelReference for each label and add it to dummy macro data_map.
        second_list: List[Tuple[Line, int]] = list()
        for line in lines:
            try:
                self._command[line.command](line)
            except EquDataTypeHasAmpersandError:
                pass
            except NotFoundInSymbolTableError:
                second_list.append((line, self._location_counter))
        # Add the saved equates which were not added in the first pass
        self._second_pass("EQU", second_list)
        # Add the saved DS which were not added in the first pass
        self._second_pass("DS", second_list)
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
    MAC_FOLDER_NAME = os.path.join(config.ROOT_DIR, "p0_source", "macro")
    DEFAULT_MACROS = ("AASEQ", "SYSEQ", "SYSEQC", "EB0EB", "UATKW", "CUSTOM")

    def __init__(self):
        self.macros: Dict[str, DataMacro] = dict()
        self.indexed_labels: Dict[str, str] = dict()
        # Load default macros
        default_macros_dict: Dict[str, str] = dict()
        non_default_macros_dict: Dict[str, str] = dict()
        for file_name in os.listdir(self.MAC_FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.MAC_EXT:
                continue
            macro_name = file_name[:-4].upper()
            file_name = os.path.join(self.MAC_FOLDER_NAME, file_name)
            if macro_name in self.DEFAULT_MACROS:
                default_macros_dict[macro_name] = file_name
            else:
                non_default_macros_dict[macro_name] = file_name
        # Initialize default macros in hierarchical order
        default_macros: Dict[str, LabelReference] = dict()
        for macro_name in self.DEFAULT_MACROS:
            self.macros[macro_name] = DataMacro(macro_name, default_macros_dict[macro_name], default_macros)
            self.macros[macro_name].load()
            default_macros = {**default_macros, **self.macros[macro_name].all_labels}
        # Initialize non default macros
        for macro_name, file_name in non_default_macros_dict.items():
            self.macros[macro_name] = DataMacro(macro_name, file_name, default_macros)
        for macro_name, data_macro in self.macros.items():
            data_macro.load()
            self.indexed_labels = {**self.indexed_labels,
                                   **{label: label_ref.name for label, label_ref in data_macro.all_labels.items()}}


_collection = _DataMacroCollection()
macros = _collection.macros
indexed_macros = _collection.indexed_labels
