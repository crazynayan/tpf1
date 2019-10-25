import os
from typing import Dict, List, Tuple, Set

from assembly.mac0_generic import LabelReference
from assembly.mac1_implementation import DataMacroImplementation
from config import config
from utils.errors import EquDataTypeHasAmpersandError, NotFoundInSymbolTableError
from utils.file_line import Line, File


class DataMacro(DataMacroImplementation):
    def __init__(self, name: str, file_name: str, default_macros: Dict[str, LabelReference]):
        super().__init__(name)
        self.file_name: str = file_name
        self.default_macros: Dict[str, LabelReference] = default_macros

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
        self._second_pass('EQU', second_list)
        # Add the saved DS which were not added in the first pass
        self._second_pass('DS', second_list)
        return

    @property
    def loaded(self):
        return self.all_labels != dict()


class _DataMacroCollection:
    MAC_EXT = {'.mac', '.txt'}
    MAC_FOLDER_NAME = os.path.join(config.ROOT_DIR, 'macro')
    DEFAULT_MACROS = {'AASEQ', 'SYSEQ', 'SYSEQC'}

    def __init__(self):
        self.macros: Dict[str, DataMacro] = dict()
        # Load default macros
        default_macros: Dict[str, LabelReference] = dict()
        non_default_macros: Set[Tuple[str, str]] = set()
        for file_name in os.listdir(self.MAC_FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.MAC_EXT:
                continue
            macro_name = file_name[:-4].upper()
            file_name = os.path.join(self.MAC_FOLDER_NAME, file_name)
            if macro_name not in self.DEFAULT_MACROS:
                non_default_macros.add((macro_name, file_name))
                continue
            self.macros[macro_name] = DataMacro(macro_name, file_name, dict())
            self.macros[macro_name].load()
            default_macros = {**default_macros, **self.macros[macro_name].all_labels}
        # Initialize non default macros
        for macro_name, file_name in non_default_macros:
            self.macros[macro_name] = DataMacro(macro_name, file_name, default_macros)
        self.macros['EB0EB'].load()
        self.macros['GLOBAL'].load()
        self.macros['WA0AA'].load()
        self.macros['MI0MI'].load()


macros = _DataMacroCollection().macros
