from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from typing import List

from d21_backend.p3_db.response import StandardResponse, RequestType
from d21_backend.p3_db.test_data import TestData, VALID_ELEMENT_TYPES


def validate_and_get_variation(test_data: TestData, variation: int, v_type: str, rsp: StandardResponse) -> list:
    if v_type not in VALID_ELEMENT_TYPES:
        rsp.message = f"Invalid variation type."
        rsp.error = True
        return list()
    td_elements = [td_element for td_element in test_data.ref(v_type) if td_element.variation == variation]
    if not td_elements:
        rsp.message = f"Variation not found in test data."
        rsp.error = True
    return td_elements


def rename_variation(test_data: TestData, variation: int, v_type: str, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.VARIATION)
    if rsp.error:
        return rsp.dict
    td_elements = validate_and_get_variation(test_data, variation, v_type, rsp)
    if rsp.error:
        return rsp.dict
    if not rsp.body.new_name.strip():
        rsp.body.new_name = f"Variation {td_elements[0].variation + 1}"
    for td_element in td_elements:
        td_element.variation_name = rsp.body.new_name
    td_elements[0].__class__.objects.save_all(td_elements)
    rsp.message = "Variation renamed successfully."
    return rsp.dict


def delete_variation(test_data: TestData, variation: int, v_type: str) -> dict:
    rsp = StandardResponse()
    td_elements = validate_and_get_variation(test_data, variation, v_type, rsp)
    if rsp.error:
        return rsp.dict
    for td_element in td_elements:
        test_data.ref(v_type).remove(td_element)
    with ThreadPoolExecutor(max_workers=len(td_elements)) as executor:
        threads = {executor.submit(td_element.delete) for td_element in td_elements}
        [future.result() for future in as_completed(threads)]
    test_data.save()
    rsp.message = "Variation deleted successfully."
    return rsp.dict


def copy_variation(test_data: TestData, variation: int, v_type: str, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.VARIATION)
    if rsp.error:
        return rsp.dict
    td_elements = validate_and_get_variation(test_data, variation, v_type, rsp)
    if rsp.error:
        return rsp.dict
    new_td_elements = deepcopy(td_elements)
    new_variation = max(td_element.variation for td_element in test_data.ref(v_type)) + 1
    if not rsp.body.new_name.strip():
        rsp.body.new_name = f"Variation {new_variation + 1}"
    for td_element in new_td_elements:
        td_element.variation = new_variation
        td_element.variation_name = rsp.body.new_name
    td_dict_elements: List[dict] = td_elements[0].__class__.objects.to_dicts(new_td_elements)
    created_td_elements = td_elements[0].__class__.objects.create_all(td_dict_elements)
    test_data.ref(v_type).extend(created_td_elements)
    test_data.save()
    rsp.message = "Variation copied successfully."
    return rsp.dict
