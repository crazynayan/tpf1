from typing import List

from flask import g

from p2_assembly.mac2_data_macro import get_global_ref
from p3_db.response import StandardResponse
from p3_db.template_models import Template, PNR, GLOBAL, AAA, AAA_MACRO_NAME, TD_REF, validate_ownership
from p3_db.test_data import TestData
from p3_db.test_data_validators import validate_and_update_pnr_text_with_field, validate_and_update_global_data, \
    validate_and_update_macro_field_data


def validate_template_name(rsp: StandardResponse) -> None:
    if not rsp.body.name:
        rsp.error = True
        rsp.error_fields.name = "Name cannot be left blank."
    return


def validate_and_update_new_template_name(rsp: StandardResponse) -> None:
    validate_template_name(rsp)
    if Template.objects.filter_by(name=rsp.body.name).first():
        rsp.error = True
        rsp.error_fields.name = "There is already a template with this name. Please use unique name."
    try:
        rsp.body.owner = g.current_user.email
    except RuntimeError:
        pass
    return


def validate_existing_template_name(rsp: StandardResponse) -> List[Template]:
    validate_template_name(rsp)
    if rsp.error:
        return list()
    templates: List[Template] = Template.objects.filter_by(name=rsp.body.name).get()
    if not templates:
        rsp.error = True
        rsp.error_fields.name = "No template found with this name."
    return templates


def validate_and_update_existing_pnr_template_name(rsp: StandardResponse) -> None:
    templates = validate_existing_template_name(rsp)
    if not templates:
        return
    validate_ownership(templates[0], rsp)
    rsp.body.description = templates[0].description
    rsp.body.owner = templates[0].owner
    rsp.body.test_data_links = templates[0].test_data_links
    rsp.body.locator = templates[0].locator
    if any(template.key == rsp.body.key for template in templates):
        rsp.error = True
        rsp.error_fields.key = f"PNR key {rsp.body.key.upper()} already exists for locator {rsp.body.locator}."
    return


def validate_and_update_existing_global_template_name(rsp: StandardResponse) -> None:
    templates = validate_existing_template_name(rsp)
    if not templates:
        return
    validate_ownership(templates[0], rsp)
    rsp.body.description = templates[0].description
    rsp.body.owner = templates[0].owner
    rsp.body.test_data_links = templates[0].test_data_links
    if any(template.global_name == rsp.body.global_name for template in templates):
        rsp.error = True
        rsp.error_fields.global_name = f"Global name {rsp.body.global_name} already exists."
    return


def validate_and_update_pnr_fields(rsp: StandardResponse) -> None:
    rsp.body.field_data_item = rsp.body.field_data
    body = rsp.body.__dict__
    errors: dict = validate_and_update_pnr_text_with_field(body)
    if errors:
        rsp.error = True
        rsp.error_fields.field_data = errors.get("field_data_item", str())
        rsp.error_fields.text = errors.get("text", str())
        return
    rsp.body.text = body["original_text"]
    rsp.body.field_data = body["original_field_data_item"]
    rsp.body.type = PNR
    return


def validate_and_update_global_fields(rsp: StandardResponse) -> None:
    rsp.body.global_name = rsp.body.global_name.strip().upper()
    if not rsp.body.global_name or not get_global_ref(rsp.body.global_name):
        rsp.error = True
        rsp.error_fields.global_name = "This global name does not exists in global definitions."
    validate_and_update_global_data_template(rsp)
    return


def validate_and_update_global_data_template(rsp: StandardResponse) -> None:
    body = rsp.body.__dict__
    errors: dict = validate_and_update_global_data(body)
    if errors:
        rsp.error = True
        rsp.error_fields.field_data = errors.get("field_data", str())
        rsp.error_fields.hex_data = errors.get("hex_data", str())
        rsp.error_fields.seg_name = errors.get("seg_name", str())
        rsp.error_fields.is_global_record = errors.get("is_global_record", str())
        return
    rsp.body.hex_data = body["original_hex_data"]
    rsp.body.field_data = body["original_field_data"]
    rsp.body.seg_name = body["seg_name"]
    rsp.body.is_global_record = body["is_global_record"]
    rsp.body.type = GLOBAL
    return


def validate_and_update_aaa_fields(rsp: StandardResponse) -> None:
    body = rsp.body.__dict__
    errors = validate_and_update_macro_field_data(body, AAA_MACRO_NAME)
    if errors:
        rsp.error = True
        rsp.error_fields.field_data = errors.get("field_data", str())
        return
    rsp.body.field_data = body["original_field_data"]
    rsp.body.type = AAA
    return


def add_test_data_link_to_template(test_data: TestData, templates: List[Template]):
    for template in templates:
        if test_data.id not in template.test_data_links:
            template.test_data_links.append(test_data.id)
    return


def remove_test_data_link_from_template(test_data: TestData, templates: List[Template]):
    if any(element for element in test_data.ref(TD_REF[templates[0].type]) if element.link == templates[0].name):
        return
    for template in templates:
        if test_data.id in template.test_data_links:
            template.test_data_links.remove(test_data.id)
    return


def get_templates_for_rename_copy(rsp: StandardResponse) -> List[Template]:
    rsp.error_fields.name = str()
    rsp.body.name = rsp.body.old_name
    templates: List[Template] = validate_existing_template_name(rsp)
    rsp.error_fields.old_name = rsp.error_fields.name
    return templates
