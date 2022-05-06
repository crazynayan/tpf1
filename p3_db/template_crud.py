from copy import copy
from itertools import groupby
from typing import List

from p3_db.response import StandardResponse, RequestType
from p3_db.template_models import Template, get_template_by_id, TD_REF, validate_and_get_template_by_id, \
    validate_ownership
from p3_db.template_validators import validate_and_update_new_template_name, \
    validate_and_update_existing_pnr_template_name, validate_and_update_global_fields, \
    validate_and_update_existing_global_template_name, validate_and_update_pnr_fields, \
    validate_and_update_global_data_template, validate_and_update_aaa_fields, get_templates_for_rename_copy, \
    validate_existing_template_name
from p3_db.test_data_get import get_whole_test_data
from p3_db.test_data_validators import validate_pnr_key, \
    validate_and_update_pnr_locator


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
        template_dict["count"] = len(template_list)
    return template_dicts


def get_templates_by_name(name: str) -> List[dict]:
    templates: List[Template] = Template.objects.filter_by(name=name).get()
    return Template.objects.to_dicts(templates)


def get_templates_by_id(template_id: str) -> dict:
    template = get_template_by_id(template_id)
    if not template:
        return dict()
    return Template.objects.to_dicts([template])[0]


def rename_template(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_RENAME_COPY)
    if rsp.error:
        return rsp.dict
    templates = get_templates_for_rename_copy(rsp)
    if rsp.body.old_name != rsp.body.new_name:
        rsp.body.name = rsp.body.new_name
        validate_and_update_new_template_name(rsp)
        rsp.error_fields.new_name = rsp.error_fields.name
    if not templates:
        return rsp.dict
    validate_ownership(templates[0], rsp)
    test_data_list = [get_whole_test_data(test_data_id, link=False) for test_data_id in templates[0].test_data_links]
    if any(test_data is None for test_data in test_data_list):
        rsp.error = True
        rsp.message = "Template to Test Data link corrupted."
    if rsp.error:
        return rsp.dict
    if rsp.body.old_name != rsp.body.new_name:
        for template in templates:
            template.name = rsp.body.new_name
        td_elements = [element for test_data in test_data_list for element in test_data.ref(TD_REF[templates[0].type])
                       if element.link == rsp.body.old_name]
        for td_element in td_elements:
            td_element.link = rsp.body.new_name
        if td_elements:
            td_elements[0].__class__.objects.save_all(td_elements)
    for template in templates:
        template.description = body["description"]
    Template.objects.save_all(templates)
    rsp.message = f"Template renamed successfully."
    return rsp.dict


def copy_template(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_RENAME_COPY)
    if rsp.error:
        return rsp.dict
    templates = get_templates_for_rename_copy(rsp)
    rsp.body.name = rsp.body.new_name
    validate_and_update_new_template_name(rsp)
    rsp.error_fields.new_name = rsp.error_fields.name
    if rsp.error:
        return rsp.dict
    new_templates: List[Template] = list()
    for template in templates:
        new_template: Template = copy(template)
        new_template.name = rsp.body.new_name
        new_template.description = rsp.body.description
        new_template.owner = rsp.body.owner
        new_template.test_data_links = list()
        new_templates.append(new_template)
    Template.objects.create_all(Template.objects.to_dicts(new_templates))
    rsp.message = f"Template copied successfully."
    return rsp.dict


def delete_template_by_id(template_id: str) -> dict:
    rsp: StandardResponse = StandardResponse()
    template = validate_and_get_template_by_id(template_id, rsp)  # validates ownership
    if not template:
        return rsp.dict
    templates: List[Template] = Template.objects.filter_by(name=template.name).get()
    if len(templates) <= 1:
        rsp.error = True
        rsp.message = "Cannot delete the last template by id. Use delete template by name."
    if rsp.error:
        return rsp.dict
    template.delete()
    rsp.message = f"Template element deleted successfully."
    return rsp.dict


def delete_template_by_name(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_DELETE)
    if rsp.error:
        return rsp.dict
    templates = validate_existing_template_name(rsp)
    rsp.message = rsp.error_fields.name
    if not templates:
        return rsp.dict
    validate_ownership(templates[0], rsp)
    if templates[0].test_data_links:
        rsp.message = "Cannot delete a template with links."
        rsp.error = True
    if rsp.error:
        return rsp.dict
    Template.objects.filter_by(name=rsp.body.name).delete()
    rsp.message = f"Template named {body['name']} deleted successfully."
    return rsp.dict


