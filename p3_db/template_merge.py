from types import SimpleNamespace
from typing import List, Tuple, Callable

from p3_db.response import StandardResponse, RequestType
from p3_db.template_models import Template, PNR, GLOBAL, AAA, AAA_MACRO_NAME, TEMPLATE_TYPES, TD_REF, MERGE, \
    LINK_CREATE, LINK_UPDATE, LINK_DELETE
from p3_db.template_validators import remove_test_data_link_from_template, add_test_data_link_to_template
from p3_db.test_data import TestData, VALID_ELEMENT_TYPES
from p3_db.test_data_elements import Pnr, Core
from p3_db.test_data_get import get_whole_test_data


def validate_and_update_variation(test_data: TestData, rsp: StandardResponse, v_type: str) -> None:
    if v_type not in VALID_ELEMENT_TYPES:
        rsp.error = True
        rsp.message = "Invalid variation type."
        return
    td_element = next((element for element in test_data.ref(v_type) if element.variation == rsp.body.variation), None)
    if td_element:
        rsp.body.variation_name = td_element.variation_name
        return
    if test_data.ref(v_type):
        next_variation = max(element.variation for element in test_data.ref(v_type)) + 1
    else:
        next_variation = 0
    if rsp.body.variation == -1:
        rsp.body.variation = next_variation
    if not rsp.body.variation_name.strip():
        rsp.body.variation_name = f"Variation {next_variation + 1}"
    if rsp.body.variation != next_variation:
        rsp.error = True
        rsp.error_fields.variation = "Invalid variation."
    return


def get_templates(rsp: StandardResponse, template_type: str) -> List[Template]:
    if template_type not in TEMPLATE_TYPES:
        rsp.error = True
        rsp.message = "Invalid template type."
        return list()
    templates: List[Template] = Template.objects.filter_by(name=rsp.body.template_name).get()
    if not templates:
        rsp.error = True
        rsp.error_fields.template_name = "Template with this name not found."
    elif any(template.type != template_type for template in templates):
        rsp.error = True
        rsp.error_fields.template_name = f"Template is NOT a {template_type} template."
    return templates


def get_new_templates(rsp: StandardResponse, template_type: str) -> List[Template]:
    templates: List[Template] = Template.objects.filter_by(name=rsp.body.new_template_name).get()
    if not templates:
        rsp.error = True
        rsp.message = f"No template found with the new template name."
    elif templates[0].type != template_type:
        rsp.error = True
        rsp.message = f"Only {template_type} templates can be linked."
    return templates


def get_pnr_element(rsp: StandardResponse, test_data: TestData, template: Template) -> Pnr:
    td_pnr = next((td_pnr for td_pnr in test_data.pnr if td_pnr.locator == template.locator
                   and td_pnr.link == template.name and td_pnr.variation == rsp.body.variation), None)
    if not td_pnr:
        rsp.error = True
        rsp.error_fields.template_name = f"No template linked with this name."
    return td_pnr


