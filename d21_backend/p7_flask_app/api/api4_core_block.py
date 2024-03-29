from typing import List

from d21_backend.p2_assembly.mac2_data_macro import indexed_macros, get_macros
from d21_backend.p7_flask_app.api.api0_constants import Types, MACRO_NAME, VARIATION, FIELD_DATA, NAME, TYPE, FIELD, DATA, \
    VARIATION_NAME, SuccessMsg, ErrorMsg, LENGTH
from d21_backend.p7_flask_app.api.api1_models import TestData
from d21_backend.p7_flask_app.api.api2_validators import get_test_data, validate_variation_name, get_macro_name, get_variation, \
    validate_macro_name, validate_empty_list, validate_empty_str, validate_variation_number, validate_empty_int


def update_core_block(data_dict: dict) -> (int, dict):
    test_data, errors = get_test_data(data_dict, data_dict[TYPE])
    macro_name = get_macro_name(data_dict)
    variation_name, variation = get_variation(data_dict, test_data)
    if data_dict[TYPE] == Types.INPUT_CORE_BLOCK:
        errors = {**errors, **validate_variation_name(data_dict, test_data)}
    core_dict = get_core_dict(test_data, data_dict[TYPE], macro_name, variation)
    db_fields = core_dict[FIELD_DATA] if FIELD_DATA in core_dict else list()
    errors = {**errors, **validate_field_data_for_update(data_dict, macro_name, db_fields)}
    if errors:
        return 400, errors
    if not core_dict:
        # Create a new core block
        core_dict[NAME] = data_dict[NAME].strip()
        core_dict[TYPE] = data_dict[TYPE]
        core_dict[FIELD_DATA] = [{FIELD: field[FIELD].strip().upper(), **get_data_length(field, data_dict[TYPE])}
                                 for field in data_dict[FIELD_DATA]]
        core_dict[MACRO_NAME] = macro_name
        if data_dict[TYPE] == Types.INPUT_CORE_BLOCK:
            core_dict[VARIATION_NAME] = variation_name
            core_dict[VARIATION] = variation
        response = TestData.objects.no_orm.truncate.create(core_dict)
        return 200, response
    # Update an existing core block
    for field in data_dict[FIELD_DATA]:
        if any(core_field[FIELD] == field[FIELD].strip().upper() for core_field in core_dict[FIELD_DATA]):
            core_dict[FIELD_DATA] = [{**core_field, **get_data_length(field, data_dict[TYPE])}
                                     if core_field[FIELD] == field[FIELD].strip().upper() else core_field
                                     for core_field in core_dict[FIELD_DATA]]
        else:
            core_dict[FIELD_DATA].append({FIELD: field[FIELD].strip().upper(),
                                          **get_data_length(field, data_dict[TYPE])})
    response = TestData.objects.no_orm.truncate.save(core_dict)
    return 200, response


def delete_core_block(data_dict: dict) -> (int, dict):
    test_data, errors = get_test_data(data_dict, data_dict[TYPE])
    errors = {**errors, **validate_macro_name(data_dict, test_data)}
    macro_name = data_dict.get(MACRO_NAME, str()).strip().upper()
    if data_dict[TYPE] == Types.INPUT_CORE_BLOCK:
        errors = {**errors, **validate_variation_number(data_dict, test_data)}
    variation = data_dict.get(VARIATION, 0)
    core_dict = get_core_dict(test_data, data_dict[TYPE], macro_name, variation)
    db_fields = core_dict[FIELD_DATA] if FIELD_DATA in core_dict else list()
    errors = {**errors, **validate_field_data_for_delete(data_dict, macro_name, db_fields)}
    if errors:
        return 400, errors
    query = TestData.objects.filter_by(name=data_dict[NAME], type=data_dict[TYPE], macro_name=macro_name)
    if data_dict[TYPE] == Types.INPUT_CORE_BLOCK:
        query = query.filter_by(variation=variation)
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


def validate_field_data_for_update(data_dict: dict, macro_name: str, db_fields: list) -> dict:
    errors = validate_empty_list(data_dict, FIELD_DATA)
    if errors:
        return errors
    error_list: List[dict] = list()
    field_set = set()
    for field in data_dict[FIELD_DATA]:
        field_errors = validate_empty_str(field, FIELD)
        field_errors = {**field_errors, **validate_data_length(field, data_dict[TYPE])}
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
            if data_dict[TYPE] == Types.INPUT_CORE_BLOCK:
                if DATA in field and db_field and field[DATA] == db_field[DATA]:
                    field_errors[DATA] = ErrorMsg.DATA_SAME
            elif LENGTH in field and db_field and field[LENGTH] == db_field[LENGTH]:
                field_errors[LENGTH] = ErrorMsg.DATA_SAME
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


def validate_data_length(field: dict, element_type: str) -> dict:
    if element_type == Types.INPUT_CORE_BLOCK:
        return validate_empty_str(field, DATA)
    # Output Core Block
    if LENGTH in field and (validate_empty_int(field, LENGTH) or field[LENGTH] < 1):
        return {LENGTH: ErrorMsg.GREATER_0}
    return dict()


def get_data_length(field: dict, element_type: str) -> dict:
    if element_type == Types.INPUT_CORE_BLOCK:
        return {DATA: field[DATA]}
    if LENGTH in field:
        return {LENGTH: field[LENGTH]}
    label_ref = get_macros()[indexed_macros[field[FIELD].strip().upper()]].lookup(field[FIELD].strip().upper())
    return {LENGTH: label_ref.length}


def get_core_dict(test_data: List[dict], element_type: str, macro_name: str, variation: int) -> dict:
    if element_type == Types.INPUT_CORE_BLOCK:
        return next((element for element in test_data if element[MACRO_NAME] == macro_name
                     and element[VARIATION] == variation), dict())
    return next((element for element in test_data if element[MACRO_NAME] == macro_name), dict())
