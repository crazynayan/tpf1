import os
import re
from typing import Dict, Optional, List

from config import config
from p1_utils.data_type import DataType
from p1_utils.errors import NotFoundInSymbolTableError, AssemblyError
from p1_utils.file_line import Line, File
from p2_assembly.mac2_data_macro import macros
from p2_assembly.seg2_ins_operand import Label
from p2_assembly.seg5_exec_macro import RealtimeMacroImplementation
from p2_assembly.seg8_listing import LstCmd, get_lines_from_listing_commands, get_or_create_lst_cmds


class Segment(RealtimeMacroImplementation):

    def __init__(self, name: str, file_name: str):
        super().__init__(name)
        self.file_name: str = file_name
        self.file_type: str = str()
        self.source: str = config.LOCAL
        self.blob_name: str = str()
        self.error_line: str = str()
        self.error_constant: str = str()

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
        if self.file_type == config.ASM:
            lines = self._assemble_asm()
            lines = self._update_index(lines)
        else:
            lines = self._assemble_lst()
        try:
            # Generate constants
            self._generate_constants()
            # Second pass - Assemble instructions and populates nodes.
            self._assemble_instructions(lines)
        except AssemblyError:
            self.nodes = dict()
            if self.file_type == config.LST:
                LstCmd.objects.filter_by(seg_name=self.seg_name).delete(workers=100)
        return

    def _assemble_asm(self) -> List[Line]:
        self.load_macro("EB0EB", base="R9")
        file = File(self.file_name)
        # Create a list of Line objects
        lines = Line.from_file(file.lines)
        # Load inline data macro and DSECT
        prior_label: Label = Label(self.root_label())
        for line in lines:
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
        return lines

    def _assemble_lst(self):
        blob_name = self.blob_name if self.source == config.CLOUD else str()
        listing_commands: List[LstCmd] = get_or_create_lst_cmds(self.seg_name, self.file_name, blob_name)
        lines: List[Line] = get_lines_from_listing_commands(listing_commands)
        prior_label: Label = Label(self.root_label())
        dsect_name = self.seg_name
        for line in lines:
            if line.command in config.DIRECTIVE_IGNORE_LABEL:
                if line.command == "DSECT":
                    dsect_name = line.label
                    self.add_label(dsect_name, 0, 1, dsect_name)
                elif line.command == "CSECT":
                    dsect_name = self.seg_name
                continue
            if line.node_exception or dsect_name != self.seg_name:
                if line.label:  # Only add it in the symbol table. Do not create the node for the same
                    self.add_label(line.label, line.dsp, 0, dsect_name)
                continue
            if line.label:
                prior_label: Label = Label(line.label)
            else:
                prior_label.index += 1
                line.label = str(prior_label)
            self.add_label(line.label, line.dsp, 0, dsect_name)
            self.all_labels[line.label].set_branch()
        # Update the length of labels in EQU, DS and DC
        for line in lines:
            if not line.label or line.command in config.DIRECTIVE_IGNORE_LABEL:
                continue
            if line.command in {"DS", "DC"}:
                length = self.ds_dc_lst(line)
            elif line.command == "EQU":
                length = self.equ_lst(line)
            else:
                length = 1
            self.all_labels[line.label].length = length
        return lines

    def _generate_constants(self) -> None:
        for dc in self.dc_list:
            if dc.expression and dc.data_type not in {"V"}:
                dc.data = bytearray()
                for operand in dc.expression:
                    self.error_constant = f"{dc}:{dc.expression}"
                    try:
                        dc.data.extend(DataType(dc.data_type, input=str(self.get_value(operand))).to_bytes(dc.length))
                    except KeyError:
                        raise NotFoundInSymbolTableError(f"{operand}=={dc}=={dc.expression}")
                    except NotFoundInSymbolTableError:
                        raise NotFoundInSymbolTableError(f"{operand}=={dc}=={dc.expression}")
            self.data.set_constant(dc.data * dc.duplication_factor, dc.start)
        self.error_constant = str()
        return

    def _assemble_instructions(self, lines: List[Line]) -> None:
        first_line = self.root_line
        self.nodes[first_line.label] = self.equ(first_line)
        prior_line: Line = first_line
        for line in lines:
            self.error_line = line
            if self._process_assembler_directive(line):
                continue
            if prior_line.is_fall_down:
                self.nodes[prior_line.label].fall_down = line.label
            prior_line = line
            if line.command in self._command:
                self.nodes[line.label] = self._command[line.command](line)
            else:
                self.nodes[line.label] = self.key_value(line)
        self.error_line = str()
        return

    def _process_assembler_directive(self, line: Line) -> bool:
        if self.file_type == config.LST:
            return self._process_assembler_directive_lst(line)
        else:
            return self._process_assembler_directive_asm(line)

    def _process_assembler_directive_lst(self, line: Line) -> bool:
        # return True -> skip creating node.
        # return False -> continue creating the node.
        if not line.is_assembler_directive and not line.node_exception:
            return False
        if line.create_node_for_directive and self.is_branch(line.label):
            return False
        if line.command in config.DIRECTIVE_SECOND_PASS - {"DATAS"}:
            # Second pass assembler directive like USING, PUSH, POP
            self._command[line.command](line)
        return True

    def _process_assembler_directive_asm(self, line: Line) -> bool:
        # return True -> skip creating node.
        # return False -> continue creating the node.
        if line.is_sw00sr:
            self.load_macro("SW00SR", "R3")
            return False
        if line.command in macros:
            self.load_macro_from_line(line)
            return True
        if line.create_node_for_directive and self.is_branch(line.label):
            return False
        if not line.is_assembler_directive:
            return False
        if not line.is_first_pass:
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
        client = Client()
        blobs = client.list_blobs(config.BUCKET)
        for blob in blobs:
            self.init_from_cloud(blob.name)
        client.close()
        return

    def init_from_cloud(self, blob_name: str):
        seg_name = blob_name[:4].upper()
        if seg_name in self.segments and self.segments[seg_name].source == config.LOCAL:
            return
        filename = os.path.join(config.DOWNLOAD_PATH, blob_name)
        segment = Segment(seg_name, filename)
        segment.file_type = config.LST
        segment.source = config.CLOUD
        segment.blob_name = blob_name
        self.segments[seg_name] = segment

    def is_seg_present(self, seg_name: str) -> bool:
        if not config.CI_CLOUD_STORAGE:
            return seg_name in self.segments
        if seg_name in self.segments:
            return True
        self.init_all_from_cloud()
        return seg_name in self.segments

    def get_seg(self, seg_name) -> Optional[Segment]:
        if not self.is_seg_present(seg_name):
            return None
        return self.segments[seg_name]

    def get_all_segments(self) -> Dict:
        if config.CI_CLOUD_STORAGE:
            self.init_all_from_cloud()
        return self.segments

    def is_seg_local(self, seg_name) -> bool:
        if not self.is_seg_present(seg_name):
            return False
        return self.segments[seg_name].source == config.LOCAL


seg_collection = _SegmentCollection()
