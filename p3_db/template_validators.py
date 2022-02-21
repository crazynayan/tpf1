from typing import List

from flask import g

from p3_db.template_models import Template, PNR
from p3_db.test_data_validators import validate_and_update_pnr_text_with_field


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


def validate_and_update_existing_pnr_template_name(body: dict) -> dict:
    errors: dict = validate_template_name(body)
    if errors:
        return errors
    templates: List[Template] = Template.objects.filter_by(name=body["name"], type=PNR).get()
    if not templates:
        errors["name"] = "No PNR template with this name found."
        return errors
    body["description"] = templates[0].description
    body["owner"] = templates[0].owner
    body["locator"] = templates[0].locator
    if any(template.key == body["key"] for template in templates):
        errors["key"] = f"PNR key {body['key'].upper()} already exists for locator {body['locator']}."
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
