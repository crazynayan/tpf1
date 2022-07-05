from typing import List

from flask import g
from munch import Munch

from p2_assembly.seg9_collection import seg_collection
from p3_db.response import StandardResponse, RequestType, StandardGetResponse
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
    if not seg_collection.is_seg_present(test_data.seg_name):
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
    TestResult.objects.truncate.create_all(TestResult.objects.to_dicts(test_results))
    rsp.message = "Test Result saved successfully."
    return rsp.dict


def get_test_results(name: str) -> dict:
    kwargs: dict = {"name": name} if name else {"type": TestResult.HEADER}
    test_results: List[TestResult] = TestResult.objects.filter_by(**kwargs).get()
    test_results.sort(key=lambda result: (result.type, result.result_id, result.variation, result.ecb_level,
                                          result.heap_name, result.macro_name, result.global_name,
                                          result.locator, result.key, result.owner, result.name))
    results: Munch = Munch.fromDict({"headers": [result.trunc_to_dict() for result in test_results]})
    if not name:
        return results.toDict()
    results.counters = Munch()
    results.counters.dumps = sum(1 for result in test_results if result.type == TestResult.RESULT and result.dumps)
    results.counters.messages = sum(1 for result in test_results if result.type == TestResult.RESULT
                                    and result.messages)
    results.counters.core_variations = len(set(result.variation for result in test_results
                                               if result.type == TestResult.CORE))
    results.counters.pnr_variations = len(set(result.variation for result in test_results
                                              if result.type == TestResult.PNR))
    results.counters.tpfdf_variations = len(set(result.variation for result in test_results
                                                if result.type == TestResult.TPFDF))
    results.counters.file_variations = len(set(result.variation for result in test_results
                                               if result.type == TestResult.FILE))
    results.cores = [result for result in results.headers if result.type == TestResult.CORE]
    results.pnr = [result for result in results.headers if result.type == TestResult.PNR]
    results.tpfdf = [result for result in results.headers if result.type == TestResult.TPFDF]
    results.files = [result for result in results.headers if result.type == TestResult.FILE]
    results.results = [result for result in results.headers if result.type == TestResult.RESULT]
    results.headers = [result for result in results.headers if result.type == TestResult.HEADER]
    return results.toDict()


def get_test_result(test_result_id: str) -> dict:
    rsp = StandardGetResponse()
    test_result: TestResult = TestResult.get_by_id(test_result_id)
    if not test_result:
        rsp.error = True
        rsp.message = "Test Result not found."
        return rsp.dict
    tr_core_field_data = ", ".join([f"{field['field']}:{field['data']}" for field in test_result.core_field_data])
    tr_pnr_field_data = ", ".join([f"{field['field']}:{field['data']}" for field in test_result.pnr_field_data])
    rsp.data.append(test_result.trunc_to_dict())
    rsp.data[0]["core_field_data"] = tr_core_field_data
    rsp.data[0]["pnr_field_data"] = tr_pnr_field_data
    return rsp.dict


def update_comment(test_result_id: str, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.RESULT_COMMENT_UPDATE)
    if rsp.error:
        return rsp.dict
    if not TestResult.is_comment_type_valid(rsp.body.comment_type):
        rsp.error_fields.comment_type = "Invalid comment type."
        rsp.error = True
    result: TestResult = TestResult.get_by_id(test_result_id)
    if not result:
        rsp.message = "Saved result not found for this variation."
        rsp.error = True
    elif result.owner != g.current_user.email:
        rsp.message = "Unauthorized to update this test result."
        rsp.error = True
    if rsp.error:
        return rsp.dict
    result.set_comment(rsp.body.comment, rsp.body.comment_type)
    result.save()
    rsp.message = "Comment updated successfully."
    return rsp.dict


def delete_test_result(name: str) -> dict:
    rsp: StandardResponse = StandardResponse()
    delete_name = name.strip()
    result: TestResult = TestResult.objects.filter_by(name=delete_name, type=TestResult.HEADER).first()
    if not result:
        rsp.message = "Test Result with this name not found."
        rsp.error = True
        return rsp.dict
    if result.owner != g.current_user.email:
        rsp.message = "Unauthorized to delete this test result."
        rsp.error = True
        return rsp.dict
    TestResult.objects.filter_by(name=delete_name).delete()
    rsp.message = "Test Result deleted successfully."
    return rsp.dict
