from typing import List

from munch import Munch

from config import config
from p1_utils.errors import ProfilerError
from p2_assembly.seg3_ins_type import InstructionType


class InstructionPath:

    def __init__(self, instruction: InstructionType, next_label: str):
        self.hit_counter: int = int()
        self.index: int = instruction.index
        self.label: str = instruction.label
        self.command: str = instruction.command
        self.operand: str = instruction.get_operand_string()
        self.next_label: str = next_label

    def __repr__(self):
        return f"{self.label:10}:{self.command:6}:{self.next_label:10}:{self.hit_counter}:{self.operand}"

    def is_hit(self) -> bool:
        return self.hit_counter > 0

    def is_equal(self, label: str, next_label: str) -> bool:
        return self.label == label and self.next_label == next_label

    def increment_hit_counter(self) -> None:
        self.hit_counter += 1


def convert_instructions_to_instruction_paths(instructions: List[InstructionType]) -> List[InstructionPath]:
    instruction_paths: List[InstructionPath] = list()
    for instruction in instructions:
        if len(instruction.next_labels) == 0:
            instruction_path: InstructionPath = InstructionPath(instruction, str())
            instruction_paths.append(instruction_path)
        else:
            instruction_paths.extend([InstructionPath(instruction, next_label) for next_label in instruction.next_labels])
    return instruction_paths


class SegmentProfiler:

    def __init__(self, instructions: List[InstructionType]):
        if len(instructions) == 0:
            raise ProfilerError
        self.instruction_paths: List[InstructionPath] = convert_instructions_to_instruction_paths(instructions)
        self.initial_label: str = instructions[0].label

    @property
    def total_instruction_paths(self) -> int:
        return len(self.instruction_paths)

    @property
    def covered_instruction_paths(self) -> int:
        return sum(1 for instruction_path in self.instruction_paths if instruction_path.is_hit())

    @property
    def documentation_coverage(self) -> str:
        return f"{round(self.covered_instruction_paths * 100 / self.total_instruction_paths)}%"

    def hit(self, instruction: InstructionType, default_next_label: str) -> None:
        next_label: str = default_next_label if default_next_label else str()
        instruction_path: InstructionPath = next((instruction_path for instruction_path in self.instruction_paths
                                                  if instruction_path.is_equal(instruction.label, next_label)), None)
        if instruction_path:
            instruction_path.increment_hit_counter()
        if instruction.command in config.CALL_AND_RETURN:
            instruction_path: InstructionPath = next((instruction_path for instruction_path in self.instruction_paths
                                                      if instruction_path.is_equal(instruction.label, instruction.fall_down)), None)
            if instruction_path:
                instruction_path.increment_hit_counter()
        return

    def get_all_instruction_paths(self) -> List[Munch]:
        return [Munch(instruction_path.__dict__) for instruction_path in self.instruction_paths]

    def get_missing_instruction_paths(self) -> List[Munch]:
        return [Munch(instruction_path.__dict__) for instruction_path in self.instruction_paths if not instruction_path.is_hit()]
