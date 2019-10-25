import os
import re
from typing import Dict, Optional, List

from assembly.mac0_generic import LabelReference
from assembly.mac2_data_macro import macros
from assembly.seg2_ins_operand import Label
from assembly.seg5_exec_macro import UserDefinedMacroImplementation
from config import config
from utils.data_type import Register
from utils.file_line import Line, File


class Segment(UserDefinedMacroImplementation):

    def __init__(self, name: str, file_name: str):
        super().__init__(name)
        self.file_name: str = file_name

    def __repr__(self) -> str:
        return f"{self.name}:{self.nodes != dict()}:{len(self.nodes)}"

    @property
    def root_line(self) -> Line:
        line = Line.from_line(f"{self.root_label()} EQU *")
        line.index = 0
        return line

    @property
    def all_commands(self) -> List[str]:
        return list(self._command)

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
        prior_label: Label = Label(self.root_label())
        self.equ(self.root_line)
        for line in lines:
            if line.command in macros:
                continue
            length = line.length if line.length is not None else config.DEFAULT_INSTRUCTION_LENGTH
            if line.is_first_pass:
                self._command[line.command](line)
            if line.is_assembler_directive and not self.is_branch(line.label):
                continue
            if line.label:
                prior_label: Label = Label(line.label)
            else:
                prior_label.index += 1
                line.label = str(prior_label)
            if not line.is_assembler_directive:
                self._symbol_table[line.label] = LabelReference(line.label, self._location_counter, length, self.name)
                self._symbol_table[line.label].set_instruction_branch()
                self._location_counter += length
        return

    def _assemble_instructions(self, lines: List[Line]) -> None:
        prior_label: str = self.root_label()
        self.nodes[self.root_label()] = self.equ(self.root_line)
        for line in lines:
            # Process data macro declarations and second pass assembler directives like USING, PUSH, POP
            if self._process_assembler_directive(line):
                continue
            # Update the prior label with fall down
            prior_node = self.nodes[str(prior_label)]
            if prior_node.is_fall_down:
                prior_node.fall_down = line.label
            prior_label = line.label
            # Create the node based on type of instruction
            self.nodes[line.label] = self._command[line.command](line)

    def _process_assembler_directive(self, line: Line) -> bool:
        # return True -> skip creating node.
        # return False -> continue creating the node.
        if line.is_sw00sr:
            self.load_macro('SW00SR', 'R3')
            return False
        if line.command in macros:
            self.load_macro_from_line(line)
            return True
        if line.create_node_for_directive and self.is_branch(line.label):
            return False
        if line.is_first_pass:
            return True
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
