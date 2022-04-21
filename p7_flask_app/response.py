from copy import copy
from types import SimpleNamespace
from typing import Optional


class RequestType:
    VARIATION = SimpleNamespace(new_name=str())
    TEMPLATE_PNR_UPDATE = SimpleNamespace(id=str(), field_data=str(), text=str())
    TEMPLATE_GLOBAL_UPDATE = SimpleNamespace(id=str(), field_data=str(), hex_data=str(), is_global_record=str())
    TEMPLATE_AAA_UPDATE = SimpleNamespace(id=str(), field_data=str())

class StandardResponse:

    def __init__(self, body: Optional[dict] = None, request_type: Optional[SimpleNamespace] = None):
        self.message: str = str()
        self.error: bool = bool()
        self.error_fields: SimpleNamespace = SimpleNamespace() if request_type is None else copy(request_type)
        self.body: SimpleNamespace = SimpleNamespace()
        if body is None:
            return
        if not isinstance(body, dict) or not body:
            self.message = "Invalid request. Request cannot be empty."
            self.error = True
            return
        valid_fields: set = set(request_type.__dict__)
        if set(body) != valid_fields:
            self.message = f"Invalid request. Only {', '.join([field for field in valid_fields])} field(s) allowed."
            self.error = True
            return
        for field, value in body.items():
            if not isinstance(value, type(request_type.__getattribute__(field))):
                self.error = True
                self.error_fields.__setattr__(field, "Invalid data type.")
        self.body: SimpleNamespace = SimpleNamespace(**body)
        return

    @property
    def dict(self):
        return {
            "message": self.message,
            "error": self.error,
            "error_fields": self.error_fields.__dict__
        }
