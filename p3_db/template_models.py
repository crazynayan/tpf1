from typing import Tuple, Optional, List

from firestore_ci import FirestoreDocument

PNR, GLOBAL, AAA = "PNR", "Global", "AAA"
AAA_MACRO_NAME = "WA0AA"
TEMPLATE_TYPES = (PNR, GLOBAL, AAA)


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


def get_template_by_id(template_id: str) -> Tuple[Optional[Template], str]:
    template: Template = Template.get_by_id(template_id)
    if not template:
        return None, "Template not found with this id."
    return template, str()
