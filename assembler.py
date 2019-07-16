from os import path
from models import Component, Node
from commands import cmd


class AssemblerLine:
    EXCLUDE_C1 = {'*'}
    EXCLUDE_C5 = {'Check', 'RCS: ', 'VERS:', '=====', '*****'}
    TRIM = {'0': 7}
    TRUE_LABELS = {'DS': '0H', 'EQU': '*'}
    FALSE_LABELS = {'DS', 'DC', 'EQU', 'DSECT', 'CSECT'}

    def __init__(self, line):
        self.line = line.strip()
        self.label = None
        self.command = None
        self.operands = list()
        self.continuation = False
        self.continuing = False

    def __repr__(self):
        return f'{self.command} {self.operands}'

    def _parse_line(self):
        """
        Call from sanitize line to initialize fields in AssemblerLine
        :return: None
        """
        line = self.line
        # Convert spaces within quotes to ;
        if line.count("'") == 2:
            start = line.index("'")
            data = line[start: line[start + 1:].index("'") + start + 2]
            new_data = data.replace(' ', ';')
            line = line.replace(data, new_data)
        words = line.split()
        if self.line[0] == ' ':
            label = None
            if not self.continuing:
                self.command = words[0].strip() if len(words) > 0 else None
                operands = words[1].strip() if len(words) > 1 else None
            else:
                operands = words[0].strip() if len(words) > 0 else None
        else:
            label = words[0].strip() if len(words) > 0 else None
            self.command = words[1].strip() if len(words) > 1 else None
            operands = words[2].strip() if len(words) > 2 else None
        # Set Label
        if label:
            if self.command in self.TRUE_LABELS and operands in self.TRUE_LABELS[self.command]:
                self.label = label
            if not self.label and self.command not in self.FALSE_LABELS:
                self.label = label
        # Set Operands
        if operands:
            # Convert (2,R4) to (2;R4)
            conversion = False
            converted = list()
            for char in operands:
                if char == '(':
                    conversion = True
                elif char == ')':
                    conversion = False
                if conversion and char == ',':
                    converted.append(';')
                else:
                    converted.append(char)
            operands = ''.join(converted)
            self.operands = operands.split(',')
        # Set Continuation
        if len(self.line) > 71 and self.line[71] != ' ':
            self.continuation = True

    def sanitize(self):
        """
        Remove comments and cvs version related line.
        :return: line of valid assembler code else None.
        """
        if len(self.line) < 5:
            return None
        if self.line[:5] in self.EXCLUDE_C5:
            return None
        if self.line[0] in self.TRIM:
            self.line = self.line[self.TRIM[self.line[0]]:]
            if not self.line:
                return None
        if self.line[0] in self.EXCLUDE_C1:
            return None
        self._parse_line()
        return self


class AssemblerProgram:
    EXT = {'.asm', '.txt'}

    def __init__(self, name):
        self.name = name
        self.root_label = '$$' + name + '$$'
        self.file_name = None
        self.lines = list()
        self.labels = list()
        self.blocks = dict()
        self.paths = list()
        self.nodes = dict()

    def set_file_name(self, file_path=None):
        """
        Sets the file_name of the source assembler file by verifying whether such file exists.
        :param file_path: A path to the assembler file name.
        :return: True if file_name set and it exists else False
        """
        if file_path:
            if path.isfile(file_path):
                self.file_name = file_path
                return True
            if file_path[-1] != '/':
                file_path += '/'
            for ext in self.EXT:
                file_name = file_path + ext
                if path.isfile(file_name):
                    self.file_name = file_name
                    return True
        for ext in self.EXT:
            file_name = self.name + ext
            if path.isfile(file_name):
                self.file_name = file_name
                return True
        return False

    def read_file(self):
        """
        Read the file and initialize assembler lines
        :return: True if assembler lines initialize else false
        """
        if self.lines:
            return False
        if not self.file_name and not self.set_file_name():
            return False
        try:
            with open(self.file_name, 'r', errors='replace') as file:
                lines = file.readlines()
        except FileNotFoundError:
            return False
        for line in lines:
            assembler_line = AssemblerLine(line)
            if self.lines and self.lines[-1].continuation:
                assembler_line.continuing = True
            sanitize_line = assembler_line.sanitize()
            if sanitize_line:
                self.lines.append(sanitize_line)
        return True

    def first_pass(self):
        if self.labels:
            return True
        if not self.lines and not self.read_file():
            return False
        self.labels = [line.label for line in self.lines if line.label]
        return True

    def _get_blocks(self):
        lines = list()
        for line in self.lines:
            if line.label:
                yield line.label, lines
                lines = [line]
            else:
                lines.append(line)
        yield None, lines

    @staticmethod
    def _get_components(component_lines):
        lines = list()
        index = 0
        while index < len(component_lines):
            line = component_lines[index]
            if cmd.check(line.command, 'create') or (line.continuing and lines):
                lines.append(line)
            if line.command and cmd.check(line.command, 'set_cc'):
                temp_index = index + 1
                temp_lines = lines.copy()
                while temp_index < len(component_lines) and temp_index < index + 5:
                    temp_line = component_lines[temp_index]
                    temp_lines.append(temp_line)
                    if cmd.check(temp_line.command, 'check_cc'):
                        yield temp_lines
                        lines = list()
                        index = temp_index
                        break
                    elif cmd.check(temp_line.command, 'set_cc') or cmd.check(temp_line.command, 'exit'):
                        break
                    temp_index += 1
            if not line.continuation and lines:
                yield lines
                lines = list()
            index += 1

    def create_nodes(self, save=False):
        """
        Create code nodes and save it to the database.
        Nodes break at exit, conditions, calls, branches and loops
        :param save: Will store it in database if true
        :return: None
        """
        if not self.labels and not self.first_pass():
            return False
        nodes = dict()
        current_label = self.root_label
        nodes[current_label] = Node(current_label, self.name)
        for label, block_lines in self._get_blocks():
            label_index = 0
            last_lines = None
            for last_lines in self._get_components(block_lines):
                pass
            for component_lines in self._get_components(block_lines):
                component = Component(component_lines, self.labels)
                nodes[current_label].components.append(component)
                if (component.is_conditional or component.is_call) and component_lines != last_lines:
                    label_index += 1
                    if '-' not in current_label:
                        fall_down_label = f'{current_label}-{label_index}'
                    else:
                        fall_down_label = f"{current_label.split('-', 1)[0]}-{label_index}"
                    nodes[current_label].set_fall_down(fall_down_label)
                    current_label = fall_down_label
                    nodes[current_label] = Node(current_label, self.name)
            if label is None:
                break
            if not nodes[current_label].is_exit:
                nodes[current_label].set_fall_down(label)
            current_label = label
            nodes[current_label] = Node(current_label, self.name)
        self.nodes = nodes
        if save:
            for key in self.nodes:
                self.nodes[key].create()
        return True
