from typing import Dict, List, Optional

from assembly.instruction_type import InstructionType


class Trace:
    def __init__(self, node: InstructionType):
        self.index: int = node.index
        self.line: str = str(node)
        self.hits: int = 0
        self.next_hits: Dict[str, int] = {label: 0 for label in node.next_labels}

    def __repr__(self) -> str:
        return f"{self.hits:4} ::{str(self.next_hits):50}:: {self.line}"

    def hit(self, next_label: Optional[str]):
        self.hits += 1
        if next_label in self.next_hits:
            self.next_hits[next_label] += 1

    def is_not_hit(self) -> bool:
        return True if self.hits == 0 or any(next_hit == 0 for _, next_hit in self.next_hits.items()) else False


class Debug:
    def __init__(self):
        self.traces: Dict[Trace] = dict()
        self.seg_list: List[str] = list()

    def init_trace(self, nodes: Dict[str, InstructionType], seg_list: List[str]):
        self.traces: Dict[Trace] = {label: Trace(node) for label, node in nodes.items()}
        self.seg_list = seg_list

    def hit(self, node: InstructionType, next_label: Optional[str]) -> None:
        if node.label in self.traces:
            self.traces[node.label].hit(next_label)
            if node.command in ['ENTRC', 'BAS']:
                self.traces[node.label].next_hits[node.fall_down] += 1

    def get_no_hit(self) -> List[Trace]:
        return [trace for _, trace in self.traces.items() if trace.is_not_hit()]
