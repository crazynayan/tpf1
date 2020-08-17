from typing import Tuple, List

from assembly.mac2_data_macro import indexed_macros, macros
from assembly.seg6_segment import segments
from flask_app.api.constants import ErrorMsg, Types, NEW_NAME, NAME, ACTION, Actions, SEG_NAME, TYPE, FIELD_DATA, \
    FIELD, DATA, MACRO_NAME, SuccessMsg
from flask_app.api.models import TestData


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


def validate_field_data(data_dict: dict, db_fields: list, macro_name: str = None) -> Tuple[dict, str]:
    field_data: List[dict] = data_dict.get(FIELD_DATA, list())
    error_list: List[dict] = list()
    common_macro_name = macro_name if macro_name else str()
    for field in field_data:
        field_errors = validate_empty_str(field, FIELD)
        if not macro_name:
            field_errors = {**field_errors, **validate_empty_str(field, DATA)}
        error_list.append(field_errors)
        if FIELD in field_errors:
            continue
        label = field[FIELD].strip().upper()
        field_macro_name = indexed_macros.get(label, None)
        common_macro_name = common_macro_name or field_macro_name
        if not field_macro_name:
            field_errors[FIELD] = ErrorMsg.MACRO_LIBRARY
        elif common_macro_name != field_macro_name:
            field_errors[FIELD] = f"{ErrorMsg.MACRO_SAME} {common_macro_name}"
        else:
            db_field = next((db_field for db_field in db_fields if db_field[FIELD] == label), None)
            if macro_name and not db_field:
                # DELETE action and field does not exists
                field_errors[FIELD] = ErrorMsg.NOT_FOUND
            if DATA not in field_errors and not macro_name and db_field and db_field[DATA] == field[DATA]:
                # UPDATE action and field exists and the data is also the same
                field_errors[DATA] = ErrorMsg.DATA_SAME
    if not all(error == dict() for error in error_list):
        return {FIELD_DATA: error_list}, str()
    return dict(), common_macro_name


def get_test_data(data_dict: dict, types: list) -> Tuple[List[dict], dict]:
    # if test data is found then return list of dict, empty error dict else return empty list, error dict
    error = validate_empty_str(data_dict, NAME)
    if error:
        return list(), error
    query = TestData.objects.no_orm.truncate.filter_by(name=data_dict[NAME])
    test_data = query.filter("type", TestData.objects.IN, types).get()
    if not test_data:
        return list(), {NAME: ErrorMsg.NOT_FOUND}
    return test_data, dict()


def process_test_data(data_dict: dict) -> (int, dict):
    error = validate_empty_str(data_dict, ACTION)
    if error:
        return 400, error
    if data_dict[ACTION] == Actions.CREATE:
        return create_test_data(data_dict)
    if data_dict[ACTION] == Actions.RENAME:
        return rename_test_data(data_dict)
    if data_dict[ACTION] == Actions.COPY:
        return copy_test_data(data_dict)
    if data_dict[ACTION] == Actions.UPDATE:
        return update_test_data(data_dict)
    if data_dict[ACTION] == Actions.DELETE:
        return update_test_data(data_dict)
    return 400, {ACTION: ErrorMsg.INVALID_ACTION}


def update_test_data(data_dict: dict) -> (int, dict):
    error = validate_empty_str(data_dict, TYPE)
    if error:
        return 400, error
    if data_dict[TYPE] == Types.INPUT_CORE_BLOCK:
        if data_dict[ACTION] == Actions.UPDATE:
            return update_input_core_block(data_dict)
        if data_dict[ACTION] == Actions.DELETE:
            return delete_input_core_block(data_dict)
    return 400, {TYPE: ErrorMsg.INVALID_TYPE}


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


def rename_test_data(data_dict: dict) -> (int, dict):
    errors = validate_new_name(data_dict, NEW_NAME)
    test_data, name_error = get_test_data(data_dict, [Types.INPUT_HEADER])
    errors = {**errors, **name_error}
    if errors:
        return 400, errors
    for element in test_data:
        element[NAME] = data_dict[NEW_NAME].strip()
    saved_data: List[dict] = TestData.objects.no_orm.truncate.save_all(test_data)
    response = next(element for element in saved_data if element[TYPE] == Types.INPUT_HEADER)
    return 200, response


