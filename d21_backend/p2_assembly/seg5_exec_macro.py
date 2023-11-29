import re
from typing import List, Tuple, Union, Optional

from d21_backend.config import config
from d21_backend.p1_utils.data_type import Register
from d21_backend.p1_utils.errors import RegisterInvalidError, AssemblyError
from d21_backend.p1_utils.file_line import Line
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p2_assembly.seg2_ins_operand import FieldBaseDsp
from d21_backend.p2_assembly.seg3_ins_type import InstructionGeneric, RegisterData
from d21_backend.p2_assembly.seg4_ins_implementation import InstructionImplementation


class KeyValue(InstructionGeneric):

    def __init__(self, line: Line,
                 operands: List[Tuple[str, Union[Optional[str], List[Tuple[str, Optional[str]]]]]],
                 branches: List[str]):
        super().__init__(line)
        self._operands: List[Tuple[str, Union[Optional[str], FieldBaseDsp, List[Tuple[str, Optional[str]]]]]] = operands
        self.branches: List[str] = branches

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self._operands}"

    @property
    def keys(self) -> List[str]:
        return [key_value[0] for key_value in self._operands]

    @property
    def sub_key_value(self) -> List[Tuple[str, List]]:
        # Returns all key_value that have sub_keys
        return [key_value for key_value in self._operands if isinstance(key_value[1], list)]

    @property
    def next_labels(self) -> set:
        labels = set(self.branches)
        if self.fall_down:
            labels.add(self.fall_down)
        return labels

    @property
    def goes(self) -> str:
        return next(iter(self.branches), None)

    def get_value(self, key: str) -> Union[Optional[str], FieldBaseDsp,
                                           List[Tuple[str, Union[Optional[str], FieldBaseDsp]]]]:
        # Returns
        # None - For key not found
        # value: str - For KEY=VALUE
        # List[sub_key] - For KEY=(SUB_KEY1, SUB_KEY2)
        # List[Tuple[sub_key, sub_value]] - For KEY=(SUB_KEY1=SUB_VALUE1, SUB_KEY2=SUB_VALUE2)
        value = next((key_value[1] for key_value in self._operands if key_value[0] == key), None)
        if isinstance(value, list) and all(sub_key_value[1] is None for sub_key_value in value):
            value = [sub_key_value[0] for sub_key_value in value]
        return value

    def get_original_value(self, key: str):
        return next((key_value[1] for key_value in self._operands if key_value[0] == key), None)

    def get_sub_value(self, key: str, sub_key: str) -> Union[Optional[str], FieldBaseDsp]:
        return next((sub_key_value[1] for key_value in self.sub_key_value for sub_key_value in key_value[1]
                     if key_value[0] == key and sub_key_value[0] == sub_key), None)

    def set_sub_value(self, value: FieldBaseDsp, original_value: str, key: str, sub_key: str) -> None:
        key_value_list = self.get_value(key)
        key_value_list.remove((sub_key, original_value))
        key_value_list.append((sub_key, value))

    def set_value(self, value: FieldBaseDsp, original_value: str, key: str) -> None:
        self._operands.remove((key, original_value))
        self._operands.append((key, value))

    def set_key_value_list(self, key_value_list: list, original_key_value_list: list, key) -> None:
        self._operands.remove((key, original_key_value_list))
        self._operands.append((key, key_value_list))

    def add_key(self, key: str, value: Union[str, list]):
        self._operands.append((key, value))


class SegmentCall(KeyValue):

    def __init__(self, line, key_value: KeyValue):
        super().__init__(line, key_value._operands, key_value.branches)


