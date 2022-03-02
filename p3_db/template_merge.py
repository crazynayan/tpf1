from typing import List

from p3_db.template_models import Template, PNR
from p3_db.test_data import TestData


def merge_pnr_template(test_data: TestData, body: dict):
    response: dict = {"error": True, "message": str(), "error_fields": dict()}
    if set(body) != {"variation", "variation_name", "template_name"}:
        response["message"] = "Only 3 fields allowed (variation, variation_name, template_name) and all are mandatory."
        return response
    if not test_data.validate_and_update_variation(body, "pnr"):
        response["error_fields"]["variation"] = "Invalid variation."
    templates: List[Template] = Template.objects.filter_by(name=body["template_name"]).get()
    if not templates:
        response["error_fields"]["template_name"] = f"Template with this name not found."
    elif any(template.type != PNR for template in templates):
        response["error_fields"]["template_name"] = f"Template is NOT a PNR template"
    if response["error_fields"]:
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
