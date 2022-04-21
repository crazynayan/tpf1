from typing import List, Tuple

from p3_db.template_models import Template, PNR, GLOBAL, AAA, AAA_MACRO_NAME
from p3_db.template_validators import remove_test_data_link_from_template, add_test_data_link_to_template
from p3_db.test_data import TestData
from p3_db.test_data_elements import Pnr, Core


def validate_template_test_data(test_data: TestData, body: dict, template_type) -> Tuple[dict, List[Template]]:
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"variation", "variation_name", "template_name"}:
        response["message"] = "Only 3 fields allowed (variation, variation_name, template_name) and all are mandatory."
        return response, list()
    variation_type = "pnr" if template_type == PNR else "core"
    if not test_data.validate_and_update_variation(body, variation_type):
        response["error_fields"]["variation"] = "Invalid variation."
    templates: List[Template] = Template.objects.filter_by(name=body["template_name"]).get()
    if not templates:
        response["error_fields"]["template_name"] = f"Template with this name not found."
    elif any(template.type != template_type for template in templates):
        response["error_fields"]["template_name"] = f"Template is NOT a {template_type} template"
    return response, templates


def merge_pnr_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, PNR)
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


def merge_global_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, GLOBAL)
    if response["error_fields"] or response["message"]:
        return response
    if any(template.global_name == td_pnr.global_name and td_pnr.variation == body["variation"]
           for template in templates for td_pnr in test_data.cores):
        response["error_fields"]["template_name"] = f"Template cannot be merged since same globals already exists in " \
                                                    f"the test data."
        return response
    for template in templates:
        create_body: dict = {"variation": body["variation"], "variation_name": body["variation_name"],
                             "global_name": template.global_name, "is_global_record": template.is_global_record,
                             "hex_data": template.hex_data, "seg_name": template.seg_name,
                             "field_data": template.field_data}
        td_response = test_data.create_global(create_body, persistence=False)
        if td_response["error"]:
            response["message"] = td_response["message"]
            for _, error_msg in td_response["error_fields"].items():
                response["message"] += error_msg
            return response
    for core in test_data.cores:
        if not core.id:
            core.create()
    test_data.save()
    response["message"] = f"Global template merged with the test data successfully."
    response["error"] = False
    return response


def merge_aaa_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, AAA)
    if response["error_fields"] or response["message"]:
        return response
    if any(core.macro_name == AAA_MACRO_NAME and core.variation == body["variation"] for core in test_data.cores):
        response["error_fields"]["template_name"] = f"Template cannot be merged since same AAA already exists in " \
                                                    f"the test data."
        return response
    for template in templates:
        create_body: dict = {"variation": body["variation"], "variation_name": body["variation_name"],
                             "field_data": template.field_data, "macro_name": AAA_MACRO_NAME}
        td_response = test_data.create_macro(create_body, persistence=False)
        if td_response["error"]:
            response["message"] = td_response["message"]
            for _, error_msg in td_response["error_fields"].items():
                response["message"] += error_msg
            return response
    for core in test_data.cores:
        if not core.id:
            core.create()
    test_data.save()
    response["message"] = f"AAA template merged with the test data successfully."
    response["error"] = False
    return response


