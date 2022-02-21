from typing import Tuple, Optional

from firestore_ci import FirestoreDocument

PNR, GLOBAL, AAA = "PNR", "Global", "AAA"
TEMPLATE_TYPES = (PNR, GLOBAL, AAA)


class Template(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name: str = str()
        self.description: str = str()
        self.owner: str = str()
        self.type: str = str()
        self.key: str = str()  # PNR key or TPFDF key
        self.field_data: str = str()
        self.text: str = str()
        self.locator: str = str()  # PNR locator


Template.init()


def get_template_by_id(template_id: str) -> Tuple[Optional[Template], str]:
    template: Template = Template.get_by_id(template_id)
    if not template:
        return None, "Template not found with this id."
    return template, str()
