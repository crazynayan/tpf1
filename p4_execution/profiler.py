from typing import List

import networkx as nx
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
    instruction_paths: List[InstructionPath] = [InstructionPath(instruction, next_label) for instruction in instructions
                                                for next_label in instruction.next_labels]
    return instruction_paths


def create_graph(instructions: List[InstructionType]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for instruction in instructions:
        graph.add_node(instruction.label)
    for instruction in instructions:
        if instruction.command.startswith("ENT") and instruction.fall_down:
            graph.add_edge(instruction.label, instruction.fall_down)
        else:
            for next_label in instruction.next_labels:
                graph.add_edge(instruction.label, next_label)
    return graph


def get_requirements(graph: nx.DiGraph, source: str) -> int:
    end_nodes: List[str] = [node for node in graph.nodes if len(list(graph.successors(node))) == 0]
    requirements = list(nx.all_simple_paths(graph, source=source, target=end_nodes))
    return len(requirements)

class SegmentProfiler:

    def __init__(self, instructions: List[InstructionType]):
        if len(instructions) == 0:
            raise ProfilerError
        self.instruction_paths: List[InstructionPath] = convert_instructions_to_instruction_paths(instructions)
        self.graph: nx.DiGraph = create_graph(instructions)
        self.source_label: str = instructions[0].label


    @property
    def total_instruction_paths(self) -> int:
        return len(self.instruction_paths)

    @property
    def covered_instruction_paths(self) -> int:
        return sum(1 for instruction_path in self.instruction_paths if instruction_path.is_hit())

    @property
    def documentation_coverage(self) -> str:
        return f"{round(self.covered_instruction_paths * 100 / self.total_instruction_paths)}%"

    def get_total_requirements(self) -> int:
        return get_requirements(self.graph, self.source_label)

    def get_covered_requirements(self) -> int:
        covered_graph: nx.DiGraph = nx.DiGraph(self.graph)
        missing_paths: List[Munch] = self.get_missing_instruction_paths()
        for path in missing_paths:
            covered_graph.remove_edge(path.label, path.next_label)
        return get_requirements(covered_graph, self.source_label)

    @property
    def requirement_coverage(self) -> str:
        return f"{round(self.get_covered_requirements() * 100 / self.get_total_requirements())}%"

    def hit(self, instruction: InstructionType, next_label) -> None:
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

