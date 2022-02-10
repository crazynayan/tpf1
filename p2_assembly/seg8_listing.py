import os
import pickle
import re
from copy import copy
from typing import List, Optional

from firestore_ci import FirestoreDocument

from config import config
from p1_utils.file_line import Line, File
from p2_assembly.seg7_listing_line import ListingLine, create_listing_lines


class LstCmd(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.seg_name: str = str()  # 4 char name of the listing. Cannot be empty.
        self.stmt: str = str()
        self.source_stmt = str()
        self.label: str = str()
        self.command: str = str()
        self.operand: str = str()
        self.dsp: int = int()
        self.is_machine_code: bool = bool()
        self.node_exception: bool = bool()

    @property
    def display_dsp(self) -> str:
        return " " * 5 if self.dsp == -1 else f"D{self.dsp:04X}"

    @property
    def display_node_ex(self) -> str:
        return "X" if self.node_exception else " "

    def __repr__(self):
        return f"{self.seg_name}:{self.stmt:7}:{self.source_stmt:7}: {self.display_dsp} :{self.display_node_ex}: " \
               f"{self.label:10}: {self.command:10}: {self.operand}"


LstCmd.init("listing_commands")


def create_listing_command(listing_line: ListingLine, seg_name) -> LstCmd:
    listing_command: LstCmd = LstCmd()
    listing_command.seg_name = seg_name
    listing_command.stmt = listing_line.stmt
    listing_command.source_stmt = listing_line.source_stmt
    listing_command.label = listing_line.label
    listing_command.dsp = listing_line.dsp
    listing_command.command = listing_line.command
    listing_command.operand = listing_line.operand
    listing_command.is_machine_code = listing_line.is_machine_code
    return listing_command


def split_operand(operand: str) -> list:
    return re.split("[,'=()+-]", operand)


def create_listing_commands(seg_name: str, lines: List[str]) -> List[LstCmd]:
    listing_lines: List[ListingLine] = create_listing_lines(seg_name, lines)
    if not listing_lines:
        return list()
    equ_ds: set = {"EQU", "DS"}
    # Init with commands that require generated code
    exec_macro_commands: set = {"GLOBZ", "#IF", "#ELSE", "#", "#EIF", "#ELIF", "#GOTO", "#LOCA", "#PERF", "#SUBR",
                                "#ESUB", "#EIFM", "#DO", "#EDO", "#EXEC", "#STPH", "#CAST", "#CASE", "#ECAS",
                                "#EXIF", "#OREL", "#DOEX", "#ELOP", "TYCVA"}
    # Init with commands that will never be expanded (IBM TPF specific executable macro)
    ibm_cmds: set = {"DETAC", "FINIS", "FLIPC", "ATTAC", "ENTNC"}
    # Initialize the different type of source stmt
    ibm_source_stmt: set = {line.stmt for line in listing_lines if line.command in ibm_cmds and not line.source_stmt}
    exec_macro_source_stmt: set = {line.stmt for line in listing_lines if line.command in exec_macro_commands
                                   and not line.source_stmt}
    exec_ibm_source_stmt: set = exec_macro_source_stmt.union(ibm_source_stmt)
    other_source_stm: set = {line.source_stmt for line in listing_lines if line.source_stmt
                             and line.source_stmt not in exec_ibm_source_stmt}
    # Source commands = True Source - Data Macro declaration - Source commands that have been expanded
    source_commands: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                     if not line.source_stmt
                                     and line.stmt not in exec_macro_source_stmt
                                     and not line.command.startswith("=")]
    # source_labels are all words in the operands of source commands
    source_labels: set = {label for cmd in source_commands for label in split_operand(cmd.operand) if label}
    # source_branch_labels are all branch labels from the source_commands
    source_branch_labels: set = {cmd.label for cmd in source_commands}
    # Exec cmds = Exec cmds that have been expanded - Ignored Exec cmds - EQU/DS cmds that are not used
    non_equ_exec_cmds: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                       if line.source_stmt and line.source_stmt in exec_macro_source_stmt
                                       and line.command not in equ_ds]
    non_equ_exec_labels: set = {label for cmd in non_equ_exec_cmds for label in split_operand(cmd.operand) if label}
    source_exec_labels: set = source_labels.union(non_equ_exec_labels)
    equ_exec_cmds: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                   if line.source_stmt and line.source_stmt in exec_macro_source_stmt
                                   and line.command in equ_ds and line.label in source_exec_labels]
    exec_labels: set = {label for cmd in equ_exec_cmds for label in split_operand(cmd.operand) if label}
    source_exec_labels: set = source_exec_labels.union(exec_labels)
    # Data cmds = Generated USING,DSECT,CSECT,PUSH,POP + Generated EQU, DS that are used in source or exec cmds.
    using_data_cmds: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                     if line.source_stmt and line.source_stmt in other_source_stm
                                     and line.command in {"USING", "DSECT", "CSECT", "PUSH", "POP"}]
    # equ_ds_data_cmds is Generated EQU, DS that are used in source or exec cmds - branch labels from source cmds
    # This is to remove generated labels with labels in front of realtime macros.
    equ_ds_data_cmds: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                      if line.source_stmt and line.source_stmt in other_source_stm
                                      and line.command in equ_ds and line.label in source_exec_labels
                                      and line.label not in source_branch_labels]
    # equ_ds_labels are all words in the operands of equ_ds_data commands
    equ_ds_labels: set = {label for cmd in equ_ds_data_cmds for label in split_operand(cmd.operand) if label}
    # equ_ds_stmt are all stmt that are in generated EQU DS - This is to avoid duplicates
    equ_ds_stmt: set = {cmd.stmt for cmd in equ_ds_data_cmds}
    # equ_ds_extra_cmds are EQU DS definition that are used as operands in equ_ds_data_cmds
    equ_ds_extra_cmds: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                       if line.source_stmt and line.source_stmt in other_source_stm
                                       and line.command in equ_ds and line.label in equ_ds_labels
                                       and line.label not in source_branch_labels
                                       and line.stmt not in equ_ds_stmt]
    listing_commands: List[LstCmd] = (source_commands + non_equ_exec_cmds + equ_exec_cmds + using_data_cmds
                                      + equ_ds_data_cmds + equ_ds_extra_cmds)
    listing_commands.sort(key=lambda item: item.stmt)
    # Setup node exception
    node_exception_cmds: set = {"BEGIN", "PGMID"}
    node_exception_stmt: set = {line.stmt for line in listing_lines if line.command in node_exception_cmds
                                and not line.source_stmt}
    data_macro_source_stmt: set = {stmt for stmt in other_source_stm
                                   if not any(line.is_machine_code for line in listing_lines
                                              if line.source_stmt == stmt)}
    for cmd in listing_commands:
        if cmd.source_stmt:
            if cmd.source_stmt in data_macro_source_stmt and cmd.source_stmt not in exec_macro_source_stmt:
                cmd.node_exception = True
            elif cmd.source_stmt in node_exception_stmt:
                cmd.node_exception = True
        elif cmd.stmt in data_macro_source_stmt:
            cmd.node_exception = True
    # Replace SVC with macro calls
    updated_lst_cmds: List[LstCmd] = list()
    macro_cmd: Optional[LstCmd] = None
    svc_cmds: set = {"FINWC", "FIWHC"}
    for cmd in listing_commands:
        if cmd.command == "SVC" and cmd.operand in svc_cmds:
            macro_cmd = copy(cmd)
            macro_cmd.command = cmd.operand
            macro_cmd.operand = str()
            continue
        if not macro_cmd:
            updated_lst_cmds.append(cmd)
        elif cmd.command == "DC" and cmd.operand.startswith("AL1(D"):
            macro_cmd.operand = cmd.operand[4:6]
        elif cmd.command == "BRC":
            macro_cmd.operand += ",SUCCESS=" if cmd.operand.startswith("15-7") else ",ERROR="
            macro_cmd.operand += cmd.operand.split(",")[1]
            updated_lst_cmds.append(macro_cmd)
            macro_cmd = None
    return updated_lst_cmds


