import os
from copy import copy

from v2.directive import AssemblerDirective
from config import config
from v2.errors import Error
from v2.file_line import File, Line, SymbolTable
from v2.macro import GlobalMacro, SegmentMacro
from v2.data_type import Register
from v2.instruction import InstructionType, Instruction


class Label:
    SEPARATOR = '.'

    def __init__(self, name, separator=None):
        self.name = name
        self.index = 0
        self.separator = self.SEPARATOR if separator is None else separator

    def __repr__(self):
        return self.name if self.index == 0 else f"{self.name}{self.separator}{self.index}"


class Constant:
    def __init__(self):
        self.data = bytearray()
        self.start = 0


class Segment:
    def __init__(self, file_name, name, macro):
        self.file_name = file_name
        self.name = name
        self.macro = macro
        self.nodes = dict()     # Dictionary of Instruction. Label is the key.
        self.errors = list()
        self.assembled = False
        self.constant = Constant()

    @property
    def root_label(self):
        return '$$' + self.name + '$$'

    def get_constant_bytes(self, label, length=None):
        try:
            symbol_table = self.macro.data_map[label]
        except KeyError:
            return None
        if symbol_table.name != self.name:
            return None
        length = length or symbol_table.length
        at = symbol_table.dsp - self.constant.start
        return self.constant.data[at: at + length]

    def load(self):
        if self.assembled:
            return True
        # Get the data from line after removing CVS and empty lines.
        file_lines = File.open(self.file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        # First pass - Build Symbol Table and generate constants.
        self._build_symbol_table(lines)
        # Second pass - Assemble instructions and populates nodes.
        self._assemble_instructions(lines)
        # Indicate segment assembled
        self.assembled = True
        return True

    def _build_symbol_table(self, lines):
        location_counter = 8
        for line in lines:
            length = line.length if line.length else 1
            dsp = location_counter
            if line.is_first_pass:
                name = self.name if self.macro.dsect is None else self.macro.dsect[1]
                asm_dir = AssemblerDirective(line.command)
                location_counter, result = asm_dir.update(line=line, macro=self.macro,  constant=self.constant,
                                                          location_counter=location_counter, name=name)

                if result != Error.NO_ERROR:
                    self.errors.append(f'{result} {line} {self.name}')
            else:
                location_counter += line.length
                if line.label:
                    self.macro.data_map[line.label] = SymbolTable(line.label, dsp, length, self.name)

    def _assemble_instructions(self, lines):
        prior_label = Label(self.root_label)
        for ins_line in Line.yield_lines(lines):
            line = ins_line[0]
            # Process assembler directive like USING and
            if self._process_assembler_directive(line):
                continue
            # Set the current label
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
            line.label = str(current_label)
            other_lines = ins_line[1:] if len(ins_line) > 1 else list()
            self._create_node(ins_line[0], other_lines)

    def _create_node(self, line, other_lines):
        # Create and empty instruction for a label with no instruction (EQU * or DS 0H)
        if line.is_node_label:
            self.nodes[line.label] = Instruction(line)
            return
        # Get the instruction class based on the command and create the dynamic instruction object
        instruction_object = InstructionType(line.command)
        node, result = instruction_object.create(line, self.macro)
        if result != Error.NO_ERROR:
            self.errors.append(f'{result} {line} {self.name}')
            return
        # Other lines contain one or more conditions (like BNE, JL) and instruction that don't change cc.
        for other_line in other_lines:
            if other_line.is_assembler_directive:
                continue
            instruction_object = InstructionType(other_line.command)
            condition, result = instruction_object.create(other_line, self.macro)
            if result != Error.NO_ERROR:
                self.errors.append(f'{result} {other_line} {self.name}')
                return
            node.conditions.append(condition)
        self.nodes[line.label] = node
        return

    def _process_assembler_directive(self, line):
        # return True means that skip creating node.
        # return False means further checks are required before deciding creation of node.
        if line.is_node_label and self.name == self.macro.data_map[line.label].name:
            return False
        if line.is_first_pass:
            return True
        if self.macro.is_present(line.command):
            base = Register(line.operand[4:])  # TODO To improve when KeyValue DataType is developed
            self.macro.load(line.command, base.reg)
            return True
        if not line.is_assembler_directive:
            return False
        # Second pass assembler directive like USING, PUSH, POP
        asm_dir = AssemblerDirective(line.command)
        _, result = asm_dir.update(line=line, macro=self.macro, location_counter=0, name=self.name)
        if result != Error.NO_ERROR:
            self.errors.append(f'{result} {line} {self.name}')
        return True


class Program:
    EXT = {'.asm', '.txt'}
    FOLDER_NAME = os.path.join(config.ROOT_DIR, 'asm')

    def __init__(self):
        self.segments = dict()     # Dictionary of Segment. Segment name is the key.
        self.macro = GlobalMacro()
        self.macro.load('EB0EB')
        for file_name in os.listdir(self.FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.EXT:
                continue
            seg_name = file_name[:-4].upper()
            seg_macro = SegmentMacro(self.macro)
            self.segments[seg_name] = Segment(os.path.join(self.FOLDER_NAME, file_name), seg_name, seg_macro)

    def load(self, seg_name):
        self.segments[seg_name].macro.copy_from_global()
        self.segments[seg_name].macro.set_using(seg_name, 'R8')
        self.segments[seg_name].macro.set_using('EB0EB', 'R9')
        self.segments[seg_name].load()
