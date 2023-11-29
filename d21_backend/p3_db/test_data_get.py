from typing import List

from d21_backend.p3_db.template_models import Template, GLOBAL, AAA, AAA_MACRO_NAME
from d21_backend.p3_db.test_data import TestData
from d21_backend.p3_db.test_data_elements import Pnr, Core
from d21_backend.p3_db.test_data_validators import validate_and_update_pnr_text_with_field, validate_and_update_global_data, \
    validate_and_update_macro_field_data


def extract_pnr_links(test_data: TestData) -> TestData:
    pnr_links: List[Pnr] = [pnr for pnr in test_data.pnr if pnr.link]
    if not pnr_links:
        return test_data
    template_names: set = {pnr.link for pnr in pnr_links}
    templates: List[Template] = list()
    for name in template_names:
        templates.extend(Template.objects.filter_by(name=name).get())
    updated_pnr_list: List[Pnr] = list()
    for pnr in pnr_links:
        linked_templates: List[Template] = [template for template in templates if template.name == pnr.link]
        for template in linked_templates:
            new_pnr = Pnr()
            new_pnr.variation = pnr.variation
            new_pnr.variation_name = pnr.variation_name
            new_pnr.link = pnr.link
            if any(not td_pnr.link and td_pnr.variation == pnr.variation and td_pnr.locator == pnr.locator and
                   td_pnr.key == template.key for td_pnr in test_data.pnr):
                new_pnr.link_status = "inactive"
            else:
                new_pnr.link_status = "active"
            new_pnr.locator = template.locator
            new_pnr.key = template.key
            body: dict = {"field_data_item": template.field_data, "text": template.text}
            errors: dict = validate_and_update_pnr_text_with_field(body)
            if errors:
                continue
            new_pnr.field_data_item = body["field_data_item"]
            new_pnr.text = body["text"]
            updated_pnr_list.append(new_pnr)
    test_data.pnr = [pnr for pnr in test_data.pnr if not pnr.link]
    test_data.pnr.extend(updated_pnr_list)
    test_data.pnr.sort(key=lambda item: (item.variation, item.locator, item.key, item.link))
    return test_data


def extract_core_links(test_data: TestData) -> TestData:
    core_links: List[Core] = [core for core in test_data.cores if core.link]
    if not core_links:
        return test_data
    template_names: set = {core.link for core in core_links}
    templates: List[Template] = list()
    for name in template_names:
        templates.extend(Template.objects.filter_by(name=name).get())
    updated_core_list: List[Core] = list()
    for core in core_links:
        linked_templates: List[Template] = [template for template in templates if template.name == core.link]
        for template in linked_templates:
            new_core = Core()
            new_core.variation = core.variation
            new_core.variation_name = core.variation_name
            new_core.link = core.link
            body: dict = {"field_data": template.field_data}
            if template.type == GLOBAL:
                if any(not td_core.link and td_core.variation == core.variation and
                       td_core.global_name == template.global_name for td_core in test_data.cores):
                    new_core.link_status = "inactive"
                else:
                    new_core.link_status = "active"
                new_core.global_name = template.global_name
                new_core.is_global_record = template.is_global_record
                body["hex_data"] = template.hex_data
                body["seg_name"] = template.seg_name
                body["is_global_record"] = template.is_global_record
                errors: dict = validate_and_update_global_data(body)
                if errors:
                    continue
                new_core.hex_data = body["hex_data"]
            elif template.type == AAA:
                new_core.macro_name = AAA_MACRO_NAME
                if any(not td_core.link and td_core.variation == core.variation and
                       td_core.macro_name == AAA_MACRO_NAME for td_core in test_data.cores):
                    new_core.link_status = "inactive"
                else:
                    new_core.link_status = "active"
                errors: dict = validate_and_update_macro_field_data(body, AAA_MACRO_NAME)
                if errors:
                    continue
            new_core.field_data = body["field_data"]
            updated_core_list.append(new_core)
    test_data.cores = [core for core in test_data.cores if not core.link]
    test_data.cores.extend(updated_core_list)
    test_data.cores.sort(key=lambda item: (item.variation, item.ecb_level, item.heap_name, item.macro_name,
                                           item.global_name, item.link))
    return test_data


def get_whole_test_data(test_data_id: str, link: bool) -> TestData:
    test_data: TestData = TestData.get_by_id(test_data_id, cascade=True)
    if not link or not test_data:
        return test_data
    test_data = extract_pnr_links(test_data)
    test_data = extract_core_links(test_data)
    return test_data
