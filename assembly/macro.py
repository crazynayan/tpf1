import re
from typing import Optional, Dict, List, Tuple, Set

from assembly.directive import AssemblerDirective
from assembly.file_line import File, Line, SymbolTable
from utils.data_type import DataType, Register
from utils.errors import Error


class DataMacro:
    ACCEPTED_COMMANDS = {'DS', 'EQU', 'ORG', 'DSECT', 'DC'}

    def __init__(self, name: str, file_name: Optional[str] = None):
        self.name: str = name
        self.file_name: Optional[str] = file_name
        self.loaded: bool = False
        self.symbol_table: Dict[str, SymbolTable] = dict()
        self.errors: List[str] = list()

    def __repr__(self) -> str:
        return f"{self.name}:{self.loaded}:{len(self.symbol_table)}"

    def load(self) -> None:
        if self.loaded:
            return
        # Get the data from file after removing CVS and empty lines.
        file_lines = File.open(self.file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        # Remove suffix like &CG1 from label and only keep the accepted commands.
        lines = [line.remove_suffix() for line in lines if line.command in self.ACCEPTED_COMMANDS]
        # Create SymbolTable for each label and add it to dummy macro data_map.
        second_list = list()
        macro = SegmentMacro(name=self.name)
        for line in lines:
            result = AssemblerDirective.from_line(line, macro, self.name)
            if result != Error.NO_ERROR:
                second_list.append((line, macro.location_counter))
        # Add the saved equates which were not added in the first pass
        assembler_directive = AssemblerDirective('EQU')
        assembler_directive.second_pass(second_list, macro, self.name, self.errors)
        # Add the saved DS which were not added in the first pass
        assembler_directive = AssemblerDirective('DS')
        assembler_directive.second_pass(second_list, macro, self.name, self.errors)
        # Move the data_map into global_map
        self.symbol_table = macro.data_map
        # Indicate data is mapped for that macro
        self.loaded = True
        return


class SegmentMacro:
    FIELD_LOOKUP = '$FIELD_LOOKUP$'
    DEFAULT_MACRO_LOAD = {'EB0EB', 'AASEQ'}

    def __init__(self, program=None, name: Optional[str] = None):
        self.seg_name:  Optional[str] = name                    # Segment name for which this instance is created.
        self.global_program = program                           # Reference to the program instance.
        self.data_map: Dict[str, SymbolTable] = dict()          # Dictionary of SymbolTable. Field name is the key.
        self.dsect: Optional[Tuple[int, str]] = None            # Tuple of location counter and name of DSECT
        self.using: Dict[str, Register] = dict()                # Key is macro name and Value is Reg
        self.using_stack: List[Dict[str, Register]] = list()    # A stack of using dicts
        self.data_macro: Set[str] = set()                       # Set of data macro names which are already loaded.
        self.location_counter: int = 0                          # Used for calculating dsp (displacement)
        self.max_counter: int = 0                               # Used for ORG

    def __repr__(self):
        return f"SegmentMacro:{self.seg_name}:{len(self.data_map)}"

    def is_branch(self, label):
        return label in self.data_map and self.data_map[label].is_branch

    def is_instruction_branch(self, label):
        return label in self.data_map and self.data_map[label].is_instruction_branch

    def is_present(self, macro_name):
        return self.global_program.is_macro_present(macro_name)

    def copy_default_from_global(self):
        for macro_name in self.DEFAULT_MACRO_LOAD:
            self.load(macro_name)

    def load(self, macro_name, base=None, suffix=None):
        self.global_program.macros[macro_name].load()
        if suffix is not None:
            original_name = macro_name
            macro_name = macro_name + suffix
            new_symbol_table = {label + suffix: SymbolTable(label + suffix, entry.dsp, entry.length, macro_name)
                                for label, entry in self.global_program.macros[original_name].symbol_table.items()}
            self.data_map = {**self.data_map, **new_symbol_table}
        elif macro_name not in self.data_macro:
            self.data_map = {**self.data_map, **self.global_program.macros[macro_name].symbol_table}
            self.data_macro.add(macro_name)
        if base is not None:
            if Register(base).is_valid():
                self.set_using(macro_name, base)
            else:
                raise TypeError

    def get_value(self, operand: str) -> Tuple[Optional[int], str]:
        if operand.isdigit():
            return int(operand), Error.NO_ERROR
        data_list = re.findall(r"[CXHFDBZPAY]D?'[^']+'", operand)
        value_list = list()
        if data_list:
            operand = re.sub(r"[CXHFDBZPAY]D?'[^']+'", "~", operand)
            for data in data_list:
                value = DataType(data[0], input=data[2:-1]).value
                value_list.insert(0, value)
        exp_list = re.split(r"([+*()-])", operand)
        if len(exp_list) == 1 and data_list:
            return value_list.pop(), Error.NO_ERROR
        exp_list = [expression for expression in exp_list if expression and expression not in '()']
        eval_list = list()
        for index, expression in enumerate(exp_list):
            if expression == '+' or expression == '-' or (expression == '*' and index % 2 == 1):
                eval_list.append(expression)
            else:
                if expression == "~":
                    value = value_list.pop()
                elif expression == '*':
                    value = self.location_counter
                else:
                    value, result = self.evaluate(expression)
                    if result != Error.NO_ERROR:
                        return None, result
                eval_list.append(str(value))
        return eval(''.join(eval_list)), Error.NO_ERROR

    def lookup(self, field: str) -> Tuple[SymbolTable, str]:
        field = next(iter(field.split('&')))
        try:
            return self.data_map[field], Error.NO_ERROR
        except KeyError:
            return SymbolTable(), Error.EXP_INVALID_KEY

    def evaluate(self, expression):
        if expression.isdigit():
            return int(expression), Error.NO_ERROR
        if expression.startswith("L'"):
            field, result = self.lookup(expression[2:])
            value = field.length
        else:
            field, result = self.lookup(expression)
            value = field.dsp
        return value, result

    def set_using(self, dsect, reg):
        using_name = next((name for name, using_reg in self.using.items() if using_reg == reg), None)
        if using_name is not None:
            del self.using[using_name]
        self.using[dsect] = reg

    def get_macro_name(self, base):
        # Will raise a StopIteration exception if the base register is not present.
        return next(name for name, reg in self.using.items() if reg == base.reg)

    def get_base(self, macro_name):
        try:
            return self.using[macro_name]
        except KeyError:
            raise KeyError

    def get_field_name(self, base, dsp, length):
        try:
            macro_name = self.get_macro_name(base)
            matches = {label: symbol_table for label, symbol_table in self.data_map.items()
                       if symbol_table.dsp == dsp and symbol_table.name == macro_name}
            return min(matches, key=lambda label: abs(matches[label].length - length))
        except (StopIteration, ValueError):
            return None
