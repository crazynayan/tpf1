from itertools import groupby
from typing import List

from p3_db.template_models import Template, get_template_by_id
from p3_db.template_validators import validate_and_update_new_template_name, \
    validate_and_update_existing_pnr_template_name, validate_and_update_pnr_fields, validate_template_name
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
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"old_name", "new_name", "description"}:
        response["message"] = "Only 3 fields allowed (old_name, new_name, description) and all are mandatory."
        return response
    body["name"] = body["old_name"]
    errors = validate_template_name(body)
    if errors:
        response["error_fields"]["old_name"] = errors["name"]
        return response
    templates: List[Template] = Template.objects.filter_by(name=body["old_name"]).get()
    if not templates:
        response["error_fields"]["old_name"] = "No template found with this name."
        return response
    if body["old_name"] != body["new_name"]:
        body["name"] = body["new_name"]
        errors = validate_and_update_new_template_name(body)
        if errors:
            response["error_fields"]["new_name"] = errors["name"]
            return response
        for template in templates:
            template.name = body["new_name"]
    for template in templates:
        template.description = body["description"]
    Template.objects.save_all(templates)
    response["message"] = f"Template renamed successfully."
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
    success: str = Template.objects.filter_by(name=body["name"]).delete()
    if not success:
        response["message"] = "No PNR template with this name found."
        response["error_fields"]["name"] = response["message"]
        return response
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