def get_variations(test_data_id: str, v_type: str) -> list:
    test_data = get_whole_test_data(test_data_id, link=False)
    variations = {(element.variation, element.variation_name) for element in test_data.ref(v_type)}
    variation_list = list(variations)
    variation_list.append((-1, "New Variation"))
    return variation_list


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
    rsp = StandardResponse(body, RequestType.TEMPLATE_MERGE_LINK)
    if rsp.error:
        return rsp.dict
    validate_and_update_variation(test_data, rsp, TD_REF[PNR])
    templates = get_templates(rsp, PNR)
    if rsp.error:
        return rsp.dict
    if any(template.key == td_pnr.key and td_pnr.locator == template.locator and td_pnr.variation == rsp.body.variation
           for template in templates for td_pnr in test_data.pnr):
        rsp.error = True
        rsp.error_fields.variation = "Template cannot be merged since some data already exists for this variation."
        return rsp.dict
    for template in templates:
        create_body = SimpleNamespace(variation=rsp.body.variation, variation_name=rsp.body.variation_name,
                                      locator=template.locator, key=template.key, text=template.text,
                                      field_data_item=template.field_data)
        td_response = test_data.create_pnr_input(create_body.__dict__, persistence=False)
        if td_response["error"]:
            rsp.error = True
            rsp.message = td_response["message"]
            for _, error_msg in td_response["error_fields"].items():
                rsp.message += error_msg
            return rsp.dict
    for pnr_input in test_data.pnr:
        if not pnr_input.id:
            pnr_input.create()
    test_data.save()
    rsp.message = f"PNR template merged with the test data successfully."
    return rsp.dict


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
    rsp = StandardResponse(body, RequestType.TEMPLATE_MERGE_LINK)
    if rsp.error:
        return rsp.dict
    validate_and_update_variation(test_data, rsp, TD_REF[PNR])
    templates = get_templates(rsp, PNR)
    if rsp.error:
        return rsp.dict
    if any(td_pnr.locator == templates[0].locator and td_pnr.link and td_pnr.variation == rsp.body.variation
           for td_pnr in test_data.pnr):
        rsp.error = True
        rsp.error_fields.template_name = f"There is already one template linked with this locator."
        return rsp.dict
    create_body = SimpleNamespace(variation=rsp.body.variation, variation_name=rsp.body.variation_name,
                                  locator=templates[0].locator, link=rsp.body.template_name)
    pnr_input: Pnr = Pnr.dict_to_doc(create_body.__dict__)
    test_data.pnr.append(pnr_input)
    pnr_input.create()
    test_data.save()
    add_test_data_link_to_template(test_data, templates)
    Template.objects.save_all(templates)
    rsp.message = f"Template linked successfully."
    return rsp.dict


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
    rsp = StandardResponse(body, RequestType.TEMPLATE_LINK_UPDATE)
    if rsp.error:
        return rsp.dict
    templates = get_templates(rsp, PNR)
    if rsp.error:
        return rsp.dict
    td_pnr = get_pnr_element(rsp, test_data, templates[0])
    new_templates: List[Template] = get_new_templates(rsp, PNR)
    if rsp.error:
        return rsp.dict
    if templates[0].name == new_templates[0].name:
        rsp.message = f"Template link is the same. No changes made"
        return rsp.dict
    td_pnr.link = rsp.body.new_template_name
    td_pnr.locator = new_templates[0].locator
    td_pnr.save()
    remove_test_data_link_from_template(test_data, templates)
    add_test_data_link_to_template(test_data, new_templates)
    templates.extend(new_templates)
    Template.objects.save_all(templates)
    rsp.message = f"Template link updated successfully."
    return rsp.dict


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
    rsp = StandardResponse(body, RequestType.TEMPLATE_LINK_DELETE)
    if rsp.error:
        return rsp.dict
    templates = get_templates(rsp, PNR)
    if rsp.error:
        return rsp.dict
    td_pnr = get_pnr_element(rsp, test_data, templates[0])
    if rsp.error:
        return rsp.dict
    test_data.pnr.remove(td_pnr)
    td_pnr.delete()
    test_data.save()
    remove_test_data_link_from_template(test_data, templates)
    Template.objects.save_all(templates)
    rsp.message = f"Template link deleted successfully."
    return rsp.dict


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


class MergeLink:
    PROCESS = {
        PNR: {
            MERGE: merge_pnr_template,
            LINK_CREATE: create_link_pnr_template,
            LINK_UPDATE: update_link_pnr_template,
            LINK_DELETE: delete_link_pnr_template,
        }
    }

    @classmethod
    def process(cls, template_type: str, action_type: str) -> Callable:
        if template_type not in cls.PROCESS:
            return cls.invalid_template_type
        if action_type not in cls.PROCESS[template_type]:
            return cls.invalid_action_type
        return cls.PROCESS[template_type][action_type]

    @classmethod
    def invalid_template_type(cls, *_, **__) -> dict:
        rsp = StandardResponse()
        rsp.error = True
        rsp.message = "Invalid template type."
        return rsp.dict

    @classmethod
    def invalid_action_type(cls, *_, **__) -> dict:
        rsp = StandardResponse()
        rsp.error = True
        rsp.message = "Invalid action type."
        return rsp.dict
