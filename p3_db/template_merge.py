from typing import List, Tuple

from p3_db.template_models import Template, PNR
from p3_db.test_data import TestData
from p3_db.test_data_elements import Pnr


def validate_pnr_template_test_data(test_data: TestData, body: dict) -> Tuple[dict, List[Template]]:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"variation", "variation_name", "template_name"}:
        response["message"] = "Only 3 fields allowed (variation, variation_name, template_name) and all are mandatory."
        return response, list()
    if not test_data.validate_and_update_variation(body, "pnr"):
        response["error_fields"]["variation"] = "Invalid variation."
    templates: List[Template] = Template.objects.filter_by(name=body["template_name"]).get()
    if not templates:
        response["error_fields"]["template_name"] = f"Template with this name not found."
    elif any(template.type != PNR for template in templates):
        response["error_fields"]["template_name"] = f"Template is NOT a PNR template"
    return response, templates


def merge_pnr_template(test_data: TestData, body: dict):
    response, templates = validate_pnr_template_test_data(test_data, body)
    if response["error_fields"] or response["message"]:
        return response
    if any(template.key == td_pnr.key for template in templates for td_pnr in test_data.pnr
           if td_pnr.locator == template.locator and td_pnr.variation == body["variation"]):
        response["error_fields"]["template_name"] = f"Template cannot be merged since some keys already exists in " \
                                                    f"the test data."
        return response
    for template in templates:
        create_body: dict = {"variation": body["variation"], "variation_name": body["variation_name"],
                             "locator": template.locator, "key": template.key, "text": template.text,
                             "field_data_item": template.field_data}
        td_response = test_data.create_pnr_input(create_body, persistence=False)
        if td_response["error"]:
            response["message"] = td_response["message"]
            for _, error_msg in td_response["error_fields"].items():
                response["message"] += error_msg
            return response
    for pnr_input in test_data.pnr:
        if not pnr_input.id:
            pnr_input.create()
    test_data.save()
    response["message"] = f"PNR template merged with the test data successfully."
    response["error"] = False
    return response


def create_link_pnr_template(test_data: TestData, body: dict):
    response, templates = validate_pnr_template_test_data(test_data, body)
    if response["error_fields"] or response["message"]:
        return response
    if any(td_pnr.locator == templates[0].locator and td_pnr.link and td_pnr.variation == body["variation"]
           for td_pnr in test_data.pnr):
        response["error_fields"]["template_name"] = f"There is already one template linked with this locator."
        return response
    create_body = {"variation": body["variation"], "variation_name": body["variation_name"],
                   "locator": templates[0].locator, "link": body["template_name"]}
    pnr_input: Pnr = Pnr.dict_to_doc(create_body)
    test_data.pnr.append(pnr_input)
    pnr_input.create()
    test_data.save()
    for template in templates:
        if test_data.id not in template.test_data_links:
            template.test_data_links.append(test_data.id)
    Template.objects.save_all(templates)
    response["message"] = f"Template linked successfully."
    response["error"] = False
    return response


def update_link_pnr_template(test_data: TestData, body: dict):
    new_template_name = body["variation_name"]
    response, templates = validate_pnr_template_test_data(test_data, body)
    if response["error_fields"] or response["message"]:
        return response
    td_pnr = next((td_pnr for td_pnr in test_data.pnr if td_pnr.locator == templates[0].locator
                   and td_pnr.link == templates[0].name and td_pnr.variation == body["variation"]), None)
    if not td_pnr:
        response["error_fields"]["template_name"] = f"No template linked with this name."
    new_templates: List[Template] = Template.objects.filter_by(name=new_template_name).get()
    if not new_templates:
        response["error_fields"]["new_template_name"] = f"No template found with this name."
    if response["error_fields"]:
        return response
    response["error"] = False
    if templates[0].name == new_templates[0].name:
        response["message"] = f"Template link is the same. No changes made"
        return response
    td_pnr.link = new_template_name
    td_pnr.locator = new_templates[0].locator
    td_pnr.save()
    for template in templates:
        if test_data.id in template.test_data_links:
            template.test_data_links.remove(test_data.id)
    for template in new_templates:
        if test_data.id not in template.test_data_links:
            template.test_data_links.append(test_data.id)
    templates.extend(new_templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template link updated successfully."
    return response


def delete_link_pnr_template(test_data: TestData, body: dict):
    response, templates = validate_pnr_template_test_data(test_data, body)
    if response["error_fields"] or response["message"]:
        return response
    td_pnr = next((td_pnr for td_pnr in test_data.pnr if td_pnr.locator == templates[0].locator
                   and td_pnr.link == templates[0].name and td_pnr.variation == body["variation"]), None)
    if not td_pnr:
        response["error_fields"]["message"] = f"No template linked with this name."
        return response
    test_data.pnr.remove(td_pnr)
    td_pnr.delete()
    test_data.save()
    for template in templates:
        if test_data.id in template.test_data_links:
            template.test_data_links.remove(test_data.id)
    Template.objects.save_all(templates)
    response["message"] = f"Template link deleted successfully."
    response["error"] = False
    return response