def write_tmp_output(seg_name: str):
    lst_cmds: List[LstCmd] = LstCmd.objects.filter_by(seg_name=seg_name).order_by("stmt").get()
    if not lst_cmds:
        print("Segment not found or not assembled yet.")
        return
    with open(f"tmp/{seg_name}-extract.txt", "w") as fh:
        fh.writelines(f"{str(line)}\n" for line in lst_cmds)
    print("Seg extract saved in tmp directory")


def create_line(listing_command: LstCmd) -> Line:
    line = Line()
    line.label = listing_command.label
    line.command = listing_command.command
    line.operand = listing_command.operand
    line.dsp = listing_command.dsp
    line.node_exception = listing_command.node_exception
    line.index = int(listing_command.stmt.strip())
    return line


def get_lines_from_listing_commands(listing_commands: List[LstCmd]) -> List[Line]:
    return [create_line(command) for command in listing_commands]


def get_from_lxp(filename: str) -> List[LstCmd]:
    try:
        with open(filename, "rb") as file:
            lst_cmds = pickle.load(file)
        lst_cmds.sort(key=lambda item: item.stmt)
    except (FileNotFoundError, pickle.UnpicklingError):
        lst_cmds = list()
    return lst_cmds


def create_lxp(seg_name: str) -> str:
    lst_cmds: List[LstCmd] = LstCmd.objects.filter_by(seg_name=seg_name.upper()).order_by("stmt").get()
    if not lst_cmds:
        return str()
    filename = f"{config.LXP_FOLDER_NAME}/{seg_name.lower()}.{config.LXP}"
    with open(filename, "wb") as file:
        pickle.dump(lst_cmds, file)
    return filename


def get_or_create_lst_cmds(seg_name: str, filename: str, blob_name: str) -> List[LstCmd]:
    lst_cmds_from_lxp: List[LstCmd] = get_from_lxp(filename)
    if lst_cmds_from_lxp:
        return lst_cmds_from_lxp
    lst_cmds: List[LstCmd] = LstCmd.objects.filter_by(seg_name=seg_name).order_by("stmt").get()
    if lst_cmds:
        return lst_cmds
    # Ensure file is present for cloud objects
    if blob_name and not os.path.exists(filename):
        # noinspection PyPackageRequirements
        from google.cloud.storage import Client
        client = Client()
        blob = client.bucket(config.BUCKET).blob(blob_name)
        blob.download_to_filename(filename)
        client.close()
    lines: List[str] = File.open_file(filename)
    listing_commands: List[LstCmd] = create_listing_commands(seg_name, lines)
    LstCmd.objects.create_all(LstCmd.objects.to_dicts(listing_commands))
    return listing_commands
