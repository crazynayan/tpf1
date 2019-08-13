import re
import os
import v2.instruction as ins

from config import config
from v2.errors import Error
from v2.file_line import File, Line
from v2.data_type import DataType, Register


class MacroFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.data_mapped = False

    def __repr__(self):
        return f'{self.file_name}:{self.data_mapped}'


class Macro:
    EXT = {'.mac', '.txt'}
    FOLDER_NAME = os.path.join(config.ROOT_DIR, 'macro')
    ACCEPTED_COMMANDS = {'DS', 'EQU', 'ORG', 'DSECT', 'DC'}
    FIELD_LOOKUP = '$FIELD_LOOKUP$'
    INTEGER = '$INTEGER$'

    def __init__(self):
        self.data_map = dict()  # Dictionary of SymbolTable. Field name is the key.
        self.files = dict()     # Dictionary of MacroFile. Marco name is the key.
        self.errors = list()
        self.dsect = None
        for file_name in os.listdir(self.FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:] not in self.EXT:
                continue
            macro_file = MacroFile(os.path.join(self.FOLDER_NAME, file_name))
            self.files[file_name[:-4].upper()] = macro_file
        self.using = dict()

    def load(self, macro_name, base=None):
        if macro_name not in self.files:
            return False
        if self.files[macro_name].data_mapped:
            return True
        # Get the data from line after removing CVS and empty lines.
        file_lines = File.open(self.files[macro_name].file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        # Remove suffix like &CG1 from label and only keep the accepted commands.
        lines = [line.remove_suffix() for line in lines if line.command in self.ACCEPTED_COMMANDS]
        # Create SymbolTable for each label and add it to data_map.
        second_list = list()
        location_counter = 0
        for line in lines:
            if line.is_second_pass:
                continue
            instruction_class = line.instruction_class
            location_counter, result = eval(
                f"ins.{instruction_class}.update(line, self, {location_counter}, macro_name)")
            if result != Error.NO_ERROR:
                second_list.append((line, location_counter))
        # Add the saved equates which were not added in the first pass
        ins.Equ.update_from_lines(second_list, self, macro_name, self.errors)
        # Add the saved DS which were not added in the first pass
        ins.Ds.update_from_lines(second_list, self, macro_name, self.errors)
        # Indicate data is mapped for that macro
        self.files[macro_name].data_mapped = True
        if base is not None and Register(base).is_valid():
            self.using[base] = macro_name
        return True

    def get_value(self, operand, location_counter=None):
        if operand.isdigit():
            return int(operand), Error.NO_ERROR
        exp_list = re.split(r"([+*()-])", operand)
        exp_list = [expression for expression in exp_list if expression and expression not in '()']
        eval_list = list()
        for index, expression in enumerate(exp_list):
            if expression == '+' or expression == '-' or (expression == '*' and index % 2 == 1):
                eval_list.append(expression)
            else:
                value, data_type, result = self.evaluate(expression, location_counter)
                if result != Error.NO_ERROR:
                    return None, result
                eval_list.append(str(value))
        try:
            return eval(''.join(eval_list)), Error.NO_ERROR
        except (SyntaxError, NameError, TypeError, ValueError):
            return None, Error.EXP_EVAL_FAIL

    def evaluate(self, expression, location_counter=None):
        if expression.isdigit():
            return int(expression), self.INTEGER, Error.NO_ERROR
        if expression == '*':
            return location_counter, str(), Error.NO_ERROR
        try:
            data_type, field = next(iter(re.findall(r"^([\w&#$]+)'*([^']*)", expression)))
        except StopIteration:
            return str(), str(), Error.EXP_REGEX
        if not field:
            field, data_type = data_type, field
        if not data_type:
            field = next(iter(field.split('&')))
            try:
                return self.data_map[field].dsp, self.FIELD_LOOKUP, Error.NO_ERROR
            except KeyError:
                return field, data_type, Error.EXP_INVALID_KEY
        if data_type == 'L':
            field = next(iter(field.split('&')))
            try:
                return self.data_map[field].length, data_type, Error.NO_ERROR
            except KeyError:
                return field, data_type, Error.EXP_INVALID_KEY_L
        if '&' in field:
            return field, data_type, Error.EXP_INVALID_KEY_X
        return DataType(data_type, input=field).value, data_type, Error.NO_ERROR

    def get_macro_name(self, base):
        # Will raise a KeyError exception if the base register is not present.
        return self.using[base.reg]

    def get_base(self, macro_name):
        # Will raise a StopIteration exception if the macro_name is not present.
        return next(reg for reg, name in self.using.items() if name == macro_name)

    def get_field_name(self, base, dsp, length):
        try:
            macro_name = self.get_macro_name(base)
            matches = {label: symbol_table for label, symbol_table in self.data_map.items()
                       if symbol_table.dsp == dsp and symbol_table.name == macro_name}
            return min(matches, key=lambda label: abs(matches[label].length - length))
        except (KeyError, ValueError):
            return None
