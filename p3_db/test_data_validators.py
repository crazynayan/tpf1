from base64 import b64encode
from copy import copy
from typing import Tuple

from config import config
from p1_utils.errors import AssemblyError
from p2_assembly.mac2_data_macro import DataMacro, macros
from p2_assembly.seg6_segment import Segment
from p2_assembly.seg9_collection import seg_collection
from p3_db.pnr import Pnr as PnrDb, PnrLocator
from p3_db.test_data_elements import Core


def validate_hex_data_with_field_data(body: dict) -> dict:
    errors = dict()
    if not body["hex_data"] or not (body["seg_name"] or body["field_data"]):
        return errors
    if body["seg_name"]:
        errors["seg_name"] = "Seg name should be left blank when hex data is provided."
    if body["field_data"]:
        errors["field_data"] = "Field data should be left blank when hex data is provided."
    errors["hex_data"] = "Hex data should be left blank when either seg name or fields are provided."
    return errors


def validate_hex_data(input_hex_data: str) -> Tuple[str, str]:
    errors = str()
    hex_data = str()
    if not input_hex_data:
        return errors, hex_data
    if not isinstance(input_hex_data, str):
        errors = "Hex data should be a string."
        return errors, hex_data
    hex_data = "".join(char.upper() for char in input_hex_data if char != " ")
    if not all(char.isdigit() or char in ("A", "B", "C", "D", "E", "F") for char in hex_data):
        errors = "Hex characters can only be 0-F. Only spaces allowed."
        return errors, hex_data
    if len(hex_data) % 2 != 0:
        errors = "The length of hex characters should be even."
        return errors, hex_data
    hex_data = b64encode(bytes.fromhex(hex_data)).decode()
    return errors, hex_data


def get_updated_field_data(body: dict) -> Tuple[dict, list]:
    field_data = list()
    errors = dict()
    for field_data_str in body["field_data"].split(","):
        if field_data_str.count(":") != 1:
            errors["field_data"] = f"Include a colon : to separate field and data - {field_data_str}."
            break
        field = field_data_str.split(":")[0].strip().upper()
        data = field_data_str.split(":")[1].strip().upper()
        error, data = validate_hex_data(data)
        if error:
            errors["field_data"] = f"{field}: {error}"
            break
        field_dict = {"field": field, "data": data}
        field_data.append(field_dict)
    return errors, field_data


def validate_seg_name_and_field_data(body: dict) -> Tuple[dict, list]:
    errors = dict()
    field_data = list()
    if body["field_data"]:
        if not body["seg_name"]:
            errors["seg_name"] = "Segment name required when field data is specified."
        if not isinstance(body["field_data"], str):
            errors["field_data"] = "Invalid format of field data. It must be a string."
            return errors, field_data
        new_errors, field_data = get_updated_field_data(body)
        errors = {**errors, **new_errors}
    if body["seg_name"]:
        if not body["field_data"]:
            errors["field_data"] = "Field data is required when seg name is provided."
        if not isinstance(body["seg_name"], str) or len(body["seg_name"]) != 4:
            errors["seg_name"] = "Invalid segment name. Seg name must be a string of 4 characters."
            return errors, field_data
        seg: Segment = seg_collection.get_seg(body["seg_name"])
        if not seg:
            errors["seg_name"] = f"{body['seg_name']} not found."
        elif seg.file_type != config.LST:
            errors["seg_name"] = f"{body['seg_name']} is not a listing."
        else:
            try:
                seg.assemble()
            except AssemblyError:
                errors["seg_name"] = "Error in assembling segment."
        if "seg_name" in errors or "field_data" in errors:
            return errors, field_data
        for field_dict in field_data:
            if not seg.check(field_dict["field"]):
                errors["field_data"] = f"Field {field_dict['field']} not found."
                break
    return errors, field_data


