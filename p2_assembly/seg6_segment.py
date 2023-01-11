import re
from typing import Optional, List

from config import config, Config
from p1_utils.data_type import DataType
from p1_utils.errors import NotFoundInSymbolTableError, AssemblyError
from p1_utils.file_line import Line, File, get_lines_from_data_stream
from p2_assembly.mac2_data_macro import get_macros
from p2_assembly.seg2_ins_operand import Label
from p2_assembly.seg5_exec_macro import RealtimeMacroImplementation
from p2_assembly.seg8_listing import LstCmd, get_lines_from_listing_commands, get_or_create_lst_cmds


class Segment(RealtimeMacroImplementation):
    STARTUP = "STARTUP"

    def __init__(self, name: str, file_name: str, data_stream: str = str()):
        super().__init__(name)
        self.file_name: str = file_name
        self.file_type: str = str()
        self.source: str = config.LOCAL
        self.blob_name: str = str()
        self.error_line: str = str()
        self.error_constant: str = str()
        self.data_stream: str = data_stream

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
            lines = self._get_asm_lines()
            self._assemble_asm(lines)
            self._update_index(lines)
            if self.data_stream:
                excluded_cmds = {"ENTRC", "ENTNC", "EXITC", "SENDA", "BACKC", "ENTDC", "SERRC", "SYSRA", "SNAPC"}
                line = next((line for line in lines if line.command in excluded_cmds), None)
                if line:
                    self.error_line = str(line)
                    return
        else:
            lines = self._assemble_lst()
        try:
            # Generate constants
            self._generate_constants()
            # Second pass - Assemble instructions and populates nodes.
            self._assemble_instructions(lines)
        except AssemblyError as e:
            print(e)  # This is required to see which line has assembly error
            self.nodes = dict()
            if self.file_type == config.LST:
                LstCmd.objects.filter_by(seg_name=self.seg_name).delete(workers=100)
        return

    def _get_asm_lines(self) -> List[Line]:
        if self.data_stream:
            lines = get_lines_from_data_stream(self.data_stream)
        else:
            file = File(self.file_name)
            lines = Line.from_file(file.lines)
        return lines

    def _assemble_asm(self, lines: List[Line]) -> None:
        self.load_macro("EB0EB", base="R9")
        prior_label: Label = Label(self.root_label())
        macros = get_macros()
        for line in lines:
            if line.command in macros:
                self.load_macro_from_line(line, using=False)
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
                    self.add_label(line.label, line.dsp, 0, dsect_name, based=dsect_name != self.seg_name)
                continue
            if line.label:
                prior_label: Label = Label(line.label)
            else:
                prior_label.index += 1
                line.label = str(prior_label)
            self.add_label(line.label, line.dsp, line.instruction_length, dsect_name)
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
            if line.command == "EQU" and self.all_labels[line.label].based:
                self.all_labels[line.label].based = self.is_based(line.operand)
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
        if self.file_type == config.ASM:
            return self._process_assembler_directive_asm(line)
        else:
            return self._process_assembler_directive_lst(line)

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
        if line.command in get_macros():
            self.load_macro_from_line(line, using=True)
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
    def _update_index(lines: List[Line]) -> None:
        for index, line in enumerate(lines):
            line.index = index + 1
        return

    def get_constant_bytes(self, label: str, length: Optional[int] = None) -> Optional[bytearray]:
        dsp = self.get_value(label)
        label = next(iter(re.split(r"[+-]", label)))
        length = length or self.lookup(label).length
        if self.lookup(label).is_literal:
            dsp = dsp - config.F4K
            return self.data.literal[dsp: dsp + length]
        else:
            return self.data.constant[dsp: dsp + length]


def get_assembled_startup_seg(data_stream: str) -> Segment:
    startup_script = f"$#STARTUP EQU *\n{data_stream}"
    seg = Segment(name=Segment.STARTUP, file_name="startup.asm", data_stream=startup_script)
    seg.seg_name = Segment.STARTUP
    seg.file_type = Config.ASM
    if data_stream.strip():
        seg.assemble()
    return seg
