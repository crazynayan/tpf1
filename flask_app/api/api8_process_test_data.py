from flask_app.api.api0_constants import ErrorMsg, Types, ACTION, Actions, TYPE
from flask_app.api.api2_validators import validate_empty_str
from flask_app.api.api3_headers import create_test_data, rename_test_data, copy_test_data
from flask_app.api.api4_input_core import update_input_core_block, delete_input_core_block


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
