import os
# noinspection PyUnresolvedReferences
import v2.instruction as ins

from config import config
from v2.file_line import File, Line
from v2.macro import Macro
from v2.errors import Error
from v2.data_type import Register
from v2.command import cmd


class SegmentFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.loaded = False
        self.root_label = None

    def __repr__(self):
        return f'{self.file_name}:{self.root_label}:{self.loaded}'


class Segment:
    EXT = {'.asm', '.txt'}
    FOLDER_NAME = os.path.join(config.ROOT_DIR, 'asm')
    LABEL_SEPARATOR = '.'

    def __init__(self):
        self.files = dict()     # Dictionary of SegmentFile. Segment name is the key.
        self.nodes = dict()     # Dictionary of Instruction. Label is the key.
        self.errors = list()
        self.macro = Macro()
        self.macro.load('EB0EB', Register('R9'))
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
        label_index = 1
        current_label = self.files[seg_name].root_label
        for line in lines:
            prior_label = current_label
            if not line.label:
                # Add the suffix to the label
                if self.LABEL_SEPARATOR in current_label:
                    current_label = f'{current_label.split(self.LABEL_SEPARATOR)[0]}{self.LABEL_SEPARATOR}{label_index}'
                else:
                    current_label = f'{current_label}{self.LABEL_SEPARATOR}{label_index}'
                label_index += 1
            else:
                current_label = line.label
            # Update the prior label with fall down
            try:        # TODO Also check if the prior node is NOT an exit command
                self.nodes[prior_label].fall_down = current_label
            except KeyError:    # Will only fail the first time
                pass
            # Get the instruction class based on the command and create the dynamic instruction object
            instruction_class = cmd.check(line.command, 'create')
            if not instruction_class:
                self.errors.append(f'{Error.INSTRUCTION_INVALID} {line} {seg_name}')
                continue
            node, result = eval(f"ins.{instruction_class}.from_operand(current_label, "
                                f"line.command, line.operand, self.macro)")
            if result == Error.NO_ERROR:
                self.nodes[current_label] = node
            else:
                self.errors.append(f'{result} {line} {seg_name}')
        self.files[seg_name].loaded = True
        return True
