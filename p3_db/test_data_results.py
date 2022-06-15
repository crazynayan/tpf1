from typing import List

from p3_db.response import StandardResponse, RequestType
from p3_db.test_data import TestData
from p3_db.test_data_elements import Result


def create_results(test_data: TestData):
    results: List[Result] = [Result(test_data.id, output) for output in test_data.outputs]
    Result.objects.create_all(Result.objects.to_dicts(results))
    return


def merge_test_data_with_results(test_data: TestData):
    results: List[Result] = Result.objects.filter_by(test_data_id=test_data.id).get()
    results.sort(key=lambda item: item.result_id)
    test_data.saved_results = Result.objects.to_dicts(results)
    for result in test_data.saved_results:
        result["pnr_fields"] = [pnr["field"] for pnr in result["pnr_field_data"]]
        result["core_fields"] = [core["field"] for core in result["core_field_data"]]
    return


def update_comment(test_data_id: str, result_id: int, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.RESULT_COMMENT_UPDATE)
    if rsp.error:
        return rsp.dict
    result: Result = Result.objects.filter_by(test_data_id=test_data_id, result_id=result_id).first()
    if not result:
        rsp.error_fields.test_data_id = "Saved result not found for this variation."
        rsp.error_fields.result_id = rsp.error_fields.test_data_id
        rsp.error = True
    if not Result.is_comment_type_valid(rsp.body.comment_type):
        rsp.error_fields.comment_type = "Invalid comment type."
        rsp.error = True
    if rsp.error:
        return rsp.dict
    result.set_comment(rsp.body.comment, rsp.body.comment_type)
    result.save()
    rsp.message = "Comment updated successfully."
    return rsp.dict
