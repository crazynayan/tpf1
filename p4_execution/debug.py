from typing import Dict, List, Optional

from p2_assembly.seg3_ins_type import InstructionType

INDEX, LINE, HITS, NEXT_HITS, LABEL = "index", "line", "hits", "next_hits", "label"
COMMAND, SEGMENT, OPERANDS = "command", "segment", "operands"


def get_label(label: str, segment: str) -> str:
    return f"{segment}-{label}"


class Trace:
    def __init__(self, node: InstructionType, segment: str):
        self.index: int = node.index
        self.line: str = str(node)
        self.hits: int = 0
        self.next_hits: Dict[str, int] = {get_label(label, segment): 0 for label in node.next_labels}
        self.label: str = get_label(node.label, segment)
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
        traces = {f"{segment}-{label}": Trace(node, segment) for label, node in nodes.items()}
        self.traces = {**traces, **self.traces}
        self.seg_list.append(segment)

    def hit(self, node: InstructionType, next_label: str, segment: str) -> None:
        next_seg_label = get_label(next_label, segment)
        node_label = get_label(node.label, segment)
        fall_down_label = get_label(node.fall_down, segment)
        if node_label in self.traces:
            self.traces[node_label].hit(next_seg_label)
            if node.command in ["ENTRC", "BAS"]:
                self.traces[node_label].next_hits[fall_down_label] += 1

    def get_no_hit(self) -> List[Trace]:
        return [trace for _, trace in self.traces.items() if trace.is_not_hit()]

    def get_hit(self) -> List[Trace]:
        return [trace for _, trace in self.traces.items() if trace.is_hit()]

    def get_traces(self, hit: Optional[bool] = None) -> List[dict]:
        if hit is True:
            traces: List[Trace] = self.get_hit()
        elif hit is False:
            traces: List[Trace] = self.get_no_hit()
        else:
            traces: List[Trace] = [trace for _, trace in self.traces.items()]
        trace_list: List[dict] = [{INDEX: trace.index, LINE: trace.line, HITS: trace.hits, NEXT_HITS: trace.next_hits,
                                   LABEL: trace.label, COMMAND: trace.command, OPERANDS: trace.operands,
                                   SEGMENT: trace.segment} for trace in traces]
        trace_list.sort(key=lambda trace_item: (trace_item[SEGMENT], trace_item[INDEX]))
        return trace_list


def get_debug_loc(traces: dict, segment: str) -> int:
    return len(traces[segment]) if segment in traces else 0


def add_debug_loc(traces: Dict[str, set], traces_to_add: list):
    for trace in traces_to_add:
        if trace[SEGMENT] not in traces:
            traces[trace[SEGMENT]] = set()
        traces[trace[SEGMENT]].add(trace[LABEL])
    return


def get_missed_loc(traces_missed: Dict[str, set], traces_hit: Dict[str, set], segment: str):
    if segment not in traces_missed:
        return
    hit_set: set = traces_hit[segment] if segment in traces_hit else set()
    missed_set = traces_missed[segment] - hit_set
    return len(missed_set)
