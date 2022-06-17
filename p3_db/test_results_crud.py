from typing import List

from p2_assembly.seg9_collection import seg_collection
from p3_db.response import StandardResponse, RequestType
from p3_db.test_data import TestData
from p3_db.test_result_model import TestResult
from p4_execution.ex5_execute import TpfServer


def create_test_result(test_data: TestData, body: dict):
    rsp: StandardResponse = StandardResponse(body, RequestType.RESULT_CREATE)
    if rsp.error:
        return rsp.dict
    rsp.body.name = rsp.body.name.strip()
    if TestResult.objects.filter_by(name=rsp.body.name).first():
        rsp.error_fields.name = "Test Result with the same name is already saved. Use unique name."
        rsp.error = True
    if not rsp.body.name:
        rsp.error_fields.name = "Name of the Test Result cannot be blank."
        rsp.error = True
    if seg_collection.is_seg_present(test_data.seg_name):
        rsp.message = "The start seg of the test data does not exists. This test data cannot be executed."
        rsp.error = True
    if rsp.error:
        return rsp.dict
    td_result: TestData = TpfServer().run(test_data.seg_name, test_data)
    test_results: List[TestResult] = list()
    test_results.append(TestResult(name=rsp.body.name, test_data=td_result))
    test_results.extend([TestResult(name=rsp.body.name, core=core) for core in td_result.cores])
    test_results.extend([TestResult(name=rsp.body.name, pnr=pnr) for pnr in td_result.pnr])
    test_results.extend([TestResult(name=rsp.body.name, tpfdf=tpfdf) for tpfdf in td_result.tpfdf])
    test_results.extend([TestResult(name=rsp.body.name, file=file) for file in td_result.fixed_files])
    test_results.extend([TestResult(name=rsp.body.name, output=output) for output in td_result.outputs])
    TestResult.objects.create_all(TestResult.objects.to_dicts(test_results))
    rsp.message = "Test Result saved successfully."
    return rsp.dict


def get_test_results(name: str) -> List[dict]:
    if name:
        test_results: List[TestResult] = TestResult.objects.filter_by(name=name).get()
    else:
        test_results: List[TestResult] = TestResult.objects.filter_by(type=TestResult.HEADER).get()
    return [test_result.trunc_to_dict() for test_result in test_results]


def update_comment(test_result_id: str, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.RESULT_COMMENT_UPDATE)
    if rsp.error:
        return rsp.dict
    result: TestResult = TestResult.get_by_id(test_result_id)
    if not result:
        rsp.error_fields.message = "Saved result not found for this variation."
        rsp.error = True
    if not TestResult.is_comment_type_valid(rsp.body.comment_type):
        rsp.error_fields.comment_type = "Invalid comment type."
        rsp.error = True
    if rsp.error:
        return rsp.dict
    result.set_comment(rsp.body.comment, rsp.body.comment_type)
    result.save()
    rsp.message = "Comment updated successfully."
    return rsp.dict


def delete_test_result(name: str) -> dict:
    rsp: StandardResponse = StandardResponse()
    deleted: str = TestResult.objects.filter_by(name=name.strip()).delete()
    if deleted:
        rsp.message = "Test Result deleted successfully."
    else:
        rsp.message = "Test Result with this name not found."
        rsp.error = True
    return rsp.dict
