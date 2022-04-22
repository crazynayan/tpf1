from copy import copy
from itertools import groupby
from typing import List

from p3_db.template_models import Template, get_template_by_id, TD_REF, validate_and_get_template_by_id
from p3_db.template_validators import validate_and_update_new_template_name, \
    validate_and_update_existing_pnr_template_name, old_validate_and_update_pnr_fields, \
    validate_and_update_template_rename_copy, validate_and_update_global_fields, \
    validate_and_update_existing_global_template_name, validate_and_update_aaa_fields, validate_and_update_pnr_fields
from p3_db.test_data import TestData
from p3_db.test_data_get import get_whole_test_data
from p3_db.test_data_validators import validate_and_update_pnr_locator_key, validate_and_update_global_data
from p7_flask_app.response import StandardResponse, RequestType


def get_templates_by_type(template_type: str) -> List[dict]:
    templates: List[Template] = Template.objects.filter_by(type=template_type).get()
    if not templates:
        return list()
    templates.sort(key=lambda item: item.name)
    template_dicts: List[dict] = list()
    for name, template_group in groupby(templates, key=lambda item: item.name):
        template_list = list(template_group)
        template_dict = Template.objects.to_dicts([template_list[0]])[0]
        template_dicts.append(template_dict)
        # template_dict["all_templates"] = Template.objects.to_dicts(template_list)
        template_dict["count"] = len(template_list)
    return template_dicts


def get_templates_by_name(name: str) -> List[dict]:
    templates: List[Template] = Template.objects.filter_by(name=name).get()
    return Template.objects.to_dicts(templates)


def get_templates_by_id(template_id: str) -> dict:
    template, _ = get_template_by_id(template_id)
    if not template:
        return dict()
    return Template.objects.to_dicts([template])[0]


def rename_template(body: dict) -> dict:
    response, templates = validate_and_update_template_rename_copy(body)
    if not templates:
        return response
    if body["old_name"] != body["new_name"]:
        body["name"] = body["new_name"]
        errors = validate_and_update_new_template_name(body)
        if errors:
            response["error_fields"]["new_name"] = errors["name"]
            return response
        test_data_list: List[TestData] = [get_whole_test_data(test_data_id, link=False)
                                          for test_data_id in templates[0].test_data_links]
        if any(test_data is None for test_data in test_data_list):
            response["error_fields"]["message"] = "Template to Test Data link corrupted."
            return response
        for template in templates:
            template.name = body["new_name"]
        td_elements = [element for test_data in test_data_list for element in test_data.ref(TD_REF[templates[0].type])
                       if element.link == body["old_name"]]
        for td_element in td_elements:
            td_element.link = body["new_name"]
        if td_elements:
            td_elements[0].__class__.objects.save_all(td_elements)
    for template in templates:
        template.description = body["description"]
    Template.objects.save_all(templates)
    response["message"] = f"Template renamed successfully."
    response["error"] = False
    return response


def copy_template(body: dict) -> dict:
    response, templates = validate_and_update_template_rename_copy(body)
    if not templates:
        return response
    body["name"] = body["new_name"]
    errors = validate_and_update_new_template_name(body)
    if errors:
        response["error_fields"]["new_name"] = errors["name"]
        return response
    new_templates: List[Template] = list()
    for template in templates:
        new_template: Template = copy(template)
        new_template.name = body["new_name"]
        new_template.description = body["description"]
        new_template.owner = body["owner"]
        new_template.test_data_links = list()
        new_templates.append(new_template)
    Template.objects.create_all(Template.objects.to_dicts(new_templates))
    response["message"] = f"Template copied successfully."
    response["error"] = False
    return response


def delete_template_by_id(template_id: str) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    template, error_msg = get_template_by_id(template_id)
    if error_msg:
        response["message"] = error_msg
        return response
    templates: List[Template] = Template.objects.filter_by(name=template.name).get()
    if len(templates) <= 1:
        response["message"] = "Cannot delete the last template by id. Use delete template by name."
        return response
    template.delete()
    response["message"] = f"Template element deleted successfully."
    response["error"] = False
    return response


def delete_template_by_name(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"name"}:
        response["message"] = "Only 1 fields allowed (name) and it is mandatory."
        return response
    template: Template = Template.objects.filter_by(name=body["name"]).first()
    if not template:
        response["message"] = "No PNR template with this name found."
        return response
    if template.test_data_links:
        response["message"] = "Cannot delete a template with links."
        return response
    Template.objects.filter_by(name=body["name"]).delete()
    response["message"] = f"Template named {body['name']} deleted successfully."
    response["error"] = False
    return response


def create_new_pnr_template(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"name", "description", "key", "field_data", "text", "locator"}:
        response["message"] = "Only 6 fields allowed (name, description, key, locator, text, field_data) " \
                              "and all are mandatory."
        return response
    errors = validate_and_update_new_template_name(body)  # Updates owner
    if errors:
        response["error_fields"] = errors
    errors = validate_and_update_pnr_locator_key(body)
    if errors:
        response["error_fields"] = {**response["error_fields"], **errors}
    errors = old_validate_and_update_pnr_fields(body)  # This will update the template type as PNR
    if errors or response["error_fields"]:
        response["error_fields"] = {**response["error_fields"], **errors}
        return response
    Template.create_from_dict(body)
    response["message"] = f"PNR template for key {body['key'].upper()} created successfully."
    response["error"] = False
    return response


