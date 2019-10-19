import os
import re
from copy import copy
from typing import Dict, Optional, List

from assembly2.mac0_generic import LabelReference
from assembly2.mac2_data_macro import macros
from assembly2.seg3_instruction import InstructionType
from assembly2.seg4_exec_macro import ExecutableMacroImplementation
from config import config
from utils.data_type import Register
from utils.file_line import Line, File


class Label:
    SEPARATOR = '.'

    def __init__(self, name: str, separator: Optional[str] = None):
        self.name: str = name
        self.index: int = 0
        self.separator: str = self.SEPARATOR if separator is None else separator

    def __repr__(self) -> str:
        return self.name if self.index == 0 else f"{self.name}{self.separator}{self.index}"


class LabelSave:
    def __init__(self):
        self.labels: List = list()

    def dumps(self, label: str) -> int:
        self.labels.append(label)
        return len(self.labels) << config.DSP_SHIFT

    def loads(self, saved: int) -> str:
        try:
            return self.labels[(saved >> config.DSP_SHIFT) - 1]
        except IndexError:
            raise IndexError


class Segment(ExecutableMacroImplementation):

    def __init__(self, name: str, file_name: str):
        super().__init__(name)
        self.file_name: str = file_name
        self.nodes: Dict[str, InstructionType] = dict()
        self.bas: LabelSave = LabelSave()

    def __repr__(self) -> str:
        return f"{self.name}:{self.nodes != dict()}:{len(self.nodes)}"

    @property
    def root_label(self) -> str:
        return '$$' + self.seg_name + '$$'

    @property
    def root_line(self) -> Line:
        line = Line.from_line(f"{self.root_label} EQU *")
        line.index = 0
        return line

    def assemble(self) -> None:
        if self.nodes:
            return
        # Default processing
        self._symbol_table = {**self.all_labels, **macros['EB0EB'].all_labels}
        self.set_using(self.name, Register('R8'))
        self.set_using('EB0EB', Register('R9'))
        # Get the data from line after removing CVS and empty lines.
        file_lines = File.open(self.file_name)
        # Create a list of Line objects
        lines = Line.from_file(file_lines)
        # First pass - Build Symbol Table and generate constants.
        self._build_symbol_table(lines)
        # Update index of each line
        lines = self._update_index(lines)
        # Second pass - Assemble instructions and populates n odes.
        self._assemble_instructions(lines)
        return

    def _build_symbol_table(self, lines: List[Line]) -> None:
        self.equ(self.root_line)
        for line in lines:
            length = line.length if line.length else config.DEFAULT_INSTRUCTION_LENGTH
            if line.is_first_pass:
                self._command[line.command](line)
            else:
                if line.label:
                    self._symbol_table[line.label] = LabelReference(line.label, self._location_counter, length,
                                                                    self.name)
                    self._symbol_table[line.label].set_instruction_branch()
                self._location_counter += length
        return

    def _assemble_instructions(self, lines: List[Line]) -> None:
        prior_label = Label(self.root_label)
        self.nodes[self.root_label] = self.equ(self.root_line)
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
            self.nodes[line.label] = self._command[line.command](line)
            # Other lines contain one or more conditions (like BNE, JL) and instruction that don't change cc.
            other_lines = ins_line[1:] if len(ins_line) > 1 else list()
            for other_line in other_lines:
                if other_line.is_assembler_directive:
                    continue
                condition = self._command[other_line.command](other_line)
                self.nodes[line.label].conditions.append(condition)

    def _process_assembler_directive(self, line: Line) -> bool:
        # return True -> skip creating node.
        # return False -> continue creating the node.
        # if line.is_sw00sr:
        #     DataMacroDeclaration(Line.from_line(" SW00SR REG=R3"), self.macro)
        #     return False
        if line.label and self.is_branch(line.label):
            return False
        if line.is_first_pass:
            return True
        # if self.macro.is_present(line.command):
        #     DataMacroDeclaration(line, self.macro)
        #     return True
        if not line.is_assembler_directive:
            return False
        # Second pass assembler directive like USING, PUSH, POP
        self._command[line.command](line)
        return True

    @staticmethod
    def _update_index(lines: List[Line]) -> List[Line]:
        for index, line in enumerate(lines):
            line.index = index + 1
        return lines

    def get_constant_bytes(self, label: str, length: Optional[int] = None) -> Optional[bytearray]:
        dsp = self.get_value(label)
        label = next(iter(re.split(r"[+-]", label)))
        length = length or self.lookup(label).length
        if self.lookup(label).is_literal:
            dsp = dsp - config.F4K
            return self.data.literal[dsp: dsp + length]
        else:
            return self.data.constant[dsp: dsp + length]


class _SegmentCollection:
    ASM_EXT = {'.asm', '.txt'}
    ASM_FOLDER_NAME = os.path.join(config.ROOT_DIR, 'asm')

    def __init__(self):
        self.segments: Dict = dict()  # Dictionary of Segment. Segment name is the key.
        for file_name in os.listdir(self.ASM_FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.ASM_EXT:
                continue
            seg_name = file_name[:-4].upper()
            file_name = os.path.join(self.ASM_FOLDER_NAME, file_name)
            self.segments[seg_name] = Segment(seg_name, file_name)
        return


segments = _SegmentCollection().segments