def create_new_pnr_template(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_PNR_CREATE)
    if rsp.error:
        return rsp.dict
    validate_and_update_new_template_name(rsp)  # Updates owner
    validate_and_update_pnr_locator(rsp)
    validate_pnr_key(rsp)
    validate_and_update_pnr_fields(rsp)  # Updates type
    if rsp.error:
        return rsp.dict
    Template.create_from_dict(rsp.body.__dict__)
    rsp.message = f"PNR element for key {rsp.body.key.upper()} created successfully."
    return rsp.dict


def create_new_global_template(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_GLOBAL_CREATE)
    if rsp.error:
        return rsp.dict
    validate_and_update_new_template_name(rsp)  # Updates owner
    validate_and_update_global_fields(rsp)  # Updates type
    if rsp.error:
        return rsp.dict
    Template.create_from_dict(rsp.body.__dict__)
    rsp.message = f"Global template for global {rsp.body.global_name} created successfully."
    return rsp.dict


def create_new_aaa_template(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_AAA_CREATE)
    if rsp.error:
        return rsp.dict
    validate_and_update_new_template_name(rsp)  # Updates owner
    validate_and_update_aaa_fields(rsp)  # Updates type
    if rsp.error:
        return rsp.dict
    Template.create_from_dict(rsp.body.__dict__)
    rsp.message = f"AAA template created successfully."
    return rsp.dict


def add_to_existing_pnr_template(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_PNR_ADD)
    if rsp.error:
        return rsp.dict
    validate_and_update_existing_pnr_template_name(rsp)  # validates ownership
    validate_pnr_key(rsp)
    validate_and_update_pnr_fields(rsp)
    if rsp.error:
        return rsp.dict
    Template.create_from_dict(rsp.body.__dict__)
    rsp.message = f"PNR element for key {rsp.body.key.upper()} added successfully."
    return rsp.dict


def add_to_existing_global_template(body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_GLOBAL_ADD)
    if rsp.error:
        return rsp.dict
    validate_and_update_existing_global_template_name(rsp)  # validates ownership
    validate_and_update_global_data_template(rsp)
    if rsp.error:
        return rsp.dict
    Template.create_from_dict(rsp.body.__dict__)
    rsp.message = f"Global template for global {rsp.body.global_name} added successfully."
    return rsp.dict


def update_pnr_template(template_id, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_PNR_UPDATE)
    if rsp.error:
        return rsp.dict
    template = validate_and_get_template_by_id(template_id, rsp)  # validates ownership
    validate_and_update_pnr_fields(rsp)
    if rsp.error:
        return rsp.dict
    template.text = rsp.body.text
    template.field_data = rsp.body.field_data
    template.save()
    rsp.message = f"PNR element for key {template.key.upper()} updated successfully."
    return rsp.dict


def update_global_template(template_id: str, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_GLOBAL_UPDATE)
    if rsp.error:
        return rsp.dict
    template = validate_and_get_template_by_id(template_id, rsp)  # validates ownership
    validate_and_update_global_data_template(rsp)
    if rsp.error:
        return rsp.dict
    template.hex_data = rsp.body.hex_data
    template.field_data = rsp.body.field_data
    template.is_global_record = rsp.body.is_global_record
    template.seg_name = rsp.body.seg_name
    template.save()
    rsp.message = f"Global template for global {template.global_name} updated successfully."
    return rsp.dict


def update_aaa_template(template_id: str, body: dict) -> dict:
    rsp: StandardResponse = StandardResponse(body, RequestType.TEMPLATE_AAA_UPDATE)
    if rsp.error:
        return rsp.dict
    template = validate_and_get_template_by_id(template_id, rsp)  # validates ownership
    validate_and_update_aaa_fields(rsp)
    if rsp.error:
        return rsp.dict
    template.field_data = rsp.body.field_data
    template.save()
    rsp.message = f"AAA template updated successfully."
    return rsp.dict


def get_variations(test_data_id: str, v_type: str) -> list:
    test_data = get_whole_test_data(test_data_id, link=False)
    variations = {(element.variation, element.variation_name) for element in test_data.ref(v_type)}
    variation_list = list(variations)
    variation_list.append((-1, "New Variation"))
    return variation_list