def create_new_global_template(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"name", "description", "global_name", "hex_data", "field_data", "seg_name", "is_global_record"}:
        response["message"] = "Only 7 fields allowed (name, description, global_name, hex_data, field_data, seg_name" \
                              "is_global_record) and all are mandatory."
        return response
    errors = validate_and_update_new_template_name(body)  # Updates owner
    if errors:
        response["error_fields"] = errors
    errors = validate_and_update_global_fields(body)  # This will update the template type as Global
    if errors or response["error_fields"]:
        response["error_fields"] = {**response["error_fields"], **errors}
        return response
    Template.create_from_dict(body)
    response["message"] = f"Global template for global {body['global_name']} created successfully."
    response["error"] = False
    return response


def create_new_aaa_template(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"name", "description", "field_data"}:
        response["message"] = "Only 3 fields allowed (name, description, field_data) and all are mandatory."
        return response
    errors = validate_and_update_new_template_name(body)  # Updates owner
    if errors:
        response["error_fields"] = errors
    errors = validate_and_update_aaa_fields(body)  # This will update the template type as AAA
    if errors or response["error_fields"]:
        response["error_fields"] = {**response["error_fields"], **errors}
        return response
    Template.create_from_dict(body)
    response["message"] = f"AAA template created successfully."
    response["error"] = False
    return response


def add_to_existing_pnr_template(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"name", "key", "field_data", "text"}:
        response["message"] = "Only 4 fields allowed (name, key, text, field_data) and all are mandatory."
        return response
    body["locator"] = str()  # This will be updated by validate_and_update_existing_pnr_template_name
    errors = validate_and_update_pnr_locator_key(body)
    if errors:
        response["error_fields"] = errors
    errors = validate_and_update_existing_pnr_template_name(body)
    if errors:
        response["error_fields"] = {**response["error_fields"], **errors}
    errors = old_validate_and_update_pnr_fields(body)
    if errors or response["error_fields"]:
        response["error_fields"] = {**response["error_fields"], **errors}
        return response
    Template.create_from_dict(body)
    response["message"] = f"PNR element for key {body['key'].upper()} created successfully."
    response["error"] = False
    return response


def add_to_existing_global_template(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"name", "global_name", "hex_data", "field_data", "seg_name", "is_global_record"}:
        response["message"] = "Only 6 fields allowed (name, global_name, hex_data, field_data, seg_name, " \
                              "is_global_record) and all are mandatory."
        return response
    errors = validate_and_update_existing_global_template_name(body)
    if errors:
        response["error_fields"] = errors
    errors = validate_and_update_global_fields(body)  # This will update the template type as Global
    if errors or response["error_fields"]:
        response["error_fields"] = {**response["error_fields"], **errors}
        return response
    Template.create_from_dict(body)
    response["message"] = f"Global template for global {body['global_name']} created successfully."
    response["error"] = False
    return response


def update_pnr_template(template_id, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_PNR_UPDATE)
    if rsp.error:
        return rsp.dict
    template = validate_and_get_template_by_id(template_id, rsp)
    validate_and_update_pnr_fields(rsp)
    if rsp.error:
        return rsp.dict
    template.text = rsp.body.text
    template.field_data = rsp.body.field_data
    template.save()
    rsp.message = f"PNR element for key {template.key.upper()} updated successfully."
    return rsp.dict


def update_global_template(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"id", "hex_data", "field_data", "seg_name", "is_global_record"}:
        response["message"] = "Only 5 fields allowed (id, hex_data, field_data, seg_name, is_global_record) " \
                              "and all are mandatory."
        return response
    template, error_msg = get_template_by_id(body["id"])
    if error_msg:
        response["error_fields"]["message"] = error_msg
        return response
    errors = validate_and_update_global_data(body)
    if errors:
        response["error_fields"] = errors
        return response
    template.hex_data = body["original_hex_data"]
    template.field_data = body["original_field_data"]
    template.is_global_record = body["is_global_record"]
    template.seg_name = body["seg_name"]
    template.save()
    response["message"] = f"Global template for global {template.global_name} updated successfully."
    response["error"] = False
    return response


def update_aaa_template(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"id", "field_data"}:
        response["message"] = "Only 2 fields allowed (id, field_data) and all are mandatory."
        return response
    template, error_msg = get_template_by_id(body["id"])
    if error_msg:
        response["error_fields"]["message"] = error_msg
        return response
    errors = validate_and_update_aaa_fields(body)
    if errors:
        response["error_fields"] = errors
        return response
    template.field_data = body["original_field_data"]
    template.save()
    response["message"] = f"AAA template updated successfully."
    response["error"] = False
    return response
