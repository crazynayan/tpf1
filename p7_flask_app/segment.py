from typing import Optional

from config import config
from p1_utils.domain import get_domain
from p2_assembly.seg6_segment import Segment
from p2_assembly.seg8_listing import LstCmd
from p2_assembly.seg9_collection import SegLst, get_seg_collection
from p4_execution.ex5_execute import TpfServer


def reset_seg_assembly(blob_name: str, file_type) -> Optional[SegLst]:
    seg_collection = get_seg_collection()
    seg_name = seg_collection.init_from_cloud(blob_name, file_type)
    segment = seg_collection.get_seg(seg_name)
    if not segment:
        return None
    if file_type == config.LST:
        LstCmd.objects.filter_by(seg_name=seg_name).delete()
    SegLst.objects.filter_by(seg_name=seg_name).delete()
    seg: SegLst = get_seg_lst(segment)  # Assemble the segment and create LstCmd
    seg.create()
    return seg


def get_seg_lst(segment: Segment) -> SegLst:
    seg_lst = SegLst()
    seg_lst.seg_name = segment.seg_name
    seg_lst.filename = segment.file_name
    seg_lst.file_type = segment.file_type
    seg_lst.source = segment.source
    seg_lst.blob_name = segment.blob_name
    seg_lst.domain = get_domain()
    segment.assemble()
    seg_lst.error_line = str(segment.error_line)
    seg_lst.error_constant = segment.error_constant
    seg_lst.loc = len(segment.nodes)
    unsupported_nodes = [node for _, node in segment.nodes.items()
                         if node.command not in TpfServer().supported_commands]
    seg_lst.error_count = len(unsupported_nodes)
    seg_lst.error_cmds = list({node.command for node in unsupported_nodes})
    return seg_lst
