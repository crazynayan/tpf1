from base64 import b64encode
from typing import Tuple

from config import config
from p1_utils.errors import AssemblyError
from p2_assembly.seg6_segment import Segment, seg_collection


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


def validate_hex_data(input_hex_data: str) -> Tuple[dict, str]:
    errors = dict()
    hex_data = str()
    if not input_hex_data:
        return errors, hex_data
    if not isinstance(input_hex_data, str):
        errors["hex_data"] = "Hex data should be a string."
        return errors, hex_data
    hex_data = "".join(char.upper() for char in input_hex_data if char != " ")
    if not all(char.isdigit() or char in ("A", "B", "C", "D", "E", "F", " ") for char in hex_data):
        errors["hex_data"] = "Hex characters can only be 0-F. Only spaces allowed."
        return errors, hex_data
    if len(hex_data) % 2 != 0:
        errors["hex_data"] = "The length of hex characters should be even."
        return errors, hex_data
    hex_data = b64encode(bytes.fromhex(hex_data)).decode()
    return errors, hex_data


def validate_seg_name_and_field_data(body: dict) -> Tuple[dict, list]:
    errors = dict()
    field_data = list()
    if body["field_data"]:
        if not body["seg_name"]:
            errors["seg_name"] = "Segment name required when field data is specified."
        if not isinstance(body["field_data"], str):
            errors["field_data"] = "Invalid format of field data. It must be a string."
            return errors, field_data
        for field_data_str in body["field_data"].split(","):
            if field_data_str.count(":") != 1:
                errors["field_data"] = f"Include a colon : to separate field and data - {field_data_str}."
                break
            field = field_data_str.split(":")[0].strip().upper()
            data = field_data_str.split(":")[1].strip().upper()
            data = "".join(char.upper() for char in data if char != " ")
            if not all(char.isdigit() or char in ("A", "B", "C", "D", "E", "F", " ") for char in data):
                errors["field_data"] = "Hex characters can only be 0-F. Only spaces allowed."
                break
            if len(data) % 2 != 0:
                errors["field_data"] = "The length of hex characters should be even."
                break
            field_dict = {"field": field, "data": b64encode(bytes.fromhex(data)).decode()}
            field_data.append(field_dict)
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
