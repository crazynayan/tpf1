from copy import copy
from types import SimpleNamespace
from typing import Optional


class RequestType:
    VARIATION = SimpleNamespace(new_name=str())
    TEMPLATE_PNR_UPDATE = SimpleNamespace(field_data=str(), text=str())
    TEMPLATE_GLOBAL_UPDATE = SimpleNamespace(field_data=str(), hex_data=str(), is_global_record=bool(), seg_name=str())
    TEMPLATE_AAA_UPDATE = SimpleNamespace(field_data=str())
    TEMPLATE_PNR_ADD = SimpleNamespace(field_data=str(), text=str(), key=str(), name=str())
    TEMPLATE_GLOBAL_ADD = SimpleNamespace(field_data=str(), hex_data=str(), is_global_record=bool(), seg_name=str(),
                                          name=str(), global_name=str())
    TEMPLATE_PNR_CREATE = SimpleNamespace(field_data=str(), text=str(), key=str(), name=str(), locator=str(),
                                          description=str())
    TEMPLATE_GLOBAL_CREATE = SimpleNamespace(field_data=str(), hex_data=str(), is_global_record=bool(), seg_name=str(),
                                             name=str(), global_name=str(), description=str())
    TEMPLATE_AAA_CREATE = SimpleNamespace(name=str(), description=str(), field_data=str())
    TEMPLATE_RENAME_COPY = SimpleNamespace(old_name=str(), new_name=str(), description=str())
    TEMPLATE_DELETE = SimpleNamespace(name=str())
    TEMPLATE_MERGE_LINK = SimpleNamespace(variation=int(), variation_name=str(), template_name=str())
    TEMPLATE_LINK_UPDATE = SimpleNamespace(variation=int(), new_template_name=str(), template_name=str())
    TEMPLATE_LINK_DELETE = SimpleNamespace(variation=int(), template_name=str())


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
            count = len(valid_fields)
            field_list = ", ".join([field for field in valid_fields])
            self.message = f"Invalid request. Only 1 field ({field_list}) allowed and it is mandatory." if count == 1 \
                else f"Invalid request. Only {count} fields ({field_list}) allowed and they are mandatory."
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
