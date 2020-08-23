from typing import List

from p2_assembly.seg6_segment import segments
from p7_flask_app.api.api0_constants import SEG_NAME, ErrorMsg, NAME, TYPE, Types, NEW_NAME
from p7_flask_app.api.api1_models import TestData
from p7_flask_app.api.api2_validators import validate_empty_str, get_test_data


def create_test_data(data_dict: dict) -> (int, dict):
    errors = dict()
    if validate_empty_str(data_dict, SEG_NAME):
        errors[SEG_NAME] = ErrorMsg.NOT_EMPTY
    elif data_dict[SEG_NAME].upper() not in segments:
        errors[SEG_NAME] = ErrorMsg.SEG_LIBRARY
    errors = {**errors, **validate_new_name(data_dict, NAME)}
    if errors:
        return 400, errors
    input_dict = dict()
    input_dict[NAME] = data_dict[NAME].strip()
    input_dict[TYPE] = Types.INPUT_HEADER
    input_dict[SEG_NAME] = data_dict[SEG_NAME].upper()
    header: dict = TestData.objects.truncate.no_orm.create(input_dict)
    return 200, header


def rename_test_data_name(data_dict: dict) -> (int, dict):
    test_data, errors = get_test_data(data_dict)
    errors = {**errors, **validate_new_name(data_dict, NEW_NAME)}
    if errors:
        return 400, errors
    for element in test_data:
        element[NAME] = data_dict[NEW_NAME].strip()
    saved_data: List[dict] = TestData.objects.no_orm.truncate.save_all(test_data)
    response = next(element for element in saved_data if element[TYPE] == Types.INPUT_HEADER)
    return 200, response


def copy_test_data(data_dict: dict) -> (int, dict):
    test_data, errors = get_test_data(data_dict)
    errors = {**errors, **validate_new_name(data_dict, NEW_NAME)}
    if errors:
        return 400, errors
    for element in test_data:
        element[NAME] = data_dict[NEW_NAME].strip()
    created_data: List[dict] = TestData.objects.no_orm.truncate.create_all(test_data)
    return 200, created_data


def validate_new_name(data: dict, key: str) -> dict:
    # return error_dict if invalid else empty dict
    error = validate_empty_str(data, key)
    if error:
        return error
    elif len(data[key]) > 100:
        return {key: ErrorMsg.LESS_100}
    elif TestData.objects.filter_by(name=data[key], type=Types.INPUT_HEADER).first():
        return {key: ErrorMsg.UNIQUE}
    return dict()
