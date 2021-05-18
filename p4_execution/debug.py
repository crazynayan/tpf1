from typing import Dict, List, Optional

from p2_assembly.seg3_ins_type import InstructionType

INDEX, LINE, HITS, NEXT_HITS, LABEL = "index", "line", "hits", "next_hits", "label"
COMMAND, SEGMENT, OPERANDS = "command", "segment", "operands"


class Trace:
    def __init__(self, node: InstructionType, segment):
        self.index: int = node.index
        self.line: str = str(node)
        self.hits: int = 0
        self.next_hits: Dict[str, int] = {label: 0 for label in node.next_labels}
        self.label: str = node.label
        self.command: str = node.command
        self.segment: str = segment
        self.operands: str = str()
        line_list = str(node).split(":")
        if len(line_list) > 3:
            self.operands = line_list[3]

    def __repr__(self) -> str:
        return f"{self.hits:4} ::{str(self.next_hits):50}:: {self.line}"

    def hit(self, next_label: Optional[str]):
        self.hits += 1
        if next_label in self.next_hits:
            self.next_hits[next_label] += 1

    def is_not_hit(self) -> bool:
        return True if self.hits == 0 or any(next_hit == 0 for _, next_hit in self.next_hits.items()) else False

    def is_hit(self) -> bool:
        return True if self.hits > 0 else False


class Debug:
    def __init__(self):
        self.traces: Dict[str, Trace] = dict()
        self.seg_list: List[str] = list()

    def add_trace(self, nodes: Dict[str, InstructionType], segment: str):
        traces = {label: Trace(node, segment) for label, node in nodes.items()}
        self.traces = {**traces, **self.traces}
        self.seg_list.append(segment)

    def hit(self, node: InstructionType, next_label: Optional[str]) -> None:
        if node.label in self.traces:
            self.traces[node.label].hit(next_label)
            if node.command in ["ENTRC", "BAS"]:
                self.traces[node.label].next_hits[node.fall_down] += 1

    def get_no_hit(self) -> List[Trace]:
        return [trace for _, trace in self.traces.items() if trace.is_not_hit()]

    def get_trace(self) -> List[dict]:
        traces = [{INDEX: trace.index, LINE: trace.line, HITS: trace.hits, NEXT_HITS: trace.next_hits,
                   LABEL: trace.label, COMMAND: trace.command, OPERANDS: trace.operands, SEGMENT: trace.segment}
                  for _, trace in self.traces.items() if trace.is_hit()]
        traces.sort(key=lambda trace_item: (trace_item[SEGMENT], trace_item[INDEX]))
        return traces


def get_debug_loc(traces: List[dict], segment: str) -> int:
    seg_traces = [trace for trace in traces if trace[SEGMENT] == segment]
    return len(seg_traces)
