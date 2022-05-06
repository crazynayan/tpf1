from typing import List

from p3_db.response import StandardResponse, RequestType
from p3_db.template_merge_validators import validate_and_update_variation, get_templates, get_new_templates, \
    validate_element_exists, get_create_request_body, validate_and_update_test_data, validate_link_exists, \
    get_link_create_body, get_test_data_element_from_body, add_test_data_link_to_template, \
    remove_test_data_link_from_template, get_test_data_element
from p3_db.template_models import Template, TEMPLATE_TYPES, TD_REF, MERGE, \
    LINK_CREATE, LINK_UPDATE, LINK_DELETE
from p3_db.test_data import TestData


def merge_template(test_data: TestData, body: dict, template_type: str) -> dict:
    rsp = StandardResponse(body, RequestType.TEMPLATE_MERGE_LINK)
    if rsp.error:
        return rsp.dict
    validate_and_update_variation(test_data, rsp, TD_REF[template_type])
    templates = get_templates(rsp, template_type)
    if rsp.error:
        return rsp.dict
    validate_element_exists(rsp, template_type, templates, test_data)
    if rsp.error:
        return rsp.dict
    for template in templates:
        create_body = get_create_request_body(rsp, template_type, template)
        validate_and_update_test_data(rsp, template_type, test_data, create_body)
        if rsp.error:
            return rsp.dict
    for element in test_data.ref(TD_REF[template_type]):
        if not element.id:
            element.create()
    test_data.save()
    rsp.message = f"{template_type} template merged with the test data successfully."
    return rsp.dict


def create_link_template(test_data: TestData, body: dict, template_type: str) -> dict:
    rsp = StandardResponse(body, RequestType.TEMPLATE_MERGE_LINK)
    if rsp.error:
        return rsp.dict
    validate_and_update_variation(test_data, rsp, TD_REF[template_type])
    templates = get_templates(rsp, template_type)
    if rsp.error:
        return rsp.dict
    validate_link_exists(rsp, template_type, templates[0], test_data)
    if rsp.error:
        return rsp.dict
    create_body = get_link_create_body(rsp, template_type, templates[0])
    td_doc = get_test_data_element_from_body(template_type, create_body)
    test_data.ref(TD_REF[template_type]).append(td_doc)
    td_doc.create()
    test_data.save()
    add_test_data_link_to_template(test_data, templates)
    Template.objects.save_all(templates)
    rsp.message = f"Template linked successfully."
    return rsp.dict


def update_link_template(test_data: TestData, body: dict, template_type: str):
    rsp = StandardResponse(body, RequestType.TEMPLATE_LINK_UPDATE)
    if rsp.error:
        return rsp.dict
    templates = get_templates(rsp, template_type)
    if rsp.error:
        return rsp.dict
    td_element = get_test_data_element(rsp, template_type, templates[0], test_data)
    new_templates: List[Template] = get_new_templates(rsp, template_type)
    if rsp.error:
        return rsp.dict
    if templates[0].name == new_templates[0].name:
        rsp.message = f"Template link is the same. No changes made"
        return rsp.dict
    td_element.link = rsp.body.new_template_name
    td_element.locator = new_templates[0].locator  # Only applicable for PNR template. Does not impact other templates.
    td_element.save()
    remove_test_data_link_from_template(test_data, templates)
    add_test_data_link_to_template(test_data, new_templates)
    templates.extend(new_templates)
    Template.objects.save_all(templates)
    rsp.message = f"Template link updated successfully."
    return rsp.dict


def delete_link_template(test_data: TestData, body: dict, template_type: str):
    rsp = StandardResponse(body, RequestType.TEMPLATE_LINK_DELETE)
    if rsp.error:
        return rsp.dict
    templates = get_templates(rsp, template_type)
    if rsp.error:
        return rsp.dict
    td_element = get_test_data_element(rsp, template_type, templates[0], test_data)
    if rsp.error:
        return rsp.dict
    test_data.ref(TD_REF[template_type]).remove(td_element)
    td_element.delete()
    test_data.save()
    remove_test_data_link_from_template(test_data, templates)
    Template.objects.save_all(templates)
    rsp.message = f"Template link deleted successfully."
    return rsp.dict


def process_merge_link(action_type: str, test_data: TestData, body: dict, template_type: str) -> dict:
    process = {
        MERGE: merge_template,
        LINK_CREATE: create_link_template,
        LINK_UPDATE: update_link_template,
        LINK_DELETE: delete_link_template,
    }
    rsp = StandardResponse()
    if action_type not in process:
        rsp.error = True
        rsp.message = "Invalid action type."
        return rsp.dict
    if template_type not in TEMPLATE_TYPES:
        rsp.error = True
        rsp.message = "Invalid template type."
        return rsp.dict
    return process[action_type](test_data, body, template_type)
