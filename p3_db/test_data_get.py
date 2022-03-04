from typing import List

from p3_db.template_models import Template
from p3_db.test_data import TestData
from p3_db.test_data_elements import Pnr
from p3_db.test_data_validators import validate_and_update_pnr_text_with_field


def get_whole_test_data(test_data_id: str, link: bool) -> TestData:
    test_data: TestData = TestData.get_by_id(test_data_id, cascade=True)
    if not link:
        return test_data
    pnr_links: List[Pnr] = [pnr for pnr in test_data.pnr if pnr.link]
    if not pnr_links:
        return test_data
    template_names: set = {pnr.link for pnr in test_data.pnr}
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
