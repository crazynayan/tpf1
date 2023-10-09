from typing import List, Optional

from munch import Munch

from p2_assembly.seg6_segment import Segment
from p2_assembly.seg9_collection import get_seg_collection
from p3_db.response import StandardResponse, RequestType
from p3_db.test_data import TestData
from p3_db.test_data_get import get_whole_test_data
from p4_execution.ex5_execute import TpfServer
from p4_execution.profiler import SegmentProfiler


def initialize_profiler(rsp: StandardResponse, seg_name: str) -> Optional[SegmentProfiler]:
    if not get_seg_collection().is_seg_present(seg_name):
        rsp.error_fields.seg_name = "Segment not found."
        rsp.error = True
        return None
    segment: Segment = get_seg_collection().get_seg(seg_name)
    segment.assemble()
    assembly_error: str = segment.error_line or segment.error_constant
    if assembly_error:
        rsp.error_fields.seg_name = f"Assembly error. {assembly_error}"
        rsp.error = True
        return None
    profiler: SegmentProfiler = SegmentProfiler(segment.get_instructions())
    return profiler


def extract_test_data(rsp: StandardResponse, test_data_ids: List[str]) -> List[TestData]:
    test_data_list: List[TestData] = list()
    for test_data_id in test_data_ids:
        if not isinstance(test_data_id, str):
            rsp.error_fields.test_data_ids = "Invalid format of Test Data."
            rsp.error = True
            return test_data_list
        test_data: TestData = get_whole_test_data(test_data_id, link=True)
        if not test_data:
            rsp.error_fields.test_data_ids = "Test Data not found."
            rsp.error = True
            return test_data_list
    return test_data_list


def execute_profiler(profiler: SegmentProfiler, test_data_list: List[TestData]) -> None:
    for test_data in test_data_list:
        tpf_server = TpfServer()
        tpf_server.run(test_data.seg_name, test_data, profiler)
    return


def extract_data_from_profiler(profiler: SegmentProfiler) -> Munch:
    return Munch(total_instruction_paths=profiler.total_instruction_paths,
                 covered_instruction_paths=profiler.covered_instruction_paths,
                 documentation_coverage=profiler.documentation_coverage,
                 all_instruction_paths=profiler.get_all_instruction_paths(),
                 missing_instruction_paths=profiler.get_missing_instruction_paths(),
                 total_requirements=profiler.total_requirements,
                 covered_requirements=profiler.covered_requirements,
                 requirement_coverage=profiler.requirement_coverage
                 )


def run_profiler(body: Munch) -> Munch:
    rsp: StandardResponse = StandardResponse(body, RequestType.PROFILER_RUN)
    if rsp.error:
        return rsp.dict_with_data
    profiler: SegmentProfiler = initialize_profiler(rsp, body.seg_name)
    if rsp.error:
        return rsp.dict_with_data
    test_data_list: List[TestData] = extract_test_data(rsp, body.test_data_ids)
    if rsp.error:
        return rsp.dict_with_data
    profiler.set_covered_requirements(sum(test_data.get_total_variation_count() for test_data in test_data_list))
    execute_profiler(profiler, test_data_list)
    rsp.data = extract_data_from_profiler(profiler)
    rsp.data.test_data_list = [Munch(name=test_data.name, id=test_data.id) for test_data in test_data_list]
    rsp.message = "Profiler ran successfully."
    return rsp.dict_with_data
