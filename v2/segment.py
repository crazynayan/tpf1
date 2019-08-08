import os
import v2.instruction as ins

from copy import copy
from config import config
from v2.file_line import File, Line
from v2.macro import Macro
from v2.errors import Error
from v2.command import cmd


class Label:
    SEPARATOR = '.'

    def __init__(self, name, separator=None):
        self.name = name
        self.index = 0
        self.separator = self.SEPARATOR if separator is None else separator

    def __repr__(self):
        return self.name if self.index == 0 else f"{self.name}{self.separator}{self.index}"


class Segment:
    def __init__(self, file_name, name, macro):
        self.file_name = file_name
        self.name = name
        self.macro = macro
        self.nodes = dict()     # Dictionary of Instruction. Label is the key.
        self.errors = list()
        self.loaded = False

    @property
    def root_label(self):
        return '$$' + self.name + '$$'

    def load(self):
        if self.loaded:
            return True
        # Get the data from line after removing CVS and empty lines.
        file_lines = File.open(self.file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        prior_label = Label(self.root_label)
        for ins_line in Line.yield_lines(lines):
            line = ins_line[0]
            if not line.label:
                current_label = copy(prior_label)
                current_label.index += 1
            else:
                current_label = Label(line.label)
            # Update the prior label with fall down
            try:
                prior_node = self.nodes[str(prior_label)]
                if prior_node.is_fall_down:
                    prior_node.fall_down = str(current_label)
            except KeyError:    # Will only fail the first time
                pass
            prior_label = current_label
            current_label = str(current_label)
            other_lines = ins_line[1:] if len(ins_line) > 1 else list()
            self._create_node(ins_line[0], other_lines, current_label, self.name)
        self.loaded = True
        return True

    def _create_node(self, line, other_lines, current_label, seg_name):
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
        parameters = 'current_label, line.command, line.operand, self.macro'
        node, result = eval(f"ins.{instruction_class}.from_operand({parameters})")
        if result != Error.NO_ERROR:
            self.errors.append(f'{result} {line} {seg_name}')
            return
        # Get the instruction class based on the command and create the dynamic instruction object for conditions
        for line in other_lines:
            instruction_class = cmd.check(line.command, 'create')
            if not instruction_class:
                self.errors.append(f'{Error.INSTRUCTION_INVALID} {line} {seg_name}')
                return
            condition, result = eval(f"ins.{instruction_class}.from_operand({parameters})")
            if result != Error.NO_ERROR:
                self.errors.append(f'{result} {line} {seg_name}')
                return
            node.conditions.append(condition)
        self.nodes[current_label] = node
        return


class Program:
    EXT = {'.asm', '.txt'}
    FOLDER_NAME = os.path.join(config.ROOT_DIR, 'asm')

    def __init__(self):
        self.segments = dict()     # Dictionary of Segment. Segment name is the key.
        self.macro = Macro()
        self.macro.load('EB0EB', ins.Register('R9'))
        for file_name in os.listdir(self.FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.EXT:
                continue
            seg_name = file_name[:-4].upper()
            self.segments[seg_name] = Segment(os.path.join(self.FOLDER_NAME, file_name), seg_name, self.macro)

    def load(self, seg_name):
        if seg_name not in self.segments:
            return False
        return self.segments[seg_name].load()
