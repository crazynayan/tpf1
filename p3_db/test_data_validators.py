from base64 import b64encode
from typing import Tuple, Callable, Optional

from config import config
from p1_utils.errors import AssemblyError
from p2_assembly.mac2_data_macro import macros
from p2_assembly.seg6_segment import Segment
from p2_assembly.seg9_collection import seg_collection
from p3_db.pnr import Pnr as PnrDb, PnrLocator


def validate_hex_data(input_hex_data: str) -> Tuple[str, str]:
    error = str()
    hex_data = str()
    if not input_hex_data:
        return error, hex_data
    if not isinstance(input_hex_data, str):
        error = "Hex data should be a string."
        return error, hex_data
    hex_data = "".join(char.upper() for char in input_hex_data if char != " ")
    if not all(char.isdigit() or char in ("A", "B", "C", "D", "E", "F") for char in hex_data):
        error = "Hex characters can only be 0-F. Only spaces allowed."
        return error, hex_data
    if len(hex_data) % 2 != 0:
        error = "The length of hex characters should be even."
        return error, hex_data
    hex_data = b64encode(bytes.fromhex(hex_data)).decode()
    return error, hex_data


def validate_and_update_field_data(body: dict, check_field: Callable[[str], bool]) -> dict:
    errors: dict = dict()
    if not isinstance(body["field_data"], str) or not body["field_data"]:
        errors["field_data"] = "Field data is required."
        return errors
    field_list: list = [field.strip().upper() for field in body["field_data"].split(",")]
    if any(not field for field in field_list):
        errors["field_data"] = "There should be a field between commas."
        return errors
    body["original_field_data"] = body["field_data"].strip().upper()
    body["field_data"] = list()
    for core_field in field_list:
        field_data: list = [f_d.strip() for f_d in core_field.split(":")]
        field = field_data[0]
        if not field:
            errors["field_data"] = "There should a field between colons."
            break
        if not check_field(field):
            errors["field_data"] = f"{field}: This is not a valid field name."
            break
        if len(field_data) != 2 or not field_data[1]:
            errors["field_data"] = f"{field}: The format is Field:Data and Data is required."
            break
        error, data = validate_hex_data(field_data[1])
        if error:
            errors["field_data"] = f"{field}: {error}"
            break
        body["field_data"].append({"field": field, "data": data})
    return errors


def validate_seg_name(body: dict) -> Tuple[dict, Optional[Segment]]:
    errors = dict()
    if len(body["seg_name"]) != 4:
        errors["seg_name"] = "Invalid segment name. Seg name must of 4 characters."
        return errors, None
    seg: Segment = seg_collection.get_seg(body["seg_name"])
    if not seg:
        errors["seg_name"] = f"Segment {body['seg_name']} not found."
    elif seg.file_type != config.LST:
        errors["seg_name"] = f"Segment {body['seg_name']} is not a listing."
    else:
        try:
            seg.assemble()
        except AssemblyError:
            errors["seg_name"] = f"Error in assembling segment {body['seg_name']}."
    return errors, seg


def validate_and_update_hex_and_field_data(body: dict) -> dict:
    errors = dict()
    if not isinstance(body["hex_data"], str):
        errors["hex_data"] = "Hex data should be a string."
    if not isinstance(body["field_data"], str):
        errors["field_data"] = "Field data should be a string."
    if not isinstance(body["seg_name"], str):
        errors["seg_name"] = "Segment name should be a string."
    if errors:
        return errors
    if body["hex_data"]:
        if body["field_data"]:
            errors["field_data"] = "Field data should be left blank when hex data is provided."
            errors["hex_data"] = "Hex data should be left blank when field data is provided."
    elif not body["field_data"]:  # Neither field_data nor hex_data is provided
        body["original_field_data"] = str()
        return errors  # Return with no errors
    elif not body["seg_name"]:
        errors["seg_name"] = "Seg name is required when field data is provided."
    if errors:
        return errors
    # Validate hex_data
    error, hex_data = validate_hex_data(body["hex_data"])
    if error:
        errors["hex_data"] = error
    if body["hex_data"]:
        body["hex_data"] = hex_data
        body["original_field_data"] = str()
        return errors  # Return with no errors
    # Validate Seg name
    errors, seg = validate_seg_name(body)
    if errors:
        return errors
    # Validate field data
    errors = validate_and_update_field_data(body, seg.check)
    return errors


def validate_and_update_global_data(body: dict) -> dict:
    errors = dict()
    if not isinstance(body["hex_data"], str):
        errors["hex_data"] = "Hex data should be a string."
    if not isinstance(body["field_data"], str):
        errors["field_data"] = "Field data should be a string."
    if not isinstance(body["seg_name"], str):
        errors["seg_name"] = "Segment name should be a string."
    if not isinstance(body["is_global_record"], bool):
        errors["is_global_record"] = "Is global record? field should be a boolean."
    if errors:
        return errors
    if not body["is_global_record"]:  # Global field
        if not body["hex_data"]:
            errors["hex_data"] = "Hex data is required for a global field."
        if body["field_data"]:
            errors["field_data"] = "Field data should be left blank for a global field."
        if errors:
            return errors
        error, hex_data = validate_hex_data(body["hex_data"])
        if error:
            errors["hex_data"] = error
            return errors
        body["hex_data"] = hex_data
        body["original_field_data"] = str()
        return errors  # Return with no errors
    # Global record
    if not body["field_data"]:
        errors["field_data"] = "Field data is required for a global record."
    if body["hex_data"]:
        errors["hex_data"] = "Hex data should be left blank for a global record."
    if errors:
        return errors
    # Validate Seg name
    errors, seg = validate_seg_name(body)
    if errors:
        return errors
    # Validate field data
    errors = validate_and_update_field_data(body, seg.check)
    return errors


def validate_and_update_macro_field_data(body: dict, macro_name: str) -> dict:
    errors: dict = dict()
    if macro_name not in macros:
        errors["macro_name"] = f"Data macro {macro_name} not found."
        return errors
    errors = validate_and_update_field_data(body, macros[macro_name].check)
    return errors


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


def validate_pnr_field(field_name: str) -> str:
    if not field_name:
        return "There should a PNR field between colons."
    if not PnrDb.is_valid_field(field_name):
        return f"{field_name}: This is not a valid PNR field name."
    return str()


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
