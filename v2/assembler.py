import re
import os


class Error:
    NO_ERROR = 0
    DS_DUP_FACTOR = 'DS - Duplication factor is not a number.'
    DS_DATA_TYPE = 'DS - Invalid data type.'
    EXP_INVALID_KEY = 'Expression - Field not present in data map for no data type.'
    EXP_INVALID_KEY_L = 'Expression - Field not present in data map for length attribute.'
    EXP_INVALID_KEY_X = 'Expression - Field not present in data map for hex data type.'
    EXP_DATA_TYPE = 'Expression - Invalid data type.'
    EXP_NOT_NUMBER = 'Expression - Not a number.'
    EXP_EVAL_FAIL = 'Expression - Function eval failed.'


class Line:
    def __init__(self):
        self.label = None
        self.command = None
        self.operand = None
        self.continuation = False

    @classmethod
    def from_line(cls, data, continuing=False):
        line = cls()
        if len(data) > 71 and data[71] != ' ':
            line.continuation = True
            data = data[:71]
        words = re.findall(r"(?:[^L]'.*?'|\S)+", data)
        if data[0] == ' ':
            # The label is None since there is no label
            words.insert(0, None)
        if continuing:
            # The command is None for continued lines
            words.insert(0, None)
        line.label = words[0]
        line.command = words[1] if len(words) > 1 else None
        line.operand = words[2] if len(words) > 2 else None
        return line

    def remove_suffix(self):
        self.label = next(iter(self.label.split('&'))) if self.label is not None else None
        return self

    def __repr__(self):
        return f'{self.label}:{self.command}:{self.operand}'


class File:
    CVS_C2 = {'Ch', 'RC', 'VE', '==', '**', 'ng', '/u', '1.'}
    TRIM = {'0': 7, ' ': 1}
    COMMENT_C1 = {'*', '.'}

    @classmethod
    def open(cls, file_name):
        # Open the file
        try:
            with open(file_name, 'r', errors='replace') as file:
                lines = file.readlines()
        except FileNotFoundError:
            return list()
        # Remove the CVS header if present
        index = 0
        for line in lines:
            if line[:2] not in cls.CVS_C2:
                break
            index += 1
        lines = lines[index:] if index < len(lines) else list()
        # Remove empty lines and trailing new line character
        lines = [line.strip('\n') for line in lines if line.strip()]
        if not lines:
            return list()
        # Find the character that is added by CVS on each line
        char = ''
        if all(line[0] == lines[0][0] for line in lines if line.strip):
            char = lines[0][0]
        # Remove (TRIM) the character from each line
        if char in cls.TRIM:
            lines = [line[cls.TRIM[char]:] for line in lines]
        # Remove comments
        lines = [line for line in lines if line[0] not in cls.COMMENT_C1]
        return lines


