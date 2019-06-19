from os import path
from models import Block, Path, Component
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
        words = self.line.split()
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

    @staticmethod
    def _get_components(component_lines):
        lines = list()
        index = 0
        while index < len(component_lines):
            line = component_lines[index]
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

    def create_blocks(self, save=False):
        """
        Create code blocks and save it to the database
        :param save: Will store it in database if true
        :return: None
        """
        if not self.labels and not self.first_pass():
            return False
        blocks = dict()
        current_label = self.root_label
        blocks[current_label] = Block(current_label, self.name)
        for label, block_lines in self._get_blocks():
            for component_lines in self._get_components(block_lines):
                if cmd.check(component_lines[0].command, 'create'):
                    blocks[current_label].components.append(Component(component_lines, self.labels))
            if not blocks[current_label].ends_in_exit():
                blocks[current_label].set_fall_down(label)
            current_label = label
            blocks[current_label] = Block(current_label, self.name)
        self.blocks = blocks
        if save:
            for key in self.blocks:
                self.blocks[key].create()
        return True

    def load_blocks(self):
        self.blocks = Block.query(dict_type=True, name=self.name)

    def create_paths(self, save=False):
        if not self.blocks:
            self.load_blocks()
        if not self.blocks:
            return False
        self._build_path(self.blocks[self.root_label])
        # Create paths for function calls
        call_blocks = [self.blocks[key] for key in self.blocks if self.blocks[key].get_calls()]
        done_labels = set()
        for block in call_blocks:
            for label in block.get_calls():
                if label not in done_labels:
                    self._build_path(self.blocks[label])
                done_labels.add(label)
        # Calculate the weight of each path
        for asm_path in self.paths:
            asm_path.weight = sum([self.blocks[label].depth for label in asm_path.path])
        # Save it into database if requested
        if save:
            for asm_path in self.paths:
                asm_path.create()
            for key in self.blocks:
                self.blocks[key].update()

    def _build_path(self, block, asm_path=None):
        if asm_path:
            asm_path.append(block.label)
        else:
            asm_path = [block.label]
        path_loops = False
        next_labels = block.get_next()
        for label in next_labels:
            if label not in asm_path:
                self._build_path(self.blocks[label], asm_path.copy())
            else:   # If label is already in the path (it is looping) then add the loop label in the block.
                path_loops = True
                if label not in self.blocks[block.label].get_loops():
                    self.blocks[block.label].add_loop_label(label)
        # Add the complete path when the last component of the block is exiting the program
        # or at least one loop label found
        if block.ends_in_program_exit() or path_loops:
            new_path = Path(self.name, asm_path)
            new_path.exit_on_loop = True if path_loops else False
            new_path.exit_on_program = True if block.ends_in_program_exit() else False
            self.paths.append(new_path)
            for label in asm_path:
                self.blocks[label].depth += 1
        return


def get_text_from_path(asm_path, blocks=None):
    # TODO code for checking invalid path. Two condition cannot be opposite.
    #  Weight = 5245, 7091, 7299, 8157
    #  Dependant on macro code.
    if not blocks:
        blocks = dict()
        for label in asm_path.path:
            block = Block.query_first(name=asm_path.name, label=label)
            if block:
                blocks[label] = block
    text_list = list()
    next_index = 1
    for label in asm_path.path:
        if label != asm_path.path[-1]:
            text = blocks[label].get_text(asm_path.path[next_index], prefix=' ' * 10)
            text_list.append(f'{label}:\n')
            if text:
                text_list.append(text)
        next_index += 1
    return ''.join(text_list)


def analyze_path(asm_path, blocks=None):
    if not blocks:
        blocks = dict()
        for label in asm_path.path:
            block = Block.query_first(name=asm_path.name, label=label)
            if block:
                blocks[label] = block
    component_paths = list()
    for index, label in enumerate(asm_path.path):
        if label == asm_path.path[-1]:
            break
        # Get a list of component path. Each component path has a list of components.
        # component -> components -> component_path -> component_paths
        component_path = blocks[label].get_path(asm_path.path[index + 1])
        component_paths.append(component_path)
