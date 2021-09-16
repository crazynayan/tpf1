import os
import re
from typing import Dict, Optional, List, Tuple

from config import config
from p1_utils.data_type import DataType
from p1_utils.errors import NotFoundInSymbolTableError, EquDataTypeHasAmpersandError
from p1_utils.file_line import Line, File
from p2_assembly.mac2_data_macro import macros
from p2_assembly.seg2_ins_operand import Label
from p2_assembly.seg5_exec_macro import RealtimeMacroImplementation


class Segment(RealtimeMacroImplementation):

    def __init__(self, name: str, file_name: str):
        super().__init__(name)
        self.file_name: str = file_name
        self.file_type: str = str()
        self.source: str = config.LOCAL
        self.blob_name: str = str()

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
        self.set_using(self.name, base_reg="R8")
        self.load_macro("EB0EB", base="R9")
        # Ensure file is present for cloud objects
        if self.source == config.CLOUD and not os.path.exists(self.file_name):
            # noinspection PyPackageRequirements
            from google.cloud.storage import Client
            blob = Client().bucket(config.BUCKET).blob(self.blob_name)
            blob.download_to_filename(self.file_name)
        file = File(self.file_name)
        self.lst_macros = file.macros
        # Create a list of Line objects
        lines = Line.from_file(file.lines)
        # First pass - Build Symbol Table and generate constants.
        self._build_symbol_table(lines)
        # Update index of each line
        lines = self._update_index(lines)
        # Generate constants
        self._generate_constants()
        # Second pass - Assemble instructions and populates nodes.
        self._assemble_instructions(lines)
        return

    def _build_symbol_table(self, lines: List[Line]) -> None:
        prior_label: Label = Label(self.root_label())
        self.equ(self.root_line)
        # First pass for listings
        second_list: List[Tuple[Line, int]] = list()
        for macro_name, macro_lines in self.lst_macros.items():
            lines_list = Line.from_file(macro_lines)
            line = Line.from_line(f"{macro_name} EQU *")
            lines_list.insert(0, line)
            for line in lines_list:
                if line.command not in {"DS", "EQU", "ORG", "DSECT", "DC", "CSECT"}:
                    continue
                try:
                    self._command[line.command](line)
                except EquDataTypeHasAmpersandError:
                    pass
                except NotFoundInSymbolTableError:
                    second_list.append((line, self._location_counter))
        # Second pass
        for line, location_counter in second_list:
            if line.command not in {"EQU", "DS"}:
                continue
            self._location_counter = location_counter
            try:
                self._command[line.command](line)
            except NotFoundInSymbolTableError:
                raise NotFoundInSymbolTableError(line)
        # Load inline symbols
        for line in lines:
            if line.command in self.lst_macros:
                reg: Optional[str] = self.key_value(line).get_value("REG")
                if not reg:
                    continue
                self.set_using(dsect=line.command, base_reg=reg)
                continue
            if line.command in macros:
                self.load_macro_from_line(line)
                continue
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
                length = line.instruction_length
                self.add_label(line.label, self._location_counter, length, self.name)
                self._symbol_table[line.label].set_branch()
                self._location_counter += length
        return

    def _generate_constants(self) -> None:
        for dc in self.dc_list:
            if dc.expression and dc.data_type not in {"S", "V"}:
                dc.data = bytearray()
                for operand in dc.expression:
                    try:
                        dc.data.extend(DataType(dc.data_type, input=str(self.get_value(operand))).to_bytes(dc.length))
                    except KeyError:
                        raise NotFoundInSymbolTableError(f"{operand}=={dc}=={dc.expression}")
                    except NotFoundInSymbolTableError:
                        raise NotFoundInSymbolTableError(f"{operand}=={dc}=={dc.expression}")
                    except ZeroDivisionError:
                        pass
            self.data.set_constant(dc.data * dc.duplication_factor, dc.start)
        return

    def _assemble_instructions(self, lines: List[Line]) -> None:
        first_line = self.root_line
        self.nodes[first_line.label] = self.equ(first_line)
        prior_line: Line = first_line
        for line in lines:
            if self._process_assembler_directive(line):
                continue
            if prior_line.is_fall_down:
                self.nodes[prior_line.label].fall_down = line.label
            prior_line = line
            if line.command in self._command:
                self.nodes[line.label] = self._command[line.command](line)
            else:
                self.nodes[line.label] = self.key_value(line)
        return

    def _process_assembler_directive(self, line: Line) -> bool:
        # return True -> skip creating node.
        # return False -> continue creating the node.
        if line.is_sw00sr:
            self.load_macro("SW00SR", "R3")
            return False
        if line.command in macros:
            self.load_macro_from_line(line)
            return True
        if line.command in self.lst_macros:
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
    ASM_EXT = {".asm", ".txt"}
    ASM_FOLDER_NAME = os.path.join(config.ROOT_DIR, "p0_source", "asm")
    LST_EXT = {".lst"}
    LST_FOLDER_NAME = os.path.join(config.ROOT_DIR, "p0_source", "lst")

    def __init__(self):
        self.segments: Dict = dict()  # Dictionary of Segment. Segment name is the key.
        self.init_segments(self.ASM_FOLDER_NAME, self.ASM_EXT, config.ASM)
        self.init_segments(self.LST_FOLDER_NAME, self.LST_EXT, config.LST)
        self.init_all_from_cloud()

    def init_segments(self, folder_name: str, extensions: set, file_type: str):
        for file_name in os.listdir(folder_name):
            if len(file_name) < 6 or file_name[-4:].lower() not in extensions:
                continue
            seg_name = file_name[:4].upper()
            if seg_name in self.segments:
                continue
            file_name = os.path.join(folder_name, file_name)
            self.segments[seg_name]: Segment = Segment(seg_name, file_name)
            self.segments[seg_name].file_type = file_type
        return

    def init_all_from_cloud(self):
        if not config.CI_CLOUD_STORAGE:
            return
        # noinspection PyPackageRequirements
        from google.cloud.storage import Client
        blobs = Client().list_blobs(config.BUCKET)
        for blob in blobs:
            self.init_from_cloud(blob.name)
        return

    def init_from_cloud(self, blob_name: str):
        seg_name = blob_name[:4].upper()
        if seg_name in self.segments:
            return
        filename = os.path.join(config.DOWNLOAD_PATH, blob_name)
        segment = Segment(seg_name, filename)
        segment.file_type = config.LST
        segment.source = config.CLOUD
        segment.blob_name = blob_name
        self.segments[seg_name] = segment


segments = _SegmentCollection().segments