def create_link_pnr_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, PNR)
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
    add_test_data_link_to_template(test_data, templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template linked successfully."
    response["error"] = False
    return response


def create_link_global_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, GLOBAL)
    if response["error_fields"] or response["message"]:
        return response
    if any(core.global_name == GLOBAL and core.link and core.variation == body["variation"]
           for core in test_data.cores):
        response["error_fields"]["template_name"] = f"There is already one global template linked with this variation."
        return response
    create_body = {"variation": body["variation"], "variation_name": body["variation_name"],
                   "global_name": GLOBAL, "link": body["template_name"]}
    core: Core = Core.dict_to_doc(create_body)
    test_data.cores.append(core)
    core.create()
    test_data.save()
    add_test_data_link_to_template(test_data, templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template linked successfully."
    response["error"] = False
    return response


def create_link_aaa_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, AAA)
    if response["error_fields"] or response["message"]:
        return response
    if any(core.macro_name == AAA_MACRO_NAME and core.link and core.variation == body["variation"]
           for core in test_data.cores):
        response["error_fields"]["template_name"] = f"There is already one AAA template linked with this variation."
        return response
    create_body = {"variation": body["variation"], "variation_name": body["variation_name"],
                   "macro_name": AAA_MACRO_NAME, "link": body["template_name"]}
    core: Core = Core.dict_to_doc(create_body)
    test_data.cores.append(core)
    core.create()
    test_data.save()
    add_test_data_link_to_template(test_data, templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template linked successfully."
    response["error"] = False
    return response


def update_link_pnr_template(test_data: TestData, body: dict):
    new_template_name = body["variation_name"]
    response, templates = validate_template_test_data(test_data, body, PNR)
    if response["error_fields"] or response["message"]:
        return response
    td_pnr = next((td_pnr for td_pnr in test_data.pnr if td_pnr.locator == templates[0].locator
                   and td_pnr.link == templates[0].name and td_pnr.variation == body["variation"]), None)
    if not td_pnr:
        response["error_fields"]["template_name"] = f"No template linked with this name."
    new_templates: List[Template] = Template.objects.filter_by(name=new_template_name).get()
    if not new_templates:
        response["message"] = f"No template found with the new template name."
    elif new_templates[0].type != PNR:
        response["message"] = f"Only PNR templates can be linked."
    if response["error_fields"] or response["message"]:
        return response
    response["error"] = False
    if templates[0].name == new_templates[0].name:
        response["message"] = f"Template link is the same. No changes made"
        return response
    td_pnr.link = new_template_name
    td_pnr.locator = new_templates[0].locator
    td_pnr.save()
    remove_test_data_link_from_template(test_data, templates)
    add_test_data_link_to_template(test_data, new_templates)
    templates.extend(new_templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template link updated successfully."
    return response


def update_link_global_template(test_data: TestData, body: dict):
    new_template_name = body["variation_name"]
    response, templates = validate_template_test_data(test_data, body, GLOBAL)
    if response["error_fields"] or response["message"]:
        return response
    core = next((core for core in test_data.cores if core.global_name == GLOBAL
                 and core.link == templates[0].name and core.variation == body["variation"]), None)
    if not core:
        response["error_fields"]["template_name"] = f"No template linked with this name."
    new_templates: List[Template] = Template.objects.filter_by(name=new_template_name).get()
    if not new_templates:
        response["message"] = f"No template found with the new template name."
    elif new_templates[0].type != GLOBAL:
        response["message"] = f"Only Global templates can be linked."
    if response["error_fields"] or response["message"]:
        return response
    response["error"] = False
    if templates[0].name == new_templates[0].name:
        response["message"] = f"Template link is the same. No changes made"
        return response
    core.link = new_template_name
    core.save()
    remove_test_data_link_from_template(test_data, templates)
    add_test_data_link_to_template(test_data, new_templates)
    templates.extend(new_templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template link updated successfully."
    return response


def update_link_aaa_template(test_data: TestData, body: dict):
    new_template_name = body["variation_name"]
    response, templates = validate_template_test_data(test_data, body, AAA)
    if response["error_fields"] or response["message"]:
        return response
    core = next((core for core in test_data.cores if core.macro_name == AAA_MACRO_NAME
                 and core.link == templates[0].name and core.variation == body["variation"]), None)
    if not core:
        response["error_fields"]["template_name"] = f"No template linked with this name."
    new_templates: List[Template] = Template.objects.filter_by(name=new_template_name).get()
    if not new_templates:
        response["message"] = f"No template found with the new template name."
    elif new_templates[0].type != AAA:
        response["message"] = f"Only AAA templates can be linked."
    if response["error_fields"] or response["message"]:
        return response
    response["error"] = False
    if templates[0].name == new_templates[0].name:
        response["message"] = f"Template link is the same. No changes made"
        return response
    core.link = new_template_name
    core.save()
    remove_test_data_link_from_template(test_data, templates)
    add_test_data_link_to_template(test_data, new_templates)
    templates.extend(new_templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template link updated successfully."
    return response


def delete_link_pnr_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, PNR)
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
    remove_test_data_link_from_template(test_data, templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template link deleted successfully."
    response["error"] = False
    return response


def delete_link_global_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, GLOBAL)
    if response["error_fields"] or response["message"]:
        return response
    core = next((core for core in test_data.cores if core.global_name == GLOBAL
                 and core.link == templates[0].name and core.variation == body["variation"]), None)
    if not core:
        response["error_fields"]["message"] = f"No template linked with this name."
        return response
    test_data.cores.remove(core)
    core.delete()
    test_data.save()
    remove_test_data_link_from_template(test_data, templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template link deleted successfully."
    response["error"] = False
    return response


def delete_link_aaa_template(test_data: TestData, body: dict):
    response, templates = validate_template_test_data(test_data, body, AAA)
    if response["error_fields"] or response["message"]:
        return response
    core = next((core for core in test_data.cores if core.macro_name == AAA_MACRO_NAME
                 and core.link == templates[0].name and core.variation == body["variation"]), None)
    if not core:
        response["error_fields"]["message"] = f"No template linked with this name."
        return response
    test_data.cores.remove(core)
    core.delete()
    test_data.save()
    remove_test_data_link_from_template(test_data, templates)
    Template.objects.save_all(templates)
    response["message"] = f"Template link deleted successfully."
    response["error"] = False
    return response
