from typing import List

from p3_db.response import StandardResponse, RequestType
from p3_db.test_data import TestData
from p3_db.test_result_model import TestResult


def create_test_result(test_data: TestData, body: dict):
    rsp: StandardResponse = StandardResponse(body, RequestType.RESULT_CREATE)
    if rsp.error:
        return rsp.dict
    rsp.body.name = rsp.body.name.strip()
    if not rsp.body.name:
        rsp.error_fields.name = "Name of the Test Result cannot be blank."
        rsp.error = True
        return rsp.dict
    if TestResult.objects.filter_by(name=rsp.body.name).first():
        rsp.error_fields.name = "Test Result with the same name is already saved. Use unique name."
        rsp.error = True
        return rsp.dict
    test_results: List[TestResult] = list()
    test_results.append(TestResult(name=rsp.body.name, test_data=test_data))
    test_results.extend([TestResult(name=rsp.body.name, core=core) for core in test_data.cores])
    test_results.extend([TestResult(name=rsp.body.name, pnr=pnr) for pnr in test_data.pnr])
    test_results.extend([TestResult(name=rsp.body.name, tpfdf=tpfdf) for tpfdf in test_data.tpfdf])
    test_results.extend([TestResult(name=rsp.body.name, file=file) for file in test_data.fixed_files])
    test_results.extend([TestResult(name=rsp.body.name, output=output) for output in test_data.outputs])
    TestResult.objects.create_all(TestResult.objects.to_dicts(test_results))
    rsp.message = "Test Result saved successfully."
    return rsp.dict


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
