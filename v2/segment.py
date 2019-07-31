import os
import v2.instruction as ins

from copy import copy
from config import config
from v2.file_line import File, Line
from v2.macro import Macro
from v2.errors import Error
from v2.command import cmd


class SegmentFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.loaded = False
        self.root_label = None

    def __repr__(self):
        return f'{self.file_name}:{self.root_label}:{self.loaded}'


class Label:
    SEPARATOR = '.'
    BEFORE_GOES_SEPARATOR = '*'

    def __init__(self, name, separator=None):
        self.name = name
        self.index = 0
        self.separator = self.SEPARATOR if separator is None else separator

    def __repr__(self):
        return self.name if self.index == 0 else f"{self.name}{self.separator}{self.index}"


class Segment:
    EXT = {'.asm', '.txt'}
    FOLDER_NAME = os.path.join(config.ROOT_DIR, 'asm')

    def __init__(self):
        self.files = dict()     # Dictionary of SegmentFile. Segment name is the key.
        self.nodes = dict()     # Dictionary of Instruction. Label is the key.
        self.errors = list()
        self.macro = Macro()
        self.macro.load('EB0EB', ins.Register('R9'))
        for file_name in os.listdir(self.FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.EXT:
                continue
            seg_file = SegmentFile(os.path.join(self.FOLDER_NAME, file_name))
            seg_name = file_name[:-4].upper()
            seg_file.root_label = f'$${seg_name}$$'
            self.files[seg_name] = seg_file

    def load(self, seg_name):
        if seg_name not in self.files:
            return False
        if self.files[seg_name].loaded:
            return True
        # Get the data from line after removing CVS and empty lines.
        file_lines = File.open(self.files[seg_name].file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        prior_label = Label(self.files[seg_name].root_label)
        for ins_line in Line.yield_lines(lines):
            line = ins_line[0]
            if not line.label:
                current_label = copy(prior_label)
                current_label.index += 1
            else:
                current_label = Label(line.label)
            # Update the prior label with fall down
            try:        # TODO Also check if the prior node is NOT an exit command
                self.nodes[str(prior_label)].fall_down = str(current_label)
            except KeyError:    # Will only fail the first time
                pass
            prior_label = current_label
            current_label = str(current_label)
            if len(ins_line) == 1:
                self._create_node(ins_line[0], None, current_label, seg_name)
                continue
            self._create_node(ins_line[0], ins_line[-1], current_label, seg_name)
            goes_label = Label(current_label, Label.BEFORE_GOES_SEPARATOR)
            for line in ins_line[1:-1]:
                self.nodes[current_label].before_goes += 1
                goes_label.index += 1
                self._create_node(line, None, str(goes_label), seg_name)
        self.files[seg_name].loaded = True
        return True

    def _create_node(self, line, check_line, current_label, seg_name):
        # Create and empty instruction for a label with no instruction (EQU * or DS 0H)
        if current_label == line.label and not self.macro.is_location_counter_changed(line):
            node = ins.Instruction(line.label, line.command)
            self.nodes[current_label] = node
            return
        # Get the instruction class based on the command and create the dynamic instruction object
        instruction_class = cmd.check(line.command, 'create')
        if not instruction_class:
            self.errors.append(f'{Error.INSTRUCTION_INVALID} {line} {seg_name}')
            return
        method = 'from_operand'
        parameters = 'current_label, line.command, line.operand, self.macro'
        if check_line is not None:
            instruction_class += 'Conditional'
            method += '_condition'
            parameters += ', check_line.operand, check_line.command'
        node, result = eval(f"ins.{instruction_class}.{method}({parameters})")
        if result == Error.NO_ERROR:
            self.nodes[current_label] = node
        else:
            self.errors.append(f'{result} {line} {seg_name}')
        return
