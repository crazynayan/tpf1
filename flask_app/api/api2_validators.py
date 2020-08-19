from typing import Tuple, List

from assembly.mac2_data_macro import indexed_macros, macros
from config import config
from flask_app.api.api0_constants import ErrorMsg, Types, FIELD_DATA, FIELD, NAME, MACRO_NAME, TYPE, \
    VARIATION_NAME, NEW_VARIATION_NAME, VARIATION
from flask_app.api.api1_models import TestData


def validate_empty_str(data: dict, key: str) -> dict:
    # return error dict if key is empty else empty dict
    if not (isinstance(data, dict) and isinstance(key, str) and data and data.get(key, None) and
            isinstance(data[key], str) and data[key].strip() != str()):
        return {key: ErrorMsg.NOT_EMPTY}
    return dict()


def validate_empty_list(data: dict, key: str) -> dict:
    if not (isinstance(data, dict) and isinstance(key, str) and data and data.get(key, None) and
            isinstance(data[key], list) and data[key] != list()):
        return {key: ErrorMsg.NOT_EMPTY}
    return dict()


def get_test_data(data_dict: dict, data_type: str = str()) -> Tuple[List[dict], dict]:
    # if test data is found then return list of dict, empty error dict else return empty list, error dict
    error = validate_empty_str(data_dict, NAME)
    if error:
        return list(), error
    types = [Types.INPUT_HEADER, data_type] if data_type else [Types.INPUT_HEADER]
    query = TestData.objects.no_orm.truncate.filter_by(name=data_dict[NAME].strip())
    test_data = query.filter("type", TestData.objects.IN, types).get()
    if not test_data:
        return list(), {NAME: ErrorMsg.NOT_FOUND}
    if data_type:
        test_data = [element for element in test_data if element[TYPE] == data_type]
    return test_data, dict()


def get_macro_name(data_dict: dict) -> str:
    if validate_empty_list(data_dict, FIELD_DATA):
        return str()
    for field in data_dict[FIELD_DATA]:
        if not validate_empty_str(field, FIELD) and field[FIELD].strip().upper() in indexed_macros:
            return indexed_macros[field[FIELD].strip().upper()]
    return str()


def validate_macro_name(data_dict: dict, test_data: List[dict]) -> dict:
    error = validate_empty_str(data_dict, MACRO_NAME)
    if error:
        return error
    if data_dict[MACRO_NAME].strip().upper() not in macros:
        return {MACRO_NAME: ErrorMsg.MACRO_LIBRARY}
    if not any(element[MACRO_NAME] == data_dict[MACRO_NAME] for element in test_data):
        return {MACRO_NAME: ErrorMsg.NOT_FOUND}
    return dict()


def get_variation(data_dict: dict, test_data: List[dict]) -> Tuple[str, int]:
    if NEW_VARIATION_NAME in data_dict:
        variation_name = data_dict[NEW_VARIATION_NAME]
        variation = max(element[VARIATION] for element in test_data) + 1 if test_data else 1
    else:
        variation_name = data_dict.get(VARIATION_NAME, None) or config.DEFAULT_VARIATION_NAME
        variation = next((element[VARIATION] for element in test_data if element[VARIATION_NAME] == variation_name), 1)
    return variation_name, variation


def validate_variation(data_dict: dict, test_data: List[dict]) -> dict:
    errors = dict()
    if NEW_VARIATION_NAME in data_dict:
        if len(data_dict[NEW_VARIATION_NAME]) > 100:
            errors[NEW_VARIATION_NAME] = ErrorMsg.LESS_100
        if any(element[VARIATION_NAME] == data_dict[NEW_VARIATION_NAME] for element in test_data):
            errors[NEW_VARIATION_NAME] = ErrorMsg.UNIQUE
        if VARIATION_NAME in data_dict:
            errors[NEW_VARIATION_NAME] = ErrorMsg.VARIATION_NAME
            errors[VARIATION_NAME] = ErrorMsg.VARIATION_NAME
        return errors
    if VARIATION_NAME in data_dict:
        if len(data_dict[VARIATION_NAME]) > 100:
            errors[VARIATION_NAME] = ErrorMsg.LESS_100
        if not any(element[VARIATION_NAME] == data_dict[NEW_VARIATION_NAME] for element in test_data):
            errors[VARIATION_NAME] = ErrorMsg.NOT_FOUND
        return errors
    if test_data and not any(element[VARIATION_NAME] == config.DEFAULT_VARIATION_NAME for element in test_data):
        errors[VARIATION_NAME] = ErrorMsg.NOT_EMPTY
    return errors
