import re
from copy import copy

from assembly.directive import AssemblerDirective
from assembly.file_line import File, Line, SymbolTable, Label, LabelSave
from assembly.instruction import Instruction
from assembly.instruction_type import DataMacroDeclaration
from utils.errors import Error


class Data:
    def __init__(self):
        self.constant = bytearray()
        self.literal = bytearray()

    @property
    def next_constant(self):
        return len(self.constant)

    @property
    def next_literal(self):
        return len(self.literal)

    def extend_constant(self, data):
        self.constant.extend(data)

    def extend_literal(self, data):
        self.literal.extend(data)

    def get_constant(self, start, end=None):
        end = start + 1 if end is None else end
        return self.constant[start: end]

    def get_literal(self, start, end=None):
        end = start + 1 if end is None else end
        return self.literal[start: end]


class Segment:
    def __init__(self, file_name, name, macro):
        self.file_name = file_name
        self.name = name
        self.macro = macro
        self.nodes = dict()     # Dictionary of Instruction. Label is the key.
        self.errors = list()
        self.assembled = False
        self.data = Data()
        self.bas = LabelSave()

    def __repr__(self):
        return f"{self.name}:{self.assembled}:{len(self.nodes)}"

    @property
    def root_label(self):
        return '$$' + self.name + '$$'

    @property
    def root_line(self):
        return Line.from_line(f"{self.root_label} EQU *")

    def get_constant_bytes(self, label, length=None):
        if set("+-").intersection(set(label)):
            dsp, result = self.macro.get_value(label)
            label = next(iter(re.split(r"[+-]", label)))
        else:
            dsp = 0
        try:
            symbol_table = self.macro.data_map[label]
        except KeyError:
            return None
        length = length or symbol_table.length
        dsp = dsp or symbol_table.dsp
        if symbol_table.is_literal:
            dsp = dsp - 0x1000
            return self.data.get_literal(dsp, dsp + length)
        else:
            return self.data.get_constant(dsp, dsp + length)

    def load(self):
        if self.assembled:
            return
        # Init Macro
        self.macro.copy_default_from_global()
        self.macro.set_using(self.name, 'R8')
        self.macro.set_using('EB0EB', 'R9')
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
        return

    def _build_symbol_table(self, lines):
        AssemblerDirective.from_line(self.root_line, self.macro, self.name)
        for line in lines:
            length = line.length if line.length else 1
            if line.is_first_pass:
                name = self.name if self.macro.dsect is None else self.macro.dsect[1]
                result = AssemblerDirective.from_line(line, self.macro, name)
                if result != Error.NO_ERROR:
                    self.errors.append(f'{result} {line} {self.name}')
            else:
                if line.label:
                    self.macro.data_map[line.label] = SymbolTable(line.label, self.macro.location_counter,
                                                                  length, self.name)
                    self.macro.data_map[line.label].set_instruction_branch()
                self.macro.location_counter += line.length

    def _assemble_instructions(self, lines):
        prior_label = Label(self.root_label)
        self.nodes[str(prior_label)], _ = Instruction.from_line(self.root_line, self.macro)
        for ins_line in Line.yield_lines(lines):
            line = ins_line[0]
            # Process data macro declarations and second pass assembler directives like USING, PUSH, POP
            if self._process_assembler_directive(line):
                continue
            # Set the current label
            if not line.label:
                current_label = copy(prior_label)
                current_label.index += 1
            else:
                current_label = Label(line.label)
            # Update the prior label with fall down
            prior_node = self.nodes[str(prior_label)]
            if prior_node.is_fall_down:
                prior_node.fall_down = str(current_label)
            # Update labels
            prior_label = current_label
            line.label = str(current_label)
            # Create the node based on type of instruction
            self.nodes[line.label], result = Instruction.from_line(line, self.macro)
            if result != Error.NO_ERROR:
                self.errors.append(f'{result} {line} {self.name}')
            # Other lines contain one or more conditions (like BNE, JL) and instruction that don't change cc.
            other_lines = ins_line[1:] if len(ins_line) > 1 else list()
            for other_line in other_lines:
                if other_line.is_assembler_directive:
                    continue
                condition, result = Instruction.from_line(other_line, self.macro)
                if result != Error.NO_ERROR:
                    self.errors.append(f'{result} {other_line} {self.name}')
                self.nodes[line.label].conditions.append(condition)

    def _process_assembler_directive(self, line):
        # return True -> skip creating node.
        # return False -> continue creating the node.
        if line.is_sw00sr:
            DataMacroDeclaration(Line.from_line(" SW00SR REG=R3"), self.macro)
            return False
        if line.label and self.macro.is_branch(line.label):
            return False
        if line.is_first_pass:
            return True
        if self.macro.is_present(line.command):
            DataMacroDeclaration(line, self.macro)
            return True
        if not line.is_assembler_directive:
            return False
        # Second pass assembler directive like USING, PUSH, POP
        result = AssemblerDirective.from_line(line, self.macro, self.name)
        if result != Error.NO_ERROR:
            self.errors.append(f'{result} {line} {self.name}')
        return True