class DsOperand:
    DATA_TYPES = {'X': 1, 'C': 1, 'H': 2, 'F': 4, 'D': 8, 'FD': 8, 'B': 1}

    def __init__(self):
        self.duplication_factor = 1
        self.data_type = ''
        self.length = 0

    def __repr__(self):
        return f'{self.duplication_factor}:{self.data_type}:{self.length}'


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
    FOLDER_NAME = '../macro'
    ACCEPTED_COMMANDS = {'DS', 'EQU', 'ORG', 'DSECT'}

    def __init__(self):
        self.data_map = dict()  # Dictionary of SymbolTable. Field name is key.
        self.files = dict()     # Dictionary of MacroFile. Marco name is key
        self.errors = list()
        for file_name in os.listdir(self.FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:] not in self.EXT:
                continue
            macro_file = MacroFile(f'{self.FOLDER_NAME}/{file_name}')
            self.files[file_name[:-4].upper()] = macro_file

    def load(self, macro):
        if macro not in self.files:
            return False
        if self.files[macro].data_mapped:
            return True
        # Get the data from line after removing CVS and empty lines.
        file_lines = File.open(self.files[macro].file_name)
        # Create a list of Line objects
        lines = list()
        prior_line = None
        main_line = None
        for data in file_lines:
            continuing = True if prior_line is not None and prior_line.continuation else False
            line = Line.from_line(data, continuing)
            if not continuing:
                lines.append(line)
                main_line = line
            else:
                main_line.operand = main_line.operand + line.operand \
                    if main_line.operand is not None else line.operand
            prior_line = line
        # Remove suffix like &CG1 from label
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
                operand, result = self.get_ds_operand(line.operand, location_counter)
                if result != Error.NO_ERROR:
                    if operand.duplication_factor == 0:
                        ds_list.append((line, location_counter))
                    else:
                        self.errors.append(f'{result} {line} {macro}')
                    continue
                length = operand.length
                total_length = operand.duplication_factor * length
                data_type_length = DsOperand.DATA_TYPES[operand.data_type]
                while location_counter % data_type_length != 0:
                    location_counter += 1
                dsp = location_counter
            elif line.command == 'EQU':
                dsp, result = self._get_value(line.operand, location_counter)
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
                dsp, result = self._get_value(line.operand, location_counter)
                if result != Error.NO_ERROR:
                    self.errors.append(f'{result} {line} {macro}')
                    continue
                location_counter = dsp
            else:
                location_counter += total_length
        # Add the saved equates which were not added in the first pass
        for line, location_counter in equate_list:
            dsp, result = self._get_value(line.operand, location_counter)
            if result != Error.NO_ERROR:
                self.errors.append(f'{result} {line} {macro}')
                continue
            symbol_table = SymbolTable(line.label, dsp, 1, macro)
            self.data_map[line.label] = symbol_table
        # Add the saved DS which were not added in the first pass
        for line, location_counter in ds_list:
            operand, result = self.get_ds_operand(line.operand, location_counter)
            if result != Error.NO_ERROR:
                self.errors.append(f'{result} {line} {macro}')
                continue
            length = operand.length
            dsp = location_counter
            symbol_table = SymbolTable(line.label, dsp, length, macro)
            self.data_map[line.label] = symbol_table
        # Indicate data is mapped for that macro
        self.files[macro].data_mapped = True

    def get_ds_operand(self, operand, location_counter):
        ds_operand = DsOperand()
        # (^\d*)    = Captures a digit at the start if present (duplication_factor)
        # ([^L]+)   = Captures all characters till L (data_type)
        # L*        = Ignores L if present
        # \(*       = Ignores ( if present
        # ([^)]*)   = Captures everything till ) if present. The length can be any expression. (length)
        # \)*       = Ignores the trailing  ) if present.
        duplication_factor, data_type, length = next(iter(re.findall(r"(^\d*)([^L]+)L*\(*([^)]*)\)*", operand)))
        if duplication_factor:
            try:
                ds_operand.duplication_factor = int(duplication_factor)
            except ValueError:
                return ds_operand, Error.DS_DUP_FACTOR
        else:
            ds_operand.duplication_factor = 1
        if data_type not in DsOperand.DATA_TYPES:
            return ds_operand, Error.DS_DATA_TYPE
        ds_operand.data_type = data_type
        if length:
            ds_operand.length, result = self._get_value(length, location_counter)
            if result != Error.NO_ERROR:
                return ds_operand, result
        else:
            ds_operand.length = DsOperand.DATA_TYPES[ds_operand.data_type]
        return ds_operand, Error.NO_ERROR

    def _get_value(self, operand, location_counter):
        if operand.isdigit():
            return int(operand), Error.NO_ERROR
        exp_list = re.split(r"([+*()-])", operand)
        exp_list = [expression for expression in exp_list if expression and expression not in '()']
        eval_list = list()
        data_type = str()
        for index, expression in enumerate(exp_list):
            if expression == '+' or expression == '-' or (expression == '*' and index % 2 == 1):
                eval_list.append(expression)
            else:
                value, data_type, result = self._evaluate(expression, location_counter)
                if result != Error.NO_ERROR:
                    return None, result
                eval_list.append(str(value))
        if len(eval_list) == 1 and data_type == 'C':
            return eval_list[0], Error.NO_ERROR
        try:
            return eval(''.join(eval_list)), Error.NO_ERROR
        except (SyntaxError, NameError, TypeError, ValueError) as _:
            return None, Error.EXP_EVAL_FAIL

    def _evaluate(self, expression, location_counter):
        if expression.isdigit():
            return int(expression), str(), Error.NO_ERROR
        if expression == '*':
            return location_counter, str(), Error.NO_ERROR
        data_type, field = next(iter(re.findall(r"^([\w&]+)\'*([^']*)", expression)))
        if not field:
            field, data_type = data_type, field
        if not data_type:
            field = next(iter(field.split('&')))
            try:
                return self.data_map[field].dsp, data_type, Error.NO_ERROR
            except KeyError:
                return field, data_type, Error.EXP_INVALID_KEY
        elif data_type == 'L':
            field = next(iter(field.split('&')))
            try:
                return self.data_map[field].length, data_type, Error.NO_ERROR
            except KeyError:
                return field, data_type, Error.EXP_INVALID_KEY_L
        elif data_type not in DsOperand.DATA_TYPES:
            return None, data_type, Error.EXP_DATA_TYPE
        elif data_type == 'X':
            try:
                return int(field, 16), data_type, Error.NO_ERROR
            except ValueError:
                return field, data_type, Error.EXP_INVALID_KEY_X
        elif data_type == 'C':
            return field, data_type, Error.NO_ERROR
        else:
            try:
                return int(field), data_type, Error.NO_ERROR
            except ValueError:
                return field, data_type, Error.EXP_NOT_NUMBER
