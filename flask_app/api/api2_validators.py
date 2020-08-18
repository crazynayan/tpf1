from typing import Tuple, List

from assembly.mac2_data_macro import indexed_macros, macros
from flask_app.api.api0_constants import ErrorMsg, Types, FIELD_DATA, FIELD, DATA, NAME, MACRO_NAME, TYPE
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


def validate_field_data_for_update(data_dict: dict, macro_name: str, db_fields: list) -> dict:
    errors = validate_empty_list(data_dict, FIELD_DATA)
    if errors:
        return errors
    error_list: List[dict] = list()
    field_set = set()
    for field in data_dict[FIELD_DATA]:
        field_errors = validate_empty_str(field, FIELD)
        field_errors = {**field_errors, **validate_empty_str(field, DATA)}
        error_list.append(field_errors)
        if FIELD in field_errors:
            continue
        label = field[FIELD].strip().upper()
        field_macro_name = indexed_macros.get(label, None)
        if label in field_set:
            field_errors[FIELD] = ErrorMsg.UNIQUE
        elif not macro_name:
            field_errors[FIELD] = ErrorMsg.MACRO_NOT_FOUND
        elif not field_macro_name:
            field_errors[FIELD] = ErrorMsg.MACRO_LIBRARY
        elif macro_name != field_macro_name:
            field_errors[FIELD] = f"{ErrorMsg.MACRO_SAME} {macro_name}"
        else:
            db_field = next((db_field for db_field in db_fields if db_field[FIELD] == label), None)
            if DATA not in field_errors and db_field and db_field[DATA] == field[DATA]:
                field_errors[DATA] = ErrorMsg.DATA_SAME
        field_set.add(label)
    return {FIELD_DATA: error_list} if not all(error == dict() for error in error_list) else dict()


def validate_field_data_for_delete(data_dict: dict, macro_name: str, db_fields: list) -> dict:
    field_data: List[dict] = data_dict.get(FIELD_DATA, list())
    error_list: List[dict] = list()
    field_set = set()
    for field in field_data:
        field_errors = validate_empty_str(field, FIELD)
        error_list.append(field_errors)
        if FIELD in field_errors:
            continue
        label = field[FIELD].strip().upper()
        field_macro_name = indexed_macros.get(label, None)
        if label in field_set:
            field_errors[FIELD] = ErrorMsg.UNIQUE
        elif not macro_name:
            field_errors[FIELD] = ErrorMsg.MACRO_NOT_FOUND
        elif not field_macro_name:
            field_errors[FIELD] = ErrorMsg.MACRO_LIBRARY
        elif macro_name != field_macro_name:
            field_errors[FIELD] = f"{ErrorMsg.MACRO_SAME} {macro_name}"
        elif not any(db_field[FIELD] == label for db_field in db_fields):
            field_errors[FIELD] = ErrorMsg.NOT_FOUND
        field_set.add(label)
    return {FIELD_DATA: error_list} if not all(error == dict() for error in error_list) else dict()


def validate_macro_name(data_dict: dict, test_data: List[dict]) -> dict:
    error = validate_empty_str(data_dict, MACRO_NAME)
    if error:
        return error
    if data_dict[MACRO_NAME].strip().upper() not in macros:
        return {MACRO_NAME: ErrorMsg.MACRO_LIBRARY}
    if not any(element[MACRO_NAME] == data_dict[MACRO_NAME] for element in test_data):
        return {MACRO_NAME: ErrorMsg.NOT_FOUND}
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