def copy_test_data(data_dict: dict) -> (int, dict):
    errors = validate_new_name(data_dict, NEW_NAME)
    test_data, name_error = get_test_data(data_dict, [Types.INPUT_HEADER])
    errors = {**errors, **name_error}
    if errors:
        return 400, errors
    for element in test_data:
        element[NAME] = data_dict[NEW_NAME].strip()
    created_data: List[dict] = TestData.objects.no_orm.truncate.create_all(test_data)
    return 200, created_data


def update_input_core_block(data_dict: dict) -> (int, dict):
    macro_name = str()
    test_data, errors = get_test_data(data_dict, [Types.INPUT_CORE_BLOCK])
    field_error = validate_empty_list(data_dict, FIELD_DATA)
    core_dict = next((element for element in test_data if element[TYPE] == Types.INPUT_CORE_BLOCK
                      and element[MACRO_NAME] == macro_name), dict())
    db_fields = core_dict[FIELD_DATA] if FIELD_DATA in core_dict else list()
    if not field_error:
        field_error, macro_name = validate_field_data(data_dict, db_fields)
    errors = {**errors, **field_error}
    if errors:
        return 400, errors
    if not core_dict:
        core_dict[NAME] = test_data[0][NAME]
        core_dict[TYPE] = Types.INPUT_CORE_BLOCK
        core_dict[FIELD_DATA] = [{FIELD: field[FIELD].strip().upper(), DATA: field[DATA]}
                                 for field in data_dict[FIELD_DATA]]
        response = TestData.objects.no_orm.truncate.create(core_dict)
        return 200, response
    for field in data_dict[FIELD_DATA]:
        core_field = next((core_field for core_field in core_dict[FIELD_DATA]
                           if core_field[FIELD] == field[FIELD].strip().upper()), None)
        if core_field:
            core_field[DATA] = field[DATA]
            continue
        core_dict[FIELD_DATA].append({FIELD: field[FIELD].strip().upper(), DATA: field[DATA]})
    response = TestData.objects.no_orm.truncate.save(core_dict)
    return 200, response


def delete_input_core_block(data_dict: dict) -> (int, dict):
    test_data, errors = get_test_data(data_dict, [Types.INPUT_CORE_BLOCK])
    macro_error = validate_empty_str(data_dict, MACRO_NAME)
    core_dict = dict()
    if macro_error:
        errors = {**errors, **macro_error}
    elif data_dict[MACRO_NAME].strip().upper() not in macros:
        errors[MACRO_NAME] = ErrorMsg.MACRO_LIBRARY
    else:
        core_dict = next((element for element in test_data
                          if element[MACRO_NAME] == data_dict[MACRO_NAME].strip().upper()), dict())
        if not core_dict:
            errors[MACRO_NAME] = ErrorMsg.NOT_FOUND
    if errors:
        return 400, errors
    db_fields = core_dict[FIELD_DATA] if FIELD_DATA in core_dict else list()
    errors, _ = validate_field_data(data_dict, db_fields, data_dict[MACRO_NAME].strip().upper())
    if errors:
        return 400, errors
    if validate_empty_list(data_dict, FIELD_DATA):
        query = TestData.objects.filter_by(name=data_dict[NAME], type=Types.INPUT_CORE_BLOCK)
        query.filter_by(macro_name=data_dict[MACRO_NAME]).delete()
        return 200, {Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}
    for field in data_dict[FIELD_DATA]:
        core_field = next(core_field for core_field in core_dict[FIELD_DATA]
                          if core_field[FIELD] == field[FIELD].strip().upper())
        core_dict[FIELD_DATA].remove(core_field)
    if not core_dict[FIELD_DATA]:
        query = TestData.objects.filter_by(name=data_dict[NAME], type=Types.INPUT_CORE_BLOCK)
        query.filter_by(macro_name=data_dict[MACRO_NAME]).delete()
        return 200, {Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}
    response = TestData.objects.no_orm.truncate.save(core_dict)
    return 200, response
