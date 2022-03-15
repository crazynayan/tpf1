from itertools import groupby
from typing import List

from p3_db.template_models import Template, get_template_by_id
from p3_db.template_validators import validate_and_update_new_template_name, \
    validate_and_update_existing_pnr_template_name, validate_and_update_pnr_fields, \
    validate_and_update_template_rename_copy
from p3_db.test_data import TestData
from p3_db.test_data_elements import Pnr
from p3_db.test_data_get import get_whole_test_data
from p3_db.test_data_validators import validate_and_update_pnr_locator_key


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
        template_dict["all_templates"] = Template.objects.to_dicts(template_list)
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
        for template in templates:
            template.name = body["new_name"]
        updated_pnr_list = list()
        for test_data_id in templates[0].test_data_links:
            test_data: TestData = get_whole_test_data(test_data_id, link=False)
            pnr_list: List[Pnr] = [pnr for pnr in test_data.pnr if pnr.link == body["old_name"]]
            for pnr in pnr_list:
                pnr.link = body["new_name"]
            updated_pnr_list.extend(pnr_list)
        if updated_pnr_list:
            Pnr.objects.save_all(updated_pnr_list)
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
        new_template: Template = Template()
        new_templates.append(new_template)
        new_template.name = body["new_name"]
        new_template.description = body["description"]
        new_template.owner = body["owner"]
        new_template.locator = template.locator
        new_template.key = template.key
        new_template.text = template.text
        new_template.field_data = template.field_data
        new_template.type = template.type
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
    errors = validate_and_update_pnr_fields(body)  # This will update the template type as PNR
    if errors or response["error_fields"]:
        response["error_fields"] = {**response["error_fields"], **errors}
        return response
    Template.create_from_dict(body)
    response["message"] = f"PNR template for key {body['key'].upper()} created successfully."
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
    errors = validate_and_update_pnr_fields(body)
    if errors or response["error_fields"]:
        response["error_fields"] = {**response["error_fields"], **errors}
        return response
    Template.create_from_dict(body)
    response["message"] = f"PNR element for key {body['key'].upper()} created successfully."
    response["error"] = False
    return response


def update_pnr_template(body: dict) -> dict:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"id", "field_data", "text"}:
        response["message"] = "Only 3 fields allowed (id, field_data and text) and all are mandatory."
        return response
    template, error_msg = get_template_by_id(body["id"])
    if error_msg:
        response["error_fields"]["message"] = error_msg
        return response
    errors = validate_and_update_pnr_fields(body)
    if errors:
        response["error_fields"] = errors
        return response
    template.text = body["text"]
    template.field_data = body["field_data"]
    template.save()
    response["message"] = f"PNR element for key {template.key.upper()} updated successfully."
    response["error"] = False
    return response
