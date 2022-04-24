from typing import Optional, List

from firestore_ci import FirestoreDocument
from flask import g

from p3_db.response import StandardResponse
from p3_db.test_data import ElementType

PNR, GLOBAL, AAA = "PNR", "Global", "AAA"
AAA_MACRO_NAME = "WA0AA"
TEMPLATE_TYPES = (PNR, GLOBAL, AAA)
TD_REF = {
    PNR: ElementType.PNR,
    GLOBAL: ElementType.CORE,
    AAA: ElementType.CORE,
}


class Template(FirestoreDocument):

    def __init__(self):
        super().__init__()
        # Common
        self.name: str = str()
        self.description: str = str()
        self.owner: str = str()
        self.type: str = str()
        self.test_data_links: List[str] = list()
        self.field_data: str = str()
        # PNR specific
        self.key: str = str()  # PNR key or TPFDF key
        self.text: str = str()
        self.locator: str = str()  # PNR locator
        # Core specific
        self.hex_data: str = str()
        self.seg_name: str = str()
        # Global specific
        self.global_name: str = str()
        self.is_global_record: bool = bool()


Template.init()


def get_template_by_id(template_id: str) -> Optional[Template]:
    template: Template = Template.get_by_id(template_id)
    return template


def validate_and_get_template_by_id(template_id: str, rsp: StandardResponse) -> Optional[Template]:
    template: Template = get_template_by_id(template_id)
    if not template:
        rsp.error = True
        rsp.message = "Template not found with this id."
        return None
    validate_ownership(template, rsp)
    return template


def validate_ownership(template: Template, rsp: StandardResponse) -> None:
    try:
        if template.owner != g.current_user.email:
            rsp.error = True
            rsp.message = "Unauthorized to update this template."
    except RuntimeError:
        pass
