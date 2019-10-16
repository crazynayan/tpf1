import os
import re
from typing import Dict, Optional, List, Tuple, Set

from assembly.file_line import LabelReference, Line, File
from config import config
from utils.data_type import DataType
from utils.errors import NotFoundInSymbolTableError, EquLabelRequiredError, EquDataTypeHasAmpersandError


class Dsdc:

    def __init__(self, duplication_factor: int, data_type: str, length: int, start: int,
                 data: Optional[bytearray] = None):
        self.duplication_factor: int = duplication_factor
        self.data_type: str = data_type
        self.length: int = length
        self.start: int = start
        self.data: Optional[bytearray] = data


class MacroGeneric:

    def __init__(self, name):
        self.name = name
        self._symbol_table: Dict[str, LabelReference] = dict()
        self._directives: Dict[str, callable] = dict()
        self._location_counter: int = 0
        self._max_counter: int = 0

    def check(self, label: str) -> bool:
        return label in self._symbol_table

    def lookup(self, label: str) -> LabelReference:
        field = next(iter(label.split('&')))
        try:
            return self._symbol_table[field]
        except KeyError:
            raise NotFoundInSymbolTableError

    def evaluate(self, expression: str) -> int:
        if expression.isdigit():
            return int(expression)
        if expression.startswith("L'"):
            value = self.lookup(expression[2:]).length
        else:
            value = self.lookup(expression).dsp
        return value

    def get_value(self, operand: str) -> int:
        if operand.isdigit():
            return int(operand)
        data_list = re.findall(r"[CXHFDBZPAY]D?'[^']+'", operand)
        value_list = list()
        if data_list:
            operand = re.sub(r"[CXHFDBZPAY]D?'[^']+'", '~', operand)
            for data in data_list:
                value = DataType(data[0], input=data[2:-1]).value
                value_list.insert(0, value)
        exp_list = re.split(r"([+*()-])", operand)
        if len(exp_list) == 1 and data_list:
            return value_list.pop()
        exp_list = [expression for expression in exp_list if expression and expression not in '()']
        eval_list = list()
        for index, expression in enumerate(exp_list):
            if expression == '+' or expression == '-' or (expression == '*' and index % 2 == 1):
                eval_list.append(expression)
            else:
                if expression == '~':
                    value = value_list.pop()
                elif expression == '*':
                    value = self._location_counter
                else:
                    value = self.evaluate(expression)
                eval_list.append(str(value))
        return eval(''.join(eval_list))

    def _dsdc(self, operand: str) -> Dsdc:
        # (^\d*)([CXHFDBZPAY]D?)(?:L([\d]+))?(?:L[(]([^)]+)[)])?(?:[']([^']+)['])?(?:[(]([^)]+)[)])?
        operands = next(iter(re.findall(
            r"(^\d*)"  # 0 Duplication Factor - A number. (Optional)
            r"([CXHFDBZPAY]D?)"  # 1 Data Type - Valid Single character Data type. (Note: FD is valid)
            r"(?:L([\d]+))?"  # 2 Length - L followed by a number. (Optional)
            r"(?:L[(]([^)]*)[)])?"  # 3 Length - L followed by a expression enclosed in paranthesis. (Optional)
            r"(?:[']([^']*)['])?"  # 4 Data - Enclosed in quotes. (Optional)
            r"(?:[(]([^)]*)[)])?",  # 5 Data - Enclosed in parenthesis. (Optional)
            operand)))
        # Duplication Factor
        duplication_factor = int(operands[0]) if operands[0] else 1
        # Data Type
        data_type = operands[1]
        # Align to boundary
        align_to_boundary = 0
        boundary = DataType(data_type).align_to_boundary
        if boundary > 0 and self._location_counter % boundary > 0:
            align_to_boundary = boundary - self._location_counter % boundary
        # Length
        if operands[2]:
            length = int(operands[2])
            align_to_boundary = 0
        elif operands[3]:
            length = self.get_value(operands[3])
            align_to_boundary = 0
        else:
            length = None
        # Data
        if operands[4]:
            data_type_object = DataType(data_type, input=operands[4])
            length = length or data_type_object.length
            data = data_type_object.to_bytes(length)
        elif operands[5]:
            data = bytearray()
            for operand in operands[5].split(','):
                number = self.get_value(operand)
                data_type_object = DataType(data_type, input=str(number))
                length = length or data_type_object.default_length
                data.extend(data_type_object.to_bytes(length))
        else:
            data = None
            length = length or DataType(data_type).default_length
        # Start (after boundary alignment) and End (After duplication factor)
        start = self._location_counter + align_to_boundary
        self._location_counter = start + duplication_factor * length
        if self._location_counter > self._max_counter:
            self._max_counter = self._location_counter
        dsdc = Dsdc(duplication_factor, data_type, length, start, data)
        return dsdc