def get_response_body_for_hex_and_field_data(input_response: dict, input_body: dict) -> Tuple[dict, dict]:
    response = copy(input_response)
    body = copy(input_body)
    errors: dict = validate_hex_data_with_field_data(body)
    response["error_fields"] = {**response["error_fields"], **errors}
    if errors:
        return response, body
    error, hex_data = validate_hex_data(body["hex_data"])
    if error:
        response["error_fields"] = {**response["error_fields"], **{"hex_data": error}}
        return response, body
    body["hex_data"] = hex_data
    errors, field_data = validate_seg_name_and_field_data(body)
    response["error_fields"] = {**response["error_fields"], **errors}
    body["original_field_data"] = body["field_data"]
    body["field_data"] = field_data
    return response, body


def get_response_body_for_macro(input_response: dict, input_body: dict, macro_name: str) -> Tuple[dict, dict]:
    response = copy(input_response)
    body = copy(input_body)
    if not body["field_data"] or not isinstance(body["field_data"], str):
        response["error_fields"]["field_data"] = "Field data is required. It cannot be empty."
        return response, body
    errors, field_data = get_updated_field_data(body)
    response["error_fields"] = {**response["error_fields"], **errors}
    if errors:
        return response, body
    if macro_name not in macros:
        response["error_fields"]["macro_name"] = f"Data macro{macro_name} not found."
        return response, body
    macro: DataMacro = macros[macro_name]
    for field_dict in field_data:
        if not macro.check(field_dict["field"]) or macro.lookup(field_dict["field"]).name != macro_name:
            response["error_fields"]["field_data"] = f"Field {field_dict['field']} not found."
            break
    body["original_field_data"] = body["field_data"]
    body["field_data"] = field_data
    return response, body


def validate_output_attribute(attribute: str, field: str) -> Tuple[str, str, int]:
    attr = attribute.strip()
    if len(attr) < 2:
        return f"{field}: Attribute should be of at least 2 char.", str(), int()
    if attr[0] not in {"I", "L"}:
        return f"{field}: Attribute should be I (item number) or L (length).", str(), int()
    try:
        attr_value: int = int(attr[1:])
    except ValueError:
        return f"{field}: Attribute value should be a number for attribute {attr[0]}.", str(), int()
    if not 1 <= attr_value <= 20:
        return f"{field}: Attribute value should be between 1 and 20 for attribute {attr[0]}.", str(), int()
    attr_key = "item_number" if attr[0] == "I" else "length"
    return str(), attr_key, attr_value


def validate_and_update_field_item_len(body: dict) -> dict:
    errors: dict = dict()
    if not isinstance(body["field_item_len"], str) or not body["field_item_len"]:
        errors["field_item_len"] = "PNR Field details are required."
        return errors
    pnr_field_list: list = [field.strip().upper() for field in body["field_item_len"].split(",")]
    if any(not field for field in pnr_field_list):
        errors["field_item_len"] = "There should be a PNR field item between commas."
        return errors
    body["original_field_item_len"] = body["field_item_len"].strip().upper()
    body["field_item_len"] = list()
    PnrDb.load_macros()
    for field_item in pnr_field_list:
        field_item_len: list = [f_i_l.strip() for f_i_l in field_item.split(":")]
        field = field_item_len[0]
        error = validate_pnr_field(field)
        if error:
            errors["field_item_len"] = error
            break
        field_item_dict: dict = {"field": field, "length": PnrDb.get_field_len(field), "item_number": 1}
        body["field_item_len"].append(field_item_dict)
        if len(field_item_len) == 1:
            continue
        error, attr_key, attr_value = validate_output_attribute(field_item_len[1], field)
        if error:
            errors["field_item_len"] = error
            break
        field_item_dict[attr_key] = attr_value
        if len(field_item_len) == 2:
            continue
        attr_key1 = attr_key
        error, attr_key, attr_value = validate_output_attribute(field_item_len[2], field)
        if error:
            errors["field_item_len"] = error
            break
        field_item_dict[attr_key] = attr_value
        if attr_key1 == attr_key:
            errors["field_item_len"] = f"{field}: Both the attributes cannot be same."
            break
        if len(field_item_len) > 3:
            errors["field_item_len"] = f"{field}: Only 2 attributes are allowed."
            break
    return errors


