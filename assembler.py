from os import path
from models import Block, Path, Reference, Component


class AssemblerLine:
    EXCLUDE_C1 = {'*'}
    EXCLUDE_C5 = {'Check', 'RCS: ', 'VERS:', '=====', '*****'}
    TRIM = {'0': 7}
    TRUE_LABELS = {'DS': '0H', 'EQU': '*'}
    FALSE_LABELS = {'DS', 'DC', 'EQU', 'DSECT', 'CSECT'}
    TRUE_BRANCH = {'B', 'BE', 'BNE', 'BH', 'BNH', 'BL', 'BNL', 'BM', 'BNM', 'BP', 'BNP', 'BC', 'BO', 'BNO', 'BZ', 'BNZ',
                   'J', 'JE', 'JNE', 'JH', 'JNH', 'JL', 'JNL', 'JM', 'JNM', 'JP', 'JNP', 'JC', 'JO', 'JNO', 'JZ', 'JNZ'}
    EXIT_COMMANDS = Component.TYPE['exit']
    FUNCTION_CALL = Component.TYPE['call']

    def __init__(self, line):
        self.line = line.strip()
        self.label = None
        self.command = None
        self.operands = list()
        self.continuation = False
        self.continuing = False

    def _parse_line(self):
        """
        Call from santize line to initialize fields in AssemblerLine
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

    def get_branch(self, labels):
        """
        Check whether assembler line is branching to a label.
        Sanitize the line before calling this function.
        :param labels: list of valid labels.
        :return: A type of Reference objects with the goes and calls attribute of Reference initialize to
                 the appropriate labels.
        """
        branches = Reference()
        if not labels:
            return branches
        words = [parameter for operand in self.operands for parameter in operand.split('=')]
        for word in words:
            if word in labels:
                label = word
                if self.command in self.TRUE_BRANCH:
                    branches.add(goes=label)
                if self.command in self.FUNCTION_CALL:
                    branches.add(calls=label)
                operands = ''.join(self.operands)
                index = operands.find(label)
                if index > 0 and operands[index - 1] == '=':
                    branches.add(goes=label)
        return branches


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
                assembler_line.command = self.lines[-1].command
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

    def create_blocks(self, save=False):
        """
        Create code blocks and save it to the database
        :return: True if blocks created else false
        """
        if not self.labels and not self.first_pass():
            return False
        blocks = dict()
        current_label = self.root_label
        exit_command = False
        blocks[current_label] = Block(current_label, self.name)
        for assembler_line in self.lines:
            label = assembler_line.label
            # Current line in a label -> Initialize a new block
            if label:
                blocks[label] = Block(label, self.name)
                # If the previous block is falling down to this block then add its reference
                if not exit_command:
                    blocks[current_label].reference.add(goes=label)
                current_label = label
                exit_command = False
            if assembler_line.command in AssemblerLine.EXIT_COMMANDS:
                exit_command = True
            branches = assembler_line.get_branch(self.labels)
            blocks[current_label].reference.add(branches)
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
        next_labels = block.get_next()
        for label in next_labels:
            if label not in asm_path:
                self._build_path(self.blocks[label], asm_path.copy())
            else:   # If label is already in the path (it is looping) then add the loop label in the block.
                self.blocks[block.label].reference.add(loops=label)
        # Add the complete path when the last block is reached
        if not next_labels:
            self.paths.append(Path(self.name, asm_path))
            for label in asm_path:
                self.blocks[label].depth += 1
        return
