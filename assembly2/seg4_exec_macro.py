import re
from typing import List, Tuple, Union, Optional

from assembly2.seg3_instruction import InstructionImplementation, InstructionGeneric
from utils.file_line import Line


class KeyValue(InstructionGeneric):

    def __init__(self, line: Line, operands: List[Tuple[str, Union[Optional[str], List[Tuple[str, Optional[str]]]]]],
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

    def get_value(self, key: str) -> Union[Optional[str], List[Tuple[str, Optional[str]]]]:
        # Returns
        # None - For key not found
        # value: str - For KEY=VALUE
        # List[sub_key] - For KEY=(SUB_KEY1, SUB_KEY2)
        # List[Tuple[sub_key, sub_value]] - For KEY=(SUB_KEY1=SUB_VALUE1, SUB_KEY2=SUB_VALUE2)
        value = next((key_value[1] for key_value in self._operands if key_value[0] == key), None)
        if isinstance(value, list) and all(sub_key_value[1] is None for sub_key_value in value):
            value = [sub_key_value[0] for sub_key_value in value]
        return value

    def get_sub_value(self, key: str, sub_key: str) -> Optional[str]:
        return next((sub_key_value[1] for key_value in self.sub_key_value for sub_key_value in key_value[1]
                     if key_value[0] == key and sub_key_value[0] == sub_key), None)


class SegmentCall(KeyValue):

    def __init__(self, line, key_value: KeyValue):
        super().__init__(line, key_value._operands, key_value.branches)

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self._operands}"


class ExecutableMacroImplementation(InstructionImplementation):
    def __init__(self, name: str):
        super().__init__(name)
        self._command['ENTRC'] = self.seg_call
        self._command['ENTNC'] = self.seg_call
        self._command['ENTDC'] = self.seg_call

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

    def load_macro_from_line(self, line: Line) -> None:
        macro_key_value: KeyValue = self.key_value(line)
        macro_name = line.command
        reg = macro_key_value.get_value('REG')
        suffix = macro_key_value.get_value('SUFFIX')
        self.load_macro(macro_name, reg, suffix)
        return
