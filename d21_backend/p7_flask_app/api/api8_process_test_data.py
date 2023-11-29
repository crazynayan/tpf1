from d21_backend.p7_flask_app.api.api0_constants import ErrorMsg, Types, ACTION, Actions, TYPE, VARIATION_NAME, \
    NEW_VARIATION_NAME
from d21_backend.p7_flask_app.api.api1_models import TestData
from d21_backend.p7_flask_app.api.api2_validators import validate_empty_str, get_test_data, validate_variation_number, \
    validate_variation_new_name
from d21_backend.p7_flask_app.api.api3_headers import create_test_data, rename_test_data_name, copy_test_data
from d21_backend.p7_flask_app.api.api4_core_block import update_core_block, delete_core_block


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
    if data_dict[TYPE] in (Types.INPUT_CORE_BLOCK, Types.OUTPUT_CORE_BLOCK):
        if data_dict[ACTION] == Actions.UPDATE:
            return update_core_block(data_dict)
        if data_dict[ACTION] == Actions.DELETE:
            return delete_core_block(data_dict)
    return 400, {TYPE: ErrorMsg.INVALID_TYPE}


def rename_test_data(data_dict: dict) -> (int, dict):
    if validate_empty_str(data_dict, TYPE):
        return rename_test_data_name(data_dict)
    if data_dict[TYPE] == Types.INPUT_HEADER:
        return rename_test_data_name(data_dict)
    if data_dict[TYPE] == Types.INPUT_CORE_BLOCK:
        return rename_variation(data_dict)
    return 400, {TYPE: ErrorMsg.INVALID_TYPE}


def rename_variation(data_dict: dict) -> (int, dict):
    test_data, errors = get_test_data(data_dict, data_dict[TYPE])
    errors = {**errors, **validate_variation_number(data_dict, test_data)}
    errors = {**errors, **validate_variation_new_name(data_dict, test_data)}
    if errors:
        return 400, errors
    for element in test_data:
        element[VARIATION_NAME] = data_dict[NEW_VARIATION_NAME]
    renamed_data = TestData.objects.no_orm.truncate.save_all(test_data)
    return 200, renamed_data
