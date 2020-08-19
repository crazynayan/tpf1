from typing import List

from assembly.seg6_segment import segments
from flask_app.api.api0_constants import ErrorMsg, Types, NEW_NAME, NAME, ACTION, Actions, SEG_NAME, TYPE, FIELD_DATA, \
    FIELD, DATA, MACRO_NAME, SuccessMsg, VARIATION, VARIATION_NAME
from flask_app.api.api1_models import TestData
from flask_app.api.api2_validators import validate_empty_str, validate_empty_list, validate_new_name, \
    get_test_data, validate_macro_name, validate_field_data_for_delete, validate_field_data_for_update, \
    get_macro_name, validate_variation, get_variation


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


def update_input_core_block(data_dict: dict) -> (int, dict):
    test_data, errors = get_test_data(data_dict, Types.INPUT_CORE_BLOCK)
    errors = {**errors, **validate_variation(data_dict, test_data)}
    macro_name = get_macro_name(data_dict)
    variation_name, variation = get_variation(data_dict, test_data)
    core_dict = next((element for element in test_data if element[MACRO_NAME] == macro_name
                      and element[VARIATION] == variation), dict())
    db_fields = core_dict[FIELD_DATA] if FIELD_DATA in core_dict else list()
    errors = {**errors, **validate_field_data_for_update(data_dict, macro_name, db_fields)}
    if errors:
        return 400, errors
    if not core_dict:
        # Create a new core block
        core_dict[NAME] = data_dict[NAME].strip()
        core_dict[TYPE] = Types.INPUT_CORE_BLOCK
        core_dict[FIELD_DATA] = [{FIELD: field[FIELD].strip().upper(), DATA: field[DATA]}
                                 for field in data_dict[FIELD_DATA]]
        core_dict[MACRO_NAME] = macro_name
        core_dict[VARIATION_NAME] = variation_name
        core_dict[VARIATION] = variation
        response = TestData.objects.no_orm.truncate.create(core_dict)
        return 200, response
    # Update an existing core block
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
    test_data, errors = get_test_data(data_dict, Types.INPUT_CORE_BLOCK)
    errors = {**errors, **validate_macro_name(data_dict, test_data)}
    macro_name = data_dict.get(MACRO_NAME, str()).strip().upper()
    core_dict = next((element for element in test_data if element[MACRO_NAME] == macro_name), dict())
    db_fields = core_dict[FIELD_DATA] if FIELD_DATA in core_dict else list()
    errors = {**errors, **validate_field_data_for_delete(data_dict, macro_name, db_fields)}
    if errors:
        return 400, errors
    query = TestData.objects.filter_by(name=data_dict[NAME], type=Types.INPUT_CORE_BLOCK, macro_name=macro_name)
    if validate_empty_list(data_dict, FIELD_DATA):
        # Delete the entire core block if field_data is not specified on input
        query.delete()
        return 200, {Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}
    for field in data_dict[FIELD_DATA]:
        core_field = next(core_field for core_field in core_dict[FIELD_DATA]
                          if core_field[FIELD] == field[FIELD].strip().upper())
        core_dict[FIELD_DATA].remove(core_field)
    if not core_dict[FIELD_DATA]:
        # If no remaining field then delete the core block
        query.delete()
        return 200, {Types.INPUT_CORE_BLOCK: SuccessMsg.DELETE}
    # Return the core block state after deleting the field
    response = TestData.objects.no_orm.truncate.save(core_dict)
    return 200, response
