from types import SimpleNamespace
from typing import List, Dict, Callable, Union

from d21_backend.p3_db.response import StandardResponse
from d21_backend.p3_db.template_models import Template, TEMPLATE_TYPES, PNR, TD_REF, GLOBAL, AAA, AAA_MACRO_NAME
from d21_backend.p3_db.test_data import TestData, VALID_ELEMENT_TYPES
from d21_backend.p3_db.test_data_elements import Pnr, Core


# Used by MERGE, LINK_CREATE
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


# Used by MERGE, LINK_CREATE, LINK_UPDATE, LINK_DELETE
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


# Used by MERGE
def validate_element_exists(rsp: StandardResponse, template_type: str, template_list: list, test_data_list: TestData):
    is_exists: Dict[str, Callable] = {
        PNR: lambda templates, test_data:
        any(td.key == template.key and td.locator == template.locator and td.variation == rsp.body.variation
            for template in templates for td in test_data.ref(TD_REF[template_type])),
        GLOBAL: lambda templates, test_data:
        any(td.global_name == template.global_name and td.variation == rsp.body.variation
            for template in templates for td in test_data.ref(TD_REF[template_type])),
        AAA: lambda templates, test_data:
        any(td.macro_name == AAA_MACRO_NAME and td.variation == rsp.body.variation
            for td in test_data.ref(TD_REF[template_type])),
    }
    if is_exists[template_type](template_list, test_data_list):
        rsp.error = True
        rsp.error_fields.variation = "Template cannot be merged since some data already exists for this variation."
    return


# Used by MERGE
def get_create_request_body(rsp: StandardResponse, template_type: str, template: Template) -> SimpleNamespace:
    body: Dict[str, SimpleNamespace] = {
        PNR: SimpleNamespace(variation=rsp.body.variation, variation_name=rsp.body.variation_name,
                             locator=template.locator, key=template.key, text=template.text,
                             field_data_item=template.field_data),
        GLOBAL: SimpleNamespace(variation=rsp.body.variation, variation_name=rsp.body.variation_name,
                                global_name=template.global_name, is_global_record=template.is_global_record,
                                hex_data=template.hex_data, seg_name=template.seg_name,
                                field_data=template.field_data),
        AAA: SimpleNamespace(variation=rsp.body.variation, variation_name=rsp.body.variation_name,
                             macro_name=AAA_MACRO_NAME, field_data=template.field_data),
    }
    return body[template_type]


# Used by MERGE
def validate_and_update_test_data(rsp: StandardResponse, template_type, test_data: TestData, body: SimpleNamespace):
    create: Dict[str, Callable] = {
        PNR: test_data.create_pnr_input,
        GLOBAL: test_data.create_global,
        AAA: test_data.create_macro,
    }
    response: dict = create[template_type](body.__dict__, persistence=False)
    if response["error"]:
        rsp.error = True
        rsp.message = response["message"]
        for _, error_msg in response["error_fields"].items():
            rsp.message += error_msg
    return


# Used by LINK_CREATE
def validate_link_exists(rsp: StandardResponse, template_type: str, template: Template, test_data: TestData):
    is_exists: Dict[str, Callable] = {
        PNR: lambda template_item, test_data_item:
        any(td.locator == template_item.locator and td.link and td.variation == rsp.body.variation
            for td in test_data_item.ref(TD_REF[template_type])),
        GLOBAL: lambda template_item, test_data_item:
        any(td.global_name == template_item.global_name and td.link and td.variation == rsp.body.variation
            for td in test_data_item.ref(TD_REF[template_type])),
        AAA: lambda _, test_data_item:
        any(td.macro_name == AAA_MACRO_NAME and td.link and td.variation == rsp.body.variation
            for td in test_data_item.ref(TD_REF[template_type])),
    }
    if is_exists[template_type](template, test_data):
        rsp.error = True
        rsp.error_fields.variation = f"There is already one {template_type} template linked with this variation."
    return


# Used by LINK_CREATE
def get_link_create_body(rsp: StandardResponse, template_type: str, template: Template) -> SimpleNamespace:
    key = {PNR: "locator", AAA: "macro_name", GLOBAL: "global_name"}
    value = {PNR: template.locator, AAA: AAA_MACRO_NAME, GLOBAL: GLOBAL}
    body = SimpleNamespace(variation=rsp.body.variation, variation_name=rsp.body.variation_name,
                           link=rsp.body.template_name)
    body.__setattr__(key[template_type], value[template_type])
    return body


# Used by LINK_CREATE
def get_test_data_element_from_body(template_type: str, body: SimpleNamespace) -> Union[Pnr, Core]:
    td_doc = {PNR: Pnr, AAA: Core, GLOBAL: Core}
    return td_doc[template_type].dict_to_doc(body.__dict__)


# Used by LINK_UPDATE, LINK_DELETE
def get_test_data_element(rsp: StandardResponse, template_type: str, template: Template, test_data: TestData):
    get_element: Dict[str, Callable] = {
        PNR: lambda template_item, test_data_item:
        next((td for td in test_data_item.ref(TD_REF[template_type]) if td.locator == template_item.locator
              and td.link == template_item.name and td.variation == rsp.body.variation), None),
        GLOBAL: lambda template_item, test_data_item:
        next((td for td in test_data_item.ref(TD_REF[template_type]) if td.global_name == GLOBAL
              and td.link == template_item.name and td.variation == rsp.body.variation), None),
        AAA: lambda template_item, test_data_item:
        next((td for td in test_data_item.ref(TD_REF[template_type]) if td.macro_name == AAA_MACRO_NAME
              and td.link == template_item.name and td.variation == rsp.body.variation), None),
    }
    element = get_element[template_type](template, test_data)
    if not element:
        rsp.error = True
        rsp.error_fields.template_name = f"No template linked with this name."
    return element


# Used by LINK_UPDATE
def get_new_templates(rsp: StandardResponse, template_type: str) -> List[Template]:
    templates: List[Template] = Template.objects.filter_by(name=rsp.body.new_template_name).get()
    if not templates:
        rsp.error = True
        rsp.message = f"No template found with the new template name."
    elif templates[0].type != template_type:
        rsp.error = True
        rsp.message = f"Only {template_type} templates can be linked."
    return templates


# Used by LINK_CREATE, LINK_UPDATE
def add_test_data_link_to_template(test_data: TestData, templates: List[Template]):
    for template in templates:
        if test_data.id not in template.test_data_links:
            template.test_data_links.append(test_data.id)
    return


# Used by LINK_UPDATE, LINK_DELETE
def remove_test_data_link_from_template(test_data: TestData, templates: List[Template]):
    if any(element for element in test_data.ref(TD_REF[templates[0].type]) if element.link == templates[0].name):
        return
    for template in templates:
        if test_data.id in template.test_data_links:
            template.test_data_links.remove(test_data.id)
    return