class RealtimeMacroImplementation(InstructionImplementation):
    def __init__(self, name: str):
        super().__init__(name)
        self._command["ENTRC"] = self.seg_call
        self._command["ENTNC"] = self.seg_call
        self._command["ENTDC"] = self.seg_call
        self._command["BACKC"] = self.instruction_generic
        self._command["EXITC"] = self.instruction_generic
        self._command["GLOBZ"] = self.globz
        self._command["FACE"] = self.instruction_generic
        self._command["PNAMC"] = self.pnamc
        self._command["DATE"] = self.date_macro
        self._command["DBRED"] = self.dbred
        self._command["DBDEL"] = self.dbred
        self._command["PDRED"] = self.pdred
        self._command["PDMOD"] = self.pdred
        self._command["DBADD"] = self.dbadd
        self._command["PNRJR"] = self.pdred
        self._command["FINWC"] = self.finwc
        self._command["FIWHC"] = self.finwc

    def key_value(self, line: Line) -> KeyValue:
        operands_list: List[str] = line.split_operands()
        operands: List[Tuple[str, Union[Optional[str], List[Tuple[str, Optional[str]]]]]] = list()
        branches: List[str] = list()
        for operand in operands_list:
            key_value = re.split(r"=(?![^()]*[)])", operand)
            if len(key_value) > 1 and key_value[1].startswith("(") and key_value[1].endswith(")"):
                sub_operands = key_value[1][1:-1]
                operands.append((key_value[0], list()))
                for sub_operand in sub_operands.split(","):
                    sub_key_value = sub_operand.split("=")
                    value = sub_key_value[1] if len(sub_key_value) > 1 else None
                    operands[-1][1].append((sub_key_value[0], value))
                    if self.is_branch(value):
                        branches.append(value)
            else:
                value = key_value[1] if len(key_value) > 1 else None
                operands.append((key_value[0], value))
                if self.is_branch(value):
                    branches.append(value)
        return KeyValue(line, operands, branches)

    def finwc(self, line: Line) -> KeyValue:
        finxc = self.key_value(line)
        if len(finxc.keys) >= 2 and self.is_branch(finxc.keys[1]):
            finxc.branches.append(finxc.keys[1])
        return finxc

    def seg_call(self, line: Line) -> SegmentCall:
        entxc = self.key_value(line)
        seg = entxc.keys[0]
        entxc.branches.append(self.root_label(seg))
        return SegmentCall(line, entxc)

    def globz(self, line: Line) -> RegisterData:
        globc = self.key_value(line)
        if globc.keys[0] == "REGR":
            reg = globc.get_value("REGR")
            macro_name = "GLOBAS"
        elif globc.keys[0] == "REGS":
            reg = globc.get_value("REGS")
            macro_name = "GLOBYS"
        elif globc.keys[0] == "REGC":
            reg = globc.get_value("REGC")
            macro_name = "GL0BS"
        else:
            raise RegisterInvalidError(line)
        base = Register(reg)
        if not base.is_valid():
            raise RegisterInvalidError(line)
        self.load_macro(macro_name, base=reg)
        line.command = "LHI"
        return RegisterData(line, base, config.FIXED_MACROS[macro_name])

    def dbred(self, line: Line) -> KeyValue:
        dbred_key = self.key_value(line)
        if dbred_key.get_value("REF") in get_macros() and dbred_key.get_value("REG"):
            self.load_macro(dbred_key.get_value("REF"), base=dbred_key.get_value("REG"))
        for key_number in range(2, 7):
            key_n = f"KEY{key_number}"
            if dbred_key.get_value(key_n) is None:
                break
            field_name = dbred_key.get_sub_value(key_n, "S")
            if not field_name:
                break
            field: FieldBaseDsp = self.field_base_dsp(field_name)
            dbred_key.set_sub_value(field, field_name, key_n, "S")
        return dbred_key

    def pdred(self, line: Line) -> KeyValue:
        pdred_key = self.key_value(line)
        for key_number in range(1, 7):
            key_n = f"SEARCH{key_number}"
            search_value = pdred_key.get_original_value(key_n)
            if search_value is None:
                break
            if not isinstance(search_value, list) or len(search_value) != 2 or search_value[0][0] != "ITMNBR":
                continue
            field_name = search_value[1][0]
            if not self.check(field_name):
                continue
            field: FieldBaseDsp = self.field_base_dsp(field_name)
            updated_search_value = [("ITMNBR", None), (field, None)]
            pdred_key.set_key_value_list(key_value_list=updated_search_value, original_key_value_list=search_value,
                                         key=key_n)
        return pdred_key

    def dbadd(self, line: Line) -> KeyValue:
        dbadd_key: KeyValue = self.key_value(line)
        newlrec_value: str = dbadd_key.get_value("NEWLREC")
        if Register(newlrec_value).is_valid():
            return dbadd_key
        try:
            newlrec_field: FieldBaseDsp = self.field_base_dsp(newlrec_value)
        except Exception:
            raise AssemblyError(line)
        dbadd_key.set_value(newlrec_field, newlrec_value, "NEWLREC")
        return dbadd_key

    def pnamc(self, line: Line) -> KeyValue:
        pnamc_key_value = self.key_value(line)
        field_name = pnamc_key_value.get_value("FIELD")
        if not field_name:
            raise AssemblyError(line)
        pnamc_key_value.set_value(self.field_base_dsp(field_name), field_name, "FIELD")
        return pnamc_key_value

    def date_macro(self, line: Line) -> KeyValue:
        date_key_value = self.key_value(line)
        field_name = date_key_value.get_value("OK")
        if not field_name:
            raise AssemblyError(line)
        date_key_value.set_value(self.field_base_dsp(field_name), field_name, "OK")
        return date_key_value

    def load_macro_from_line(self, line: Line, using: bool) -> None:
        macro_key_value: KeyValue = self.key_value(line)
        macro_name = line.command
        reg = macro_key_value.get_value("REG")
        suffix = macro_key_value.get_value("SUFFIX")
        self.load_macro(macro_name, reg, suffix, using)
        return

    def executable_data_macro(self, line: Line) -> KeyValue:
        node = self.key_value(line)
        self.load_macro(f"_{node.command}")
        return node
