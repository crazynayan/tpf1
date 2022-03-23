from typing import List, Tuple

from flask import g

from p2_assembly.mac2_data_macro import get_global_ref
from p3_db.template_models import Template, PNR, GLOBAL
from p3_db.test_data import TestData
from p3_db.test_data_validators import validate_and_update_pnr_text_with_field, validate_and_update_global_data


def validate_template_name(body: dict) -> dict:
    errors: dict = dict()
    if not isinstance(body["name"], str):
        errors["name"] = "Name must be a string."
        return errors
    if not body["name"]:
        errors["name"] = "Name cannot be left blank."
    return errors


def validate_and_update_new_template_name(body: dict) -> dict:
    errors: dict = validate_template_name(body)
    if errors:
        return errors
    if Template.objects.filter_by(name=body["name"]).first():
        errors["name"] = "There is already a template with this name. Please use unique name."
    try:
        body["owner"] = g.current_user.email
    except RuntimeError:
        pass
    return errors


def validate_existing_template_name(body: dict, template_type: str) -> Tuple[dict, List[Template]]:
    errors: dict = validate_template_name(body)
    if errors:
        return errors, list()
    templates: List[Template] = Template.objects.filter_by(name=body["name"], type=template_type).get()
    if not templates:
        errors["name"] = "No PNR template with this name found."
    return errors, templates


def validate_and_update_existing_pnr_template_name(body: dict) -> dict:
    errors, templates = validate_existing_template_name(body, PNR)
    if errors:
        return errors
    body["description"] = templates[0].description
    body["owner"] = templates[0].owner
    body["locator"] = templates[0].locator
    body["test_data_links"] = templates[0].test_data_links
    if any(template.key == body["key"] for template in templates):
        errors["key"] = f"PNR key {body['key'].upper()} already exists for locator {body['locator']}."
    return errors


def validate_and_update_existing_global_template_name(body: dict) -> dict:
    errors, templates = validate_existing_template_name(body, GLOBAL)
    if errors:
        return errors
    body["description"] = templates[0].description
    body["owner"] = templates[0].owner
    body["test_data_links"] = templates[0].test_data_links
    if any(template.global_name == body["global_name"] for template in templates):
        errors["global_name"] = f"Global name {body['global_name']} already exists."
    return errors


def validate_and_update_pnr_fields(body: dict) -> dict:
    body["field_data_item"] = body["field_data"]
    errors = validate_and_update_pnr_text_with_field(body)
    if not errors:
        body["text"] = body["original_text"]
        body["field_data"] = body["original_field_data_item"]
        body["type"] = PNR
    elif "field_data_item" in errors:
        errors["field_data"] = errors["field_data_item"]
        del errors["field_data_item"]
    return errors


def validate_and_update_global_fields(body: dict) -> dict:
    errors = dict()
    if not body["global_name"] or not isinstance(body["global_name"], str) or not get_global_ref(body["global_name"]):
        errors["global_name"] = "This global name does not exists in global definitions."
    else:
        body["global_name"] = body["global_name"].strip().upper()
    other_errors = validate_and_update_global_data(body)
    if other_errors:
        errors = {**errors, **other_errors}
    else:
        body["field_data"] = body["original_field_data"]
        body["hex_data"] = body["original_hex_data"]
        body["type"] = GLOBAL
    return errors


def add_test_data_link_to_template(test_data: TestData, templates: List[Template]):
    for template in templates:
        if test_data.id not in template.test_data_links:
            template.test_data_links.append(test_data.id)
    return


def remove_test_data_link_from_template(test_data: TestData, templates: List[Template], template_type: str):
    if template_type == PNR:
        if any(td_pnr for td_pnr in test_data.pnr if td_pnr.link == templates[0].name):
            return
    else:
        if any(core for core in test_data.cores if core.link == templates[0].name):
            return
    for template in templates:
        if test_data.id in template.test_data_links:
            template.test_data_links.remove(test_data.id)
    return


def validate_and_update_template_rename_copy(body: dict) -> Tuple[dict, List[Template]]:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"old_name", "new_name", "description"}:
        response["message"] = "Only 3 fields allowed (old_name, new_name, description) and all are mandatory."
        return response, list()
    body["name"] = body["old_name"]
    errors = validate_template_name(body)
    if errors:
        response["error_fields"]["old_name"] = errors["name"]
        return response, list()
    templates: List[Template] = Template.objects.filter_by(name=body["old_name"]).get()
    if not templates:
        response["error_fields"]["old_name"] = "No template found with this name."
    return response, templates
