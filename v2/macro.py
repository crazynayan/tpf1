import re
import os

from config import config
from v2.errors import Error
from v2.file_line import File, Line
from v2.data_type import DataType


class DsDc:
    def __init__(self):
        self.duplication_factor = 1
        self.length = 0
        self.data_type = None
        self.data = None
        self.align_to_boundary = True

    @classmethod
    def from_operand(cls, operand, macro, location_counter=None):
        dsdc = cls()
        operands = next(iter(re.findall(
            r"(^\d*)([CXHFDBZPAY]D?)(?:L(?:\(([^)]*)\))?(?:([\d]+))?)?(['(])?([^')]*)[')]?", operand)))
        # Duplication Factor
        dsdc.duplication_factor = int(operands[0]) if operands[0] else 1
        # Data Type
        dsdc.data_type = operands[1]
        if dsdc.data_type not in DataType.DATA_TYPES:
            raise TypeError
        # Data
        length = None
        if operands[4] == "'":
            data_type_object = DataType(dsdc.data_type, input=operands[5])
            dsdc.data = data_type_object.to_bytes()
            length = data_type_object.length
        elif operands[4] == "(":
            number, result = macro.get_value(operands[5], location_counter)
            if result != Error.NO_ERROR:
                return dsdc, result
            dsdc.data = DataType(dsdc.data_type, input=str(number)).to_bytes()
        else:
            dsdc.data = None
        # Length
        if not operands[2] and not operands[3]:
            dsdc.length = DataType.DATA_TYPES[dsdc.data_type] if length is None else length
        elif operands[2]:
            dsdc.length, result = macro.get_value(operands[2], location_counter)
            dsdc.align_to_boundary = False
            if result != Error.NO_ERROR:
                return dsdc, result
        else:
            dsdc.length = int(operands[3])
            dsdc.align_to_boundary = False
        return dsdc, Error.NO_ERROR

    def __repr__(self):
        return f'{self.duplication_factor}:{self.data_type}:{self.length}:{self.data}'


class SymbolTable:
    def __init__(self, label, dsp, length, macro):
        self.label = label
        self.dsp = dsp
        self.length = length
        self.macro = macro

    def __repr__(self):
        return f'{self.label}:{self.dsp}:{self.length}:{self.macro}'


class MacroFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.data_mapped = False
        self.base = None

    def __repr__(self):
        return f'{self.file_name}:{self.data_mapped}:{self.base}'


class Macro:
    EXT = {'.mac', '.txt'}
    FOLDER_NAME = os.path.join(config.ROOT_DIR, 'macro')
    ACCEPTED_COMMANDS = {'DS', 'EQU', 'ORG', 'DSECT'}
    FIELD_LOOKUP = '$FIELD_LOOKUP$'
    INTEGER = '$INTEGER$'

    def __init__(self):
        self.data_map = dict()  # Dictionary of SymbolTable. Field name is the key.
        self.files = dict()     # Dictionary of MacroFile. Marco name is the key.
        self.base = dict()      # Dictionary of macro names. Base is the key.
        self.errors = list()
        for file_name in os.listdir(self.FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:] not in self.EXT:
                continue
            macro_file = MacroFile(os.path.join(self.FOLDER_NAME, file_name))
            self.files[file_name[:-4].upper()] = macro_file

    def load(self, macro, base=None):
        if macro not in self.files:
            return False
        if self.files[macro].data_mapped:
            return True
        # Get the data from line after removing CVS and empty lines.
        file_lines = File.open(self.files[macro].file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        # Remove suffix like &CG1 from label and only keep the accepted commands.
        lines = [line.remove_suffix() for line in lines if line.command in self.ACCEPTED_COMMANDS]
        # Create SymbolTable for each label and add it to data_map.
        equate_list = list()
        ds_list = list()
        location_counter = 0
        for line in lines:
            total_length = 0
            length = 1
            dsp = -1
            if line.command == 'DS':
                ds, result = DsDc.from_operand(line.operand, self, location_counter)
                if result != Error.NO_ERROR:
                    if ds.duplication_factor == 0:
                        ds_list.append((line, location_counter))
                    else:
                        self.errors.append(f'{result} {line} {macro}')
                    continue
                length = ds.length
                total_length = ds.duplication_factor * length
                while location_counter % DataType.DATA_TYPES[ds.data_type] != 0 and ds.align_to_boundary:
                    location_counter += 1
                dsp = location_counter
            elif line.command == 'EQU':
                dsp, result = self.get_value(line.operand, location_counter)
                if result != Error.NO_ERROR:
                    equate_list.append((line, location_counter))
                    continue
            elif line.command == 'DSECT':
                dsp = 0
                length = 0
            if line.label:
                symbol_table = SymbolTable(line.label, dsp, length, macro)
                self.data_map[line.label] = symbol_table
            if line.command == 'ORG':
                dsp, result = self.get_value(line.operand, location_counter)
                if result != Error.NO_ERROR:
                    self.errors.append(f'{result} {line} {macro}')
                    continue
                location_counter = dsp
            else:
                location_counter += total_length
        # Add the saved equates which were not added in the first pass
        for line, location_counter in equate_list:
            dsp, result = self.get_value(line.operand, location_counter)
            if result != Error.NO_ERROR:
                self.errors.append(f'{result} {line} {macro}')
                continue
            symbol_table = SymbolTable(line.label, dsp, 1, macro)
            self.data_map[line.label] = symbol_table
        # Add the saved DS which were not added in the first pass
        for line, location_counter in ds_list:
            ds, result = DsDc.from_operand(line.operand, self, location_counter)
            if result != Error.NO_ERROR:
                self.errors.append(f'{result} {line} {macro}')
                continue
            length = ds.length
            dsp = location_counter
            symbol_table = SymbolTable(line.label, dsp, length, macro)
            self.data_map[line.label] = symbol_table
        # Indicate data is mapped for that macro
        self.files[macro].data_mapped = True
        if base is not None and base.is_valid():
            self.files[macro].base = base
            self.base[str(base)] = macro
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

    def evaluate(self, expression, location_counter=-1):
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

    @staticmethod
    def is_location_counter_changed(line):
        if line.command == 'EQU' and line.operand == '*':
            return False
        if line.command == 'DS' and line.operand[0] == '0':
            return False
        return True

    def get_field_name(self, base, dsp, length):
        try:
            macro_name = self.base[base.reg]
            matches = {label: symbol_table for label, symbol_table in self.data_map.items()
                       if symbol_table.dsp == dsp and symbol_table.macro == macro_name}
            return min(matches, key=lambda label: abs(matches[label].length - length))
        except (KeyError, ValueError):
            return None