class DataMacroImplementation(MacroGeneric):

    def __init__(self, name):
        super().__init__(name)
        self._directives['DS'] = self.ds
        self._directives['EQU'] = self.equ
        self._directives['ORG'] = self.org
        self._directives['DSECT'] = self.dsect

    def ds(self, line: Line) -> None:
        operands = line.split_operands()
        dsdc = self._dsdc(operands[0])
        if line.label:
            self._symbol_table[line.label] = LabelReference(line.label, dsdc.start, dsdc.length, self.name)
        if len(operands) > 1:
            for operand in operands[1:]:
                self._dsdc(operand)  # Increment location counter for multiple values
        return

    def equ(self, line: Line) -> None:
        if line.label is None:
            raise EquLabelRequiredError
        operands = line.split_operands()
        dsp_operand = operands[0]
        length = 1
        if dsp_operand == '*':
            dsp = self._location_counter
        elif not set("+-*").intersection(dsp_operand):
            if dsp_operand.isdigit():
                dsp = int(dsp_operand)
            elif re.match(r"^[CXHFDBZPAY]'[^']+'$", dsp_operand) is not None:
                if '&' in dsp_operand:
                    raise EquDataTypeHasAmpersandError
                dsp = DataType(dsp_operand[0], input=dsp_operand[2:-1]).value
            else:
                if dsp_operand[0] == '&':
                    raise EquDataTypeHasAmpersandError
                field = self.lookup(dsp_operand)
                dsp = field.dsp
                length = field.length
        else:
            dsp = self.get_value(dsp_operand)
        if len(operands) > 1:
            length = self.get_value(operands[1])
        self._symbol_table[line.label] = LabelReference(line.label, dsp, length, self.name)
        return

    def org(self, line: Line) -> None:
        if line.operand is None:
            self._location_counter = self._max_counter
        else:
            self._location_counter = self.get_value(line.operand)
        return

    def dsect(self, line: Line) -> None:
        self._location_counter = 0
        self._max_counter = 0
        self._symbol_table[line.label] = LabelReference(line.label, 0, 0, line.label)
        return


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
            self._directives[line.command](line)
        return

    @property
    def all_labels(self) -> Dict[str, LabelReference]:
        return self._symbol_table

    def load(self) -> None:
        if self._symbol_table:
            return
        # Load default macros
        self._symbol_table = {**self._symbol_table, **self.default_macros}
        # Get the data from file after removing CVS and empty lines.
        file_lines = File.open(self.file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        # Remove suffix like &CG1 from label and only keep the accepted commands.
        lines = [line.remove_suffix() for line in lines if line.command in self._directives]
        # Create LabelReference for each label and add it to dummy macro data_map.
        second_list: List[Tuple[Line, int]] = list()
        for line in lines:
            try:
                self._directives[line.command](line)
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
        return self._symbol_table != dict()


class _Assembly:
    ASM_EXT = {'.asm', '.txt'}
    ASM_FOLDER_NAME = os.path.join(config.ROOT_DIR, 'asm')
    MAC_EXT = {'.mac', '.txt'}
    MAC_FOLDER_NAME = os.path.join(config.ROOT_DIR, 'macro')
    DEFAULT_MACROS = {'AASEQ', 'SYSEQ', 'SYSEQC'}

    def __init__(self):
        # MACRO PROCESSION
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

    def is_macro_present(self, macro_name):
        return macro_name in self.macros


assembly = _Assembly()