def validate_pnr_field(field_name: str) -> str:
    if not field_name:
        return "There should a PNR field between colons."
    if not PnrDb.is_valid_field(field_name):
        return f"{field_name}: This is not a valid PNR field name."
    return str()


def validate_and_update_pnr_text_with_field(body: dict) -> dict:
    errors = dict()
    body["original_text"] = str()
    body["original_field_data_item"] = str()
    if not body["text"] and not body["field_data_item"]:
        errors["text"] = "Either PNR item text or PNR field data is required."
        errors["field_data_item"] = "Either PNR field data or PNR item text is required."
    elif body["text"] and body["field_data_item"]:
        errors["text"] = "PNR text should be left blank when PNR field data is provided."
    else:
        if not isinstance(body["text"], str):
            errors["text"] = "PNR item text should be string."
        if not isinstance(body["field_data_item"], str):
            errors["field_data_item"] = "PNR field data should be string"
    if errors:
        return errors
    if body["text"]:
        pnr_texts: list = [text.strip().upper() for text in body["text"].split(",")]
        if any(not text for text in pnr_texts):
            errors["text"] = "There should be some PNR item text between commas."
            return errors
        if len(pnr_texts) > 20:
            errors["text"] = "Only a max of 20 PNR items can be added."
            return errors
        body["original_text"] = body["text"].strip().upper()
        body["text"] = pnr_texts
        return errors
    pnr_field_list: list = [field.strip().upper() for field in body["field_data_item"].split(",")]
    if any(not field for field in pnr_field_list):
        errors["field_data_item"] = "There should be a PNR field data item between commas."
        return errors
    body["original_field_data_item"] = body["field_data_item"].strip().upper()
    body["field_data_item"] = list()
    PnrDb.load_macros()
    prior_item_number: int = 0
    for pnr_field in pnr_field_list:
        field_data_item: list = [f_d_i.strip() for f_d_i in pnr_field.split(":")]
        field = field_data_item[0]
        error = validate_pnr_field(field)
        if error:
            errors["field_data_item"] = error
            break
        if len(field_data_item) != 3:
            errors["field_data_item"] = f"{field}: The format is Field:Data:Item and all 3 are required."
            break
        data, item = field_data_item[1], field_data_item[2]
        if not data or not item:
            errors["field_data_item"] = f"{field}: The format is Field:Data:Item and all 3 are required."
            break
        error, data = validate_hex_data(field_data_item[1])
        if error:
            errors["field_data_item"] = f"{field}: {error}"
            break
        if not item.startswith("I") or len(item) < 2 or not item[1:].isdigit():
            errors["field_data_item"] = f"{field}: Item number should start with I followed by a number."
            break
        item_number: int = int(item[1:])
        if item_number > 20:
            errors["field_data_item"] = f"{field}: Only a max of 20 PNR items allowed."
            break
        if item_number - prior_item_number not in (0, 1) or item_number == 0:
            errors["field_data_item"] = f"{field}: Item number is out of sequence."
            break
        prior_item_number = item_number
        body["field_data_item"].append({"field": field, "data": data, "item_number": item_number})
    return errors


def validate_and_update_pnr_locator_key(body: dict) -> dict:
    errors = dict()
    if not PnrLocator.is_valid(body["locator"]):
        errors["locator"] = "PNR Locator needs to be 6 character alpha string."
    if PnrDb.get_attribute_by_name(body["key"]) is None:
        errors["key"] = "Invalid PNR key."
    if not errors:
        body["locator"] = config.AAAPNR if not body["locator"] else body["locator"].upper()
    return errors


def create_core_for_hex_and_field_data(body: dict) -> Core:
    core_to_create: Core = create_core(body)
    core_to_create.hex_data = body["hex_data"]
    core_to_create.seg_name = body["seg_name"]
    return core_to_create


def create_core(body: dict) -> Core:
    core_to_create: Core = Core()
    core_to_create.variation = body["variation"]
    core_to_create.variation_name = body["variation_name"]
    core_to_create.field_data = body["field_data"]
    core_to_create.original_field_data = body["original_field_data"]
    return core_to_create
