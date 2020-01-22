import re
from typing import List, Tuple, Union, Optional

from assembly.seg2_ins_operand import FieldBaseDsp
from assembly.seg3_ins_type import InstructionGeneric, RegisterData
from assembly.seg4_ins_implementation import InstructionImplementation
from config import config
from utils.data_type import Register
from utils.errors import RegisterInvalidError
from utils.file_line import Line


class KeyValue(InstructionGeneric):

    def __init__(self, line: Line,
                 operands: List[Tuple[str, Union[Optional[str], List[Tuple[str, Optional[str]]]]]],
                 branches: List[str]):
        super().__init__(line)
        self._operands: List[Tuple[str, Union[Optional[str], List[Tuple[str, Optional[str]]]]]] = operands
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

    def get_value(self, key: str) -> Union[Optional[str], List[Tuple[str, Union[Optional[str], FieldBaseDsp]]]]:
        # Returns
        # None - For key not found
        # value: str - For KEY=VALUE
        # List[sub_key] - For KEY=(SUB_KEY1, SUB_KEY2)
        # List[Tuple[sub_key, sub_value]] - For KEY=(SUB_KEY1=SUB_VALUE1, SUB_KEY2=SUB_VALUE2)
        value = next((key_value[1] for key_value in self._operands if key_value[0] == key), None)
        if isinstance(value, list) and all(sub_key_value[1] is None for sub_key_value in value):
            value = [sub_key_value[0] for sub_key_value in value]
        return value

    def get_sub_value(self, key: str, sub_key: str) -> Union[Optional[str], FieldBaseDsp]:
        return next((sub_key_value[1] for key_value in self.sub_key_value for sub_key_value in key_value[1]
                     if key_value[0] == key and sub_key_value[0] == sub_key), None)

    def set_sub_value(self, value: FieldBaseDsp, original_value: str, key: str, sub_key: str) -> None:
        key_value_list = self.get_value(key)
        key_value_list.remove((sub_key, original_value))
        key_value_list.append((sub_key, value))


class SegmentCall(KeyValue):

    def __init__(self, line, key_value: KeyValue):
        super().__init__(line, key_value._operands, key_value.branches)


class RealtimeMacroImplementation(InstructionImplementation):
    def __init__(self, name: str):
        super().__init__(name)
        self._command['ENTRC'] = self.seg_call
        self._command['ENTNC'] = self.seg_call
        self._command['ENTDC'] = self.seg_call
        self._command['BACKC'] = self.instruction_generic
        self._command['EXITC'] = self.instruction_generic
        self._command['GETCC'] = self.key_value
        self._command['LEVTA'] = self.key_value
        self._command['RELCC'] = self.key_value
        self._command['RCUNC'] = self.key_value
        self._command['RELFC'] = self.key_value
        self._command['RLCHA'] = self.key_value
        self._command['CRUSA'] = self.key_value
        self._command['DETAC'] = self.key_value
        self._command['ATTAC'] = self.key_value
        self._command['MODEC'] = self.key_value
        self._command['GLOBZ'] = self.globz
        self._command['FACE'] = self.instruction_generic
        self._command['FINWC'] = self.key_value
        self._command['SYSRA'] = self.key_value
        self._command['SERRC'] = self.key_value
        self._command['SENDA'] = self.key_value
        self._command['DBOPN'] = self.key_value
        self._command['DBRED'] = self.dbred
        self._command['DBCLS'] = self.key_value
        self._command['DBIFB'] = self.key_value

    def key_value(self, line: Line) -> KeyValue:
        operands_list: List[str] = line.split_operands()
        operands: List[Tuple[str, Union[Optional[str], List[Tuple[str, Optional[str]]]]]] = list()
        branches: List[str] = list()
        for operand in operands_list:
            key_value = re.split(r"=(?![^()]*[)])", operand)
            if len(key_value) > 1 and key_value[1].startswith('(') and key_value[1].endswith(')'):
                sub_operands = key_value[1][1:-1]
                operands.append((key_value[0], list()))
                for sub_operand in sub_operands.split(','):
                    sub_key_value = sub_operand.split('=')
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

    def seg_call(self, line: Line) -> SegmentCall:
        entxc = self.key_value(line)
        seg = entxc.keys[0]
        entxc.branches.append(self.root_label(seg))
        return SegmentCall(line, entxc)

    def globz(self, line: Line) -> RegisterData:
        globc = self.key_value(line)
        reg = globc.get_value('REGR')
        reg = reg or globc.get_value('REGS')
        base = Register(reg)
        if not base.is_valid():
            raise RegisterInvalidError
        self.load_macro('GLOBAL', base=reg)
        line.command = 'LHI'
        return RegisterData(line, base, config.GLOBAL)

    def dbred(self, line: Line) -> KeyValue:
        dbred_key = self.key_value(line)
        for key_number in range(2, 7):
            key_n = f"KEY{key_number}"
            if dbred_key.get_value(key_n) is None:
                break
            field_name = dbred_key.get_sub_value(key_n, 'S')
            if not field_name:
                break
            field: FieldBaseDsp = self.field_base_dsp(field_name)
            dbred_key.set_sub_value(field, field_name, key_n, 'S')
        return dbred_key

    def load_macro_from_line(self, line: Line) -> None:
        macro_key_value: KeyValue = self.key_value(line)
        macro_name = line.command
        reg = macro_key_value.get_value('REG')
        suffix = macro_key_value.get_value('SUFFIX')
        self.load_macro(macro_name, reg, suffix)
        return


class UserDefinedMacroImplementation(RealtimeMacroImplementation):
    def __init__(self, name: str):
        super().__init__(name)
        self._command['AAGET'] = self.key_value
        self._command['PNRCC'] = self.key_value
        self._command['PDRED'] = self.key_value
        self._command['PDCLS'] = self.key_value
        self._command['CFCMA'] = self.key_value
        self._command['HEAPA'] = self.key_value
        self._command['EHEAPA'] = self.key_value
        self._command['LOCAA'] = self.key_value
        # Tool specific commands
        self._command['ERROR_CHECK'] = self.key_value
        self._command['PARS_DATE'] = self.key_value
