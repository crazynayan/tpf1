from typing import List, Optional

from munch import Munch

from d21_backend.p2_assembly.seg6_segment import Segment
from d21_backend.p2_assembly.seg9_collection import get_seg_collection
from d21_backend.p3_db.response import StandardResponse, RequestType
from d21_backend.p3_db.startup_script import validate_seg_name
from d21_backend.p3_db.test_data import TestData
from d21_backend.p3_db.test_data_get import get_whole_test_data
from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p4_execution.profiler import SegmentProfiler


def initialize_profiler(rsp: StandardResponse) -> Optional[SegmentProfiler]:
    validate_seg_name(rsp)
    if rsp.error:
        return None
    segment: Segment = get_seg_collection().get_seg(rsp.body.seg_name)
    segment.assemble()
    assembly_error: str = segment.error_line or segment.error_constant
    if assembly_error:
        rsp.error_fields.seg_name = f"Assembly error. {assembly_error}"
        rsp.error = True
        return None
    profiler: SegmentProfiler = SegmentProfiler(segment.get_instructions())
    return profiler


def extract_test_data(rsp: StandardResponse) -> List[TestData]:
    if not rsp.body.test_data_ids:
        rsp.error_fields.test_data_ids = "At least one test data is required."
        rsp.error = True
        return list()
    test_data_list: List[TestData] = list()
    for test_data_id in rsp.body.test_data_ids:
        if not isinstance(test_data_id, str):
            rsp.error_fields.test_data_ids = "Invalid format of Test Data."
            rsp.error = True
            return test_data_list
        test_data: TestData = get_whole_test_data(test_data_id, link=True)
        if not test_data:
            rsp.error_fields.test_data_ids = "Test Data not found."
            rsp.error = True
            return test_data_list
        test_data_list.append(test_data)
    return test_data_list


def execute_profiler(profiler: SegmentProfiler, test_data_list: List[TestData]) -> None:
    for test_data in test_data_list:
        tpf_server = TpfServer()
        tpf_server.run(test_data.seg_name, test_data, profiler)
    return


def extract_data_from_profiler(profiler: SegmentProfiler) -> Munch:
    all_instruction_paths: List[Munch] = sorted(profiler.get_all_instruction_paths(), key=lambda item: item.index)
    missing_instruction_paths: List[Munch] = sorted(profiler.get_missing_instruction_paths(), key=lambda item: item.index)
    return Munch(total_instruction_paths=profiler.total_instruction_paths,
                 covered_instruction_paths=profiler.covered_instruction_paths,
                 documentation_coverage=profiler.documentation_coverage,
                 all_instruction_paths=all_instruction_paths,
                 missing_instruction_paths=missing_instruction_paths,
                 )


def run_profiler(body: Munch) -> Munch:
    rsp: StandardResponse = StandardResponse(body, RequestType.PROFILER_RUN)
    if rsp.error:
        return rsp.dict_with_data
    profiler: SegmentProfiler = initialize_profiler(rsp)
    if rsp.error:
        return rsp.dict_with_data
    test_data_list: List[TestData] = extract_test_data(rsp)
    if rsp.error:
        return rsp.dict_with_data
    execute_profiler(profiler, test_data_list)
    rsp.data = extract_data_from_profiler(profiler)
    rsp.data.test_data_list = [Munch(name=test_data.name, id=test_data.id) for test_data in test_data_list]
    rsp.message = "Profiler ran successfully."
    return rsp.dict_with_data
