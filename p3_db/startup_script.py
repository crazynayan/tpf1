from flask import g

from p2_assembly.seg6_segment import get_assembled_startup_seg, Segment
from p2_assembly.seg9_collection import seg_collection
from p3_db.response import StandardResponse, RequestType
from p3_db.test_data import TestData
from p4_execution.ex5_execute import TpfServer


class StartupMsg:
    ASSEMBLY_ERROR_PREFIX = "Assembly error at "
    EXECUTION_ERROR_PREFIX = "Execution error at "
    NAME_EMPTY = "Name cannot be left blank."
    NAME_UNIQUE = "Name needs to be unique across all the test data."
    SEG_NOT_FOUND = "Segment is not present in the library."
    STOP_SEG_4_CHAR = "Segment name should be 4 character alpha numeric."
    SUCCESS_CREATE = "Test Data created successfully."
    SUCCESS_UPDATE = "Test Data updated successfully."


def validate_startup_script(rsp: StandardResponse) -> None:
    rsp.body.startup_script = rsp.body.startup_script
    if not rsp.body.startup_script:
        return
    seg: Segment = get_assembled_startup_seg(rsp.body.startup_script)
    error_message: str = str(seg.error_line) or str(seg.error_constant)
    if error_message:
        rsp.error_fields.startup_script = f"{StartupMsg.ASSEMBLY_ERROR_PREFIX}{error_message.strip()}"
        rsp.error = True
        return
    test_data = TestData()
    test_data.startup_script = rsp.body.startup_script
    tpf_server = TpfServer()
    test_data = tpf_server.run("TS14", test_data)
    if test_data.output.dumps:
        rsp.error_fields.startup_script = f"{StartupMsg.EXECUTION_ERROR_PREFIX}{test_data.output.last_node.strip()}"
        rsp.error = True
    return


def validate_test_data_name(rsp: StandardResponse, existing_name: str = str()):
    rsp.body.name = rsp.body.name.strip()
    if not rsp.body.name:
        rsp.error_fields.name = StartupMsg.NAME_EMPTY
        rsp.error = True
        return
    if rsp.body.name == existing_name:
        return
    if TestData.objects.filter_by(name=rsp.body.name).first():
        rsp.error_fields.name = StartupMsg.NAME_UNIQUE
        rsp.error = True
    return


def validate_seg_name(rsp: StandardResponse):
    rsp.body.seg_name = rsp.body.seg_name.upper()
    if not seg_collection.is_seg_present(rsp.body.seg_name):
        rsp.error_fields.seg_name = StartupMsg.SEG_NOT_FOUND
        rsp.error = True
    return


def validate_stop_segments(rsp: StandardResponse):
    stop_segments: str = str(rsp.body.stop_segments)
    rsp.body.stop_segments = [seg.strip().upper() for seg in stop_segments.split(",") if seg.strip()]
    if any(len(seg) != 4 or not seg.isalnum() for seg in rsp.body.stop_segments):
        rsp.error_fields.stop_segments = StartupMsg.STOP_SEG_4_CHAR
        rsp.error = True
    return


def test_data_create(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEST_DATA_CREATE)
    if rsp.error:
        return rsp.dict
    validate_test_data_name(rsp)
    validate_seg_name(rsp)
    validate_stop_segments(rsp)
    validate_startup_script(rsp)
    if rsp.error:
        return rsp.dict
    try:
        rsp.body.owner = g.current_user.email
    except RuntimeError:
        pass
    test_data = TestData.create_from_dict(rsp.body.__dict__)
    rsp.id = test_data.id
    rsp.message = StartupMsg.SUCCESS_CREATE
    return rsp.dict_with_id


def test_data_update(test_data: TestData, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEST_DATA_CREATE)
    if rsp.error:
        return rsp.dict
    validate_test_data_name(rsp, test_data.name)
    validate_seg_name(rsp)
    validate_stop_segments(rsp)
    validate_startup_script(rsp)
    if rsp.error:
        return rsp.dict
    test_data.name = rsp.body.name
    test_data.seg_name = rsp.body.seg_name
    test_data.stop_segments = rsp.body.stop_segments
    test_data.startup_script = rsp.body.startup_script
    test_data.save()
    rsp.message = StartupMsg.SUCCESS_UPDATE
    return rsp.dict
