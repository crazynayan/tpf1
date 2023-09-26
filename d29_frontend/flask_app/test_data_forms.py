from typing import List

from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from munch import Munch
from wtforms import StringField, SubmitField, BooleanField, IntegerField, SelectField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, ValidationError, NumberRange, Length
from wtforms.widgets import Input

from d29_frontend.config import Config
from d29_frontend.flask_app import tpf2_app
from d29_frontend.flask_app.form_prompts import OLD_FIELD_DATA_PROMPT, PNR_OUTPUT_FIELD_DATA_PROMPT, PNR_INPUT_FIELD_DATA_PROMPT, \
    PNR_KEY_PROMPT, PNR_LOCATOR_PROMPT, PNR_TEXT_PROMPT, VARIATION_PROMPT, VARIATION_NAME_PROMPT, GLOBAL_NAME_PROMPT, \
    IS_GLOBAL_RECORD_PROMPT, GLOBAL_HEX_DATA_PROMPT, GLOBAL_SEG_NAME_PROMPT, GLOBAL_FIELD_DATA_PROMPT, \
    MACRO_FIELD_DATA_PROMPT, ECB_FIELD_DATA_PROMPT, evaluate_error, init_body
from d29_frontend.flask_app.server import Server, RequestType


def form_validate_field_data(data: str) -> str:
    data = data.strip().upper()
    if data.startswith("'"):
        if len(data) == 1:
            raise ValidationError("There needs to be some text after a single quote")
        data = data[1:].encode("cp037").hex().upper()
    elif data.startswith("-"):
        if len(data) == 1 or not data[1:].isdigit():
            raise ValidationError("Invalid Negative Number")
        neg_data = int(data)
        if neg_data < -0x80000000:
            raise ValidationError(f"Negative Number cannot be less than {-0x80000000}")
        data = f"{neg_data & tpf2_app.config['REG_MAX']:08X}"
    elif len(data) % 2 == 1 and data.isdigit():
        number_data = int(data)
        if number_data > 0x7FFFFFFF:
            raise ValidationError(f"Number cannot be greater than {0x7FFFFFFF}")
        data = f"{number_data:08X}"
    else:
        try:
            int(data, 16)
            if len(data) % 2:
                data = f"0{data}"
        except ValueError:
            data = data.encode("cp037").hex().upper()
    return data


def form_validate_multiple_field_data(data: str, macro_name: str) -> str:
    updated_field_data = list()
    for key_value in data.split(","):
        if key_value.count(":") != 1:
            raise ValidationError(f"Include a single colon : to separate field and data - {key_value}")
        field = key_value.split(":")[0].strip().upper()
        label_ref = Server.search_field(field)
        if not label_ref:
            raise ValidationError(f"Field name not found - {field}")
        if macro_name != label_ref["name"]:
            raise ValidationError(f"Field not in the same macro - {field} not in {macro_name}")
        data = form_validate_field_data(key_value.split(":")[1])
        updated_field_data.append(f"{field}:{data}")
    return ",".join(updated_field_data)


def form_field_lookup(data: str, macro_name: str) -> str:
    data = data.upper()
    label_ref = Server.search_field(data)
    if not label_ref:
        raise ValidationError(f"Field name not found - {data}")
    if macro_name != label_ref["name"]:
        raise ValidationError(f"Field not in the same macro - {data} not in {macro_name}")
    return data


def form_validate_macro_name(macro_name: str) -> str:
    macro_name = macro_name.upper()
    label_ref = Server.search_field(macro_name)
    if not label_ref or label_ref["name"] != macro_name:
        raise ValidationError("This is not a valid macro name")
    return macro_name


class TestDataForm(FlaskForm):
    name = StringField("Name of Test Data (Must be unique in the system)")
    seg_name = StringField("Segment Name (Must exists in the system)")
    stop_segments = StringField("Stop Segment Name List (Separate multiple segments with comma). Optional")
    startup_script = TextAreaField("Enter script in ASM to run at startup", render_kw={"rows": "7"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEST_DATA_CREATE)
            self.response: Munch = Server.create_test_data(body) if not test_data \
                else Server.rename_test_data(test_data["id"], body)
        if test_data and request.method == "GET":
            self.name.data = test_data["name"]
            self.seg_name.data = test_data["seg_name"]
            # stop_segments: List[str] = test_data["stop_segments"]
            self.stop_segments.data = test_data["stop_seg_string"]
            self.startup_script.data = test_data["startup_script"]

    def validate_name(self, _):
        evaluate_error(self.response, "name", message=True)

    def validate_seg_name(self, _):
        evaluate_error(self.response, "seg_name")

    def validate_stop_segments(self, _):
        evaluate_error(self.response, "stop_segments")

    def validate_startup_script(self, _):
        evaluate_error(self.response, "startup_script")


class DeleteForm(FlaskForm):
    deleted_item = HiddenField()
    submit = SubmitField("Yes - Delete")


class RegisterForm(FlaskForm):
    r0 = BooleanField("R0")
    r1 = BooleanField("R1")
    r2 = BooleanField("R2")
    r3 = BooleanField("R3")
    r4 = BooleanField("R4")
    r5 = BooleanField("R5")
    r6 = BooleanField("R6")
    r7 = BooleanField("R7")
    r8 = BooleanField("R8")
    r9 = BooleanField("R9")
    r10 = BooleanField("R10")
    r11 = BooleanField("R11")
    r12 = BooleanField("R12")
    r13 = BooleanField("R13")
    r14 = BooleanField("R14")
    r15 = BooleanField("R15")
    save = SubmitField("Save & Continue - Add Further Data")


class FieldSearchForm(FlaskForm):
    field = StringField("Field name", validators=[InputRequired()])
    search = SubmitField("Search")

    @staticmethod
    def validate_field(_, field: StringField) -> None:
        field.data = field.data.upper()
        label_ref = Server.search_field(field.data)
        if not label_ref:
            raise ValidationError("Field name not found")
        field.data = label_ref


class FieldLengthForm(FlaskForm):
    length = IntegerField("Length", validators=[NumberRange(1, 4095, "Length can be from 1 to 4095")])
    base_reg = StringField("Base Register - Keep it blank for default macros like AAA, ECB, GLOBAL, IMG etc.")
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, macro_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.macro_name = macro_name

    def validate_base_reg(self, base_reg: StringField) -> None:
        base_reg.data = base_reg.data.upper()
        if base_reg.data and base_reg.data not in tpf2_app.config["REGISTERS"]:
            raise ValidationError("Invalid Base Register - Register can be from R0 to R15")
        default_macros = set(tpf2_app.config["DEFAULT_MACROS"]).union({"GLOBAS", "GLOBYS", "GL0BS"})
        if (not base_reg.data or base_reg.data == "R0") and self.macro_name not in default_macros:
            raise ValidationError(f"Base Register cannot be blank or R0 for macro {self.macro_name}")
        return


def init_variation(variation: SelectField, variation_name: StringField, test_data_id: str, v_type: str) -> dict:
    variations = Server.get_variations(test_data_id, v_type)
    if not current_user.is_authenticated:
        return dict()
    variation.choices = [(item["variation"], f"{item['variation_name']}") for item in variations]
    variation.choices.append((-1, "New Variation"))
    if request.method != "POST":
        return dict()
    if variation.data == -1:
        variation_name.data = variation_name.data.strip()
        variation_number = variations[-1]["variation"] + 1 if variations else 0
    else:
        variation_name.data = next(variation_name for variation, variation_name in variation.choices)
        variation_number = variation.data
    return {"variation": variation_number, "variation_name": variation_name.data}


class HeapForm(FlaskForm):
    variation = SelectField(VARIATION_PROMPT, coerce=int)
    variation_name = StringField(VARIATION_NAME_PROMPT)
    heap_name = StringField("Enter Heap Name - Must be alphanumeric", validators=[InputRequired()])
    hex_data = StringField("Enter input data in hex format to initialize the heap. Leave it blank to init with zeroes")
    seg_name = StringField("Segment Name. Leave it blank to either init with zeroes or with hex data")
    field_data = TextAreaField("Enter multiple fields and data separated by comma. The field and data should be "
                               "separated by colon. Data should be in hex format. Leave it blank to either init with "
                               "zeroes or with hex data", render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        body = init_variation(self.variation, self.variation_name, test_data_id, "core")
        self.response: dict = dict()
        if request.method == "POST":
            body["heap_name"] = self.heap_name.data
            body["hex_data"] = "".join(char.upper() for char in self.hex_data.data if char != " ")
            body["seg_name"] = self.seg_name.data.upper()
            body["field_data"] = self.field_data.data
            self.response = Server.add_input_heap(test_data_id, body)

    def validate_variation(self, variation):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "variation" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["variation"])
        if variation.data == -1:
            variation.data = 0

    def validate_heap_name(self, _) -> None:
        if "error_fields" in self.response and "heap_name" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["heap_name"])

    def validate_hex_data(self, _):
        if "error_fields" in self.response and "hex_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["hex_data"])

    def validate_seg_name(self, _):
        if "error_fields" in self.response and "seg_name" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["seg_name"])

    def validate_field_data(self, _):
        if "error_fields" in self.response and "field_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_data"])


class MacroForm(FlaskForm):
    variation = SelectField(VARIATION_PROMPT, coerce=int)
    variation_name = StringField(VARIATION_NAME_PROMPT)
    field_data = TextAreaField(MACRO_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, macro_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        body = init_variation(self.variation, self.variation_name, test_data_id, "core")
        if macro_name == "EB0EB":
            self.field_data.label.text = ECB_FIELD_DATA_PROMPT
        self.response: dict = dict()
        if request.method == "POST":
            body["macro_name"] = macro_name
            body["field_data"] = self.field_data.data
            self.response = Server.add_input_macro(test_data_id, body)

    def validate_variation(self, variation):
        evaluate_error(self.response, "variation", message=True)
        if variation.data == -1:
            variation.data = 0

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data")


class EcbLevelForm(FlaskForm):
    variation = SelectField(VARIATION_PROMPT, coerce=int)
    variation_name = StringField(VARIATION_NAME_PROMPT)
    ecb_level = SelectField("Select an ECB level")
    hex_data = StringField("Enter input data in hex format to initialize the block. Leave it blank to either init "
                           "with zeroes or with field data")
    seg_name = StringField("Segment Name. Leave it blank to either init with zeroes or with hex data")
    field_data = TextAreaField("Enter multiple fields and data separated by comma. The field and data should be "
                               "separated by colon. Data should be in hex format. Leave it blank to either init with "
                               "zeroes or with hex data", render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        body = init_variation(self.variation, self.variation_name, test_data_id, "core")
        self.ecb_level.choices = [(level, level) for level in Config.ECB_LEVELS]
        self.response: dict = dict()
        if request.method == "POST":
            body["ecb_level"] = self.ecb_level.data
            body["hex_data"] = "".join(char.upper() for char in self.hex_data.data if char != " ")
            body["seg_name"] = self.seg_name.data.upper()
            body["field_data"] = self.field_data.data
            self.response = Server.add_input_ecb_level(test_data_id, body)

    def validate_variation(self, variation):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "variation" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["variation"])
        if variation.data == -1:
            variation.data = 0

    def validate_ecb_level(self, _):
        if "error_fields" in self.response and "ecb_level" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["ecb_level"])

    def validate_hex_data(self, _):
        if "error_fields" in self.response and "hex_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["hex_data"])

    def validate_seg_name(self, _):
        if "error_fields" in self.response and "seg_name" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["seg_name"])

    def validate_field_data(self, _):
        if "error_fields" in self.response and "field_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_data"])


class UpdateHexFieldDataForm(FlaskForm):
    hex_data = StringField("Enter input data in hex format to initialize the block. Leave it blank to either init with "
                           "zeroes or with field data")
    seg_name = StringField("Segment Name. Leave it blank to either init with zeroes or with hex data")
    field_data = TextAreaField("Enter multiple fields and data separated by comma. The field and data should be "
                               "separated by colon. Data should be in hex format. Leave it blank to either init with "
                               "zeroes or with hex data", render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, core: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        variation_name = f" ({core['variation_name']})" if core["variation_name"] else str()
        self.display_fields.append(("Variation", f"{core['variation']}{variation_name}"))
        if core["ecb_level"]:
            self.display_fields.append(("ECB Level", core["ecb_level"]))
        elif core["heap_name"]:
            self.display_fields.append(("Heap", core["heap_name"]))
        self.response: dict = dict()
        if request.method == "GET":
            self.hex_data.data = core["hex_data"][0]
            self.seg_name.data = core["seg_name"]
            self.field_data.data = core["original_field_data"]
        if request.method == "POST":
            body: dict = dict()
            body["hex_data"] = "".join(char.upper() for char in self.hex_data.data if char != " ")
            body["seg_name"] = self.seg_name.data.upper()
            body["field_data"] = self.field_data.data
            if core["ecb_level"]:
                self.response = Server.update_input_ecb_level(test_data_id, core["ecb_level"], core["variation"], body)
            elif core["heap_name"]:
                self.response = Server.update_input_heap(test_data_id, core["heap_name"], core["variation"], body)
        return

    def validate_hex_data(self, _):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "hex_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["hex_data"])

    def validate_seg_name(self, _):
        if "error_fields" in self.response and "seg_name" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["seg_name"])

    def validate_field_data(self, _):
        if "error_fields" in self.response and "field_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_data"])


class UpdateMacroForm(FlaskForm):
    field_data = TextAreaField(MACRO_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, core: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        variation_name = f" ({core['variation_name']})" if core["variation_name"] else str()
        self.display_fields = list()
        self.display_fields.append(("Data macro", core["macro_name"]))
        self.display_fields.append(("Variation", f"{core['variation']}{variation_name}"))
        self.response: dict = dict()
        if request.method == "GET":
            self.field_data.data = core["original_field_data"]
        if request.method == "POST":
            body: dict = dict()
            body["field_data"] = self.field_data.data
            self.response = Server.update_input_macro(test_data_id, core["macro_name"], core["variation"], body)
        return

    def validate_field_data(self, _):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "field_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_data"])


class GlobalForm(FlaskForm):
    variation = SelectField(VARIATION_PROMPT, coerce=int)
    variation_name = StringField(VARIATION_NAME_PROMPT)
    global_name = StringField(GLOBAL_NAME_PROMPT, validators=[InputRequired()])
    is_global_record = BooleanField(IS_GLOBAL_RECORD_PROMPT)
    hex_data = StringField(GLOBAL_HEX_DATA_PROMPT)
    seg_name = StringField(GLOBAL_SEG_NAME_PROMPT)
    field_data = TextAreaField(GLOBAL_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        body = init_variation(self.variation, self.variation_name, test_data_id, "core")
        self.response: dict = dict()
        if request.method == "POST":
            body["global_name"] = self.global_name.data.upper()
            body["hex_data"] = "".join(char.upper() for char in self.hex_data.data if char != " ")
            body["seg_name"] = self.seg_name.data.upper()
            body["field_data"] = self.field_data.data
            body["is_global_record"] = self.is_global_record.data
            self.response = Server.add_input_global(test_data_id, body)

    def validate_variation(self, variation):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "variation" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["variation"])
        if variation.data == -1:
            variation.data = 0

    def validate_global_name(self, _) -> None:
        if "error_fields" in self.response and "global_name" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["global_name"])

    def validate_hex_data(self, _):
        if "error_fields" in self.response and "hex_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["hex_data"])

    def validate_seg_name(self, _):
        if "error_fields" in self.response and "seg_name" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["seg_name"])

    def validate_field_data(self, _):
        if "error_fields" in self.response and "field_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_data"])


class UpdateGlobalForm(FlaskForm):
    is_global_record = BooleanField(IS_GLOBAL_RECORD_PROMPT)
    hex_data = StringField(GLOBAL_HEX_DATA_PROMPT)
    seg_name = StringField(GLOBAL_SEG_NAME_PROMPT)
    field_data = TextAreaField(GLOBAL_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, core: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        variation_name = f" ({core['variation_name']})" if core["variation_name"] else str()
        self.display_fields.append(("Variation", f"{core['variation']}{variation_name}"))
        self.display_fields.append(("Global Name", core["global_name"]))
        self.response: dict = dict()
        if request.method == "GET":
            self.is_global_record.data = core["is_global_record"]
            self.hex_data.data = core["hex_data"][0]
            self.seg_name.data = core["seg_name"]
            self.field_data.data = core["original_field_data"]
        if request.method == "POST":
            body: dict = dict()
            body["hex_data"] = "".join(char.upper() for char in self.hex_data.data if char != " ")
            body["seg_name"] = self.seg_name.data.upper()
            body["field_data"] = self.field_data.data
            body["is_global_record"] = self.is_global_record.data
            self.response = Server.update_input_global(test_data_id, core["id"], body)
        return

    def validate_hex_data(self, _):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "hex_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["hex_data"])

    def validate_seg_name(self, _):
        if "error_fields" in self.response and "seg_name" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["seg_name"])

    def validate_field_data(self, _):
        if "error_fields" in self.response and "field_data" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_data"])


class PnrOutputForm(FlaskForm):
    key = SelectField(PNR_KEY_PROMPT, choices=tpf2_app.config["PNR_KEYS"], default="header")
    locator = StringField(PNR_LOCATOR_PROMPT)
    field_item_len = TextAreaField(PNR_OUTPUT_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: dict = dict()
        if request.method == "POST":
            body: dict = dict()
            body["key"] = self.key.data
            body["locator"] = self.locator.data
            body["field_item_len"] = self.field_item_len.data
            self.response = Server.add_output_pnr(test_data_id, body)

    def validate_key(self, _):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "key" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["key"])

    def validate_locator(self, _):
        if "error_fields" in self.response and "locator" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["locator"])

    def validate_field_item_len(self, _):
        if "error_fields" in self.response and "field_item_len" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_item_len"])


class UpdatePnrOutputForm(FlaskForm):
    field_item_len = TextAreaField(PNR_OUTPUT_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, pnr_output: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        self.display_fields.append(("Key", pnr_output["key"].upper()))
        pwc = f"{' (PNR Working copy)' if pnr_output['locator'] == Config.AAAPNR else str()}"
        self.display_fields.append(("PNR Locator", f"{pnr_output['locator']}{pwc}"))
        self.response: dict = dict()
        if request.method == "GET":
            self.field_item_len.data = pnr_output["original_field_item_len"]
        if request.method == "POST":
            body: dict = {"field_item_len": self.field_item_len.data}
            self.response = Server.update_output_pnr(test_data_id, pnr_output["id"], body)

    def validate_field_item_len(self, _):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "field_item_len" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_item_len"])


class PnrInputForm(FlaskForm):
    variation = SelectField(VARIATION_PROMPT, coerce=int)
    variation_name = StringField(VARIATION_NAME_PROMPT)
    key = SelectField(PNR_KEY_PROMPT, choices=tpf2_app.config["PNR_KEYS"], default="header")
    locator = StringField(PNR_LOCATOR_PROMPT)
    text = StringField(PNR_TEXT_PROMPT)
    field_data_item = TextAreaField(PNR_INPUT_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: dict = dict()
        body: dict = init_variation(self.variation, self.variation_name, test_data_id, "pnr")
        if request.method == "POST":
            body["key"] = self.key.data
            body["locator"] = self.locator.data
            body["text"] = self.text.data
            body["field_data_item"] = self.field_data_item.data
            self.response = Server.add_input_pnr(test_data_id, body)

    def validate_variation(self, variation):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "variation" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["variation"])
        if variation.data == -1:
            variation.data = 0

    def validate_key(self, _):
        if "error_fields" in self.response and "key" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["key"])

    def validate_locator(self, _):
        if "error_fields" in self.response and "locator" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["locator"])

    def validate_text(self, _):
        if "error_fields" in self.response and "text" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["text"])

    def validate_field_data_item(self, _):
        if "error_fields" in self.response and "field_data_item" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_data_item"])


class UpdatePnrInputForm(FlaskForm):
    text = StringField(PNR_TEXT_PROMPT)
    field_data_item = TextAreaField(PNR_INPUT_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Save & Continue - Add Further Data")

    def __init__(self, test_data_id: str, pnr_input: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        variation_name = f" ({pnr_input['variation_name']})" if pnr_input["variation_name"] else str()
        self.display_fields.append(("Variation", f"{pnr_input['variation']}{variation_name}"))
        self.display_fields.append(("Key", pnr_input["key"].upper()))
        pwc = f"{' (PNR Working copy)' if pnr_input['locator'] == Config.AAAPNR else str()}"
        self.display_fields.append(("PNR Locator", f"{pnr_input['locator']}{pwc}"))
        self.response: dict = dict()
        if request.method == "GET":
            self.text.data = pnr_input["original_text"]
            self.field_data_item.data = pnr_input["original_field_data_item"]
        if request.method == "POST":
            body: dict = {"text": self.text.data, "field_data_item": self.field_data_item.data}
            self.response = Server.update_input_pnr(test_data_id, pnr_input["id"], body)

    def validate_text(self, _):
        if "error" in self.response and self.response["error"] and \
                "message" in self.response and self.response["message"]:
            raise ValidationError(self.response["message"])
        if "error_fields" in self.response and "text" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["text"])

    def validate_field_data_item(self, _):
        if "error_fields" in self.response and "field_data_item" in self.response["error_fields"]:
            raise ValidationError(self.response["error_fields"]["field_data_item"])


class RegisterFieldDataForm(FlaskForm):
    reg = StringField("Enter Register - Valid values are from R0 to R15")
    field_data = StringField("Enter Data - Input hex characters. Odd number of digit will be considered a number. "
                             "Prefix with 0 to make the number a digit. Non hex characters are considered as text. "
                             "Prefix with quote to enforce text.", validators=[InputRequired()])
    save = SubmitField("Save & Continue - Add Further Data")

    @staticmethod
    def validate_reg(_, reg: StringField) -> None:
        reg.data = reg.data.upper()
        if reg.data not in tpf2_app.config["REGISTERS"]:
            raise ValidationError("Invalid Register - Register can be from R0 to R15")
        return

    @staticmethod
    def validate_field_data(_, field_data: StringField) -> None:
        hex_data = form_validate_field_data(field_data.data)
        hex_data = hex_data[:8]
        hex_data = hex_data.zfill(8)
        field_data.data = hex_data


class TpfdfForm(FlaskForm):
    variation = SelectField(VARIATION_PROMPT, coerce=int)
    variation_name = StringField(VARIATION_NAME_PROMPT)
    macro_name = StringField("Enter the name of TPFDF macro", validators=[InputRequired()])
    key = StringField("Enter key as 2 hex characters",
                      validators=[InputRequired(), Length(min=2, max=2, message="Please enter 2 characters only")])
    field_data = TextAreaField(OLD_FIELD_DATA_PROMPT, render_kw={"rows": "5"}, validators=[InputRequired()])
    save = SubmitField("Save & Continue - Add Further Data")

    @staticmethod
    def validate_macro_name(_, macro_name: StringField):
        macro_name.data = form_validate_macro_name(macro_name.data)

    @staticmethod
    def validate_key(_, key: StringField):
        key.data = key.data.upper()
        try:
            int(key.data, 16)
        except ValueError:
            raise ValidationError("Invalid hex characters")
        return

    def validate_field_data(self, field_data: TextAreaField):
        field_data.data = form_validate_multiple_field_data(field_data.data, self.macro_name.data)


class DebugForm(FlaskForm):
    seg_list = StringField("Enter segment names separated by comma")
    save = SubmitField("Save & Continue - Add Further Data")

    @staticmethod
    def validate_seg_list(_, seg_list: StringField):
        updated_seg_list = list()
        response = Server.segments()
        segments: List[str] = response["segments"] if "segments" in response else list()
        for seg_name in seg_list.data.split(","):
            seg_name = seg_name.upper()
            if seg_name not in segments and seg_name != "STARTUP":
                raise ValidationError(f"Segment {seg_name} not present in the database")
            updated_seg_list.append(seg_name)
        seg_list.data = ",".join(updated_seg_list)


class FixedFileForm(FlaskForm):
    variation = SelectField(VARIATION_PROMPT, coerce=int)
    variation_name = StringField(VARIATION_NAME_PROMPT)
    macro_name = StringField("Fixed File - Macro Name", validators=[InputRequired()])
    rec_id = StringField("Fixed File - Record ID (4 hex characters or 2 alphabets)", validators=[InputRequired()])
    fixed_type = StringField("Fixed File - File Type (Equate name or number)", validators=[InputRequired()])
    fixed_ordinal = StringField("Fixed File - Ordinal Number (Even digit is hex or Odd digit is number)",
                                validators=[InputRequired()])
    fixed_fch_count = IntegerField("Fixed File - Number of Forward Chains", validators=[NumberRange(0, 100)], default=0,
                                   widget=Input(input_type="number"))
    fixed_fch_label = StringField("Fixed File - Forward Chain Label (Required only if number of forward chain is > 0")
    fixed_field_data = TextAreaField(f"Fixed File - Field Data ({OLD_FIELD_DATA_PROMPT})", render_kw={"rows": "3"})
    fixed_item_field = StringField("Fixed File Item - Item Label")
    fixed_item_adjust = BooleanField("Fixed File Item  - Check this ON if the item field data has similar field "
                                     "names as the item field name")
    fixed_item_repeat = IntegerField("Fixed File Item - No of times you want this item to be repeated (1 to 100)",
                                     validators=[NumberRange(0, 100)], default=1, widget=Input(input_type="number"))
    fixed_item_count = StringField("Fixed File Item - Item Count Label")
    fixed_item_field_data = TextAreaField(f"Fixed File - Item Field Data ({OLD_FIELD_DATA_PROMPT})",
                                          render_kw={"rows": "3"})
    pool_macro_name = StringField("Pool File - Macro Name")
    pool_rec_id = StringField("Pool File - Record Id (4 hex characters or 2 alphabets)")
    pool_index_field = StringField("Pool File - Field in Fixed File where reference of this pool file will be stored")
    pool_fch_count = IntegerField("Pool File - Number of Forward Chains", validators=[NumberRange(0, 100)], default=0,
                                  widget=Input(input_type="number"))
    pool_fch_label = StringField("Pool File - Forward Chain Label (Required only if number of forward chain is > 0")
    pool_field_data = TextAreaField(f"Pool File - Field Data ({OLD_FIELD_DATA_PROMPT})", render_kw={"rows": "3"})
    pool_item_field = StringField("Pool File Item - Item Label")
    pool_item_adjust = BooleanField("Pool File Item  - Check this ON if the item field data has similar field "
                                    "names as the item field name")
    pool_item_repeat = IntegerField("Pool File Item - No of times you want this item to be repeated (1 to 100)",
                                    validators=[NumberRange(0, 100)], default=1, widget=Input(input_type="number"))
    pool_item_count = StringField("Pool File Item - Item Count Label")
    pool_item_field_data = TextAreaField(f"Pool File - Item Field Data ({OLD_FIELD_DATA_PROMPT})",
                                         render_kw={"rows": "3"})
    save = SubmitField("Save & Continue - Add Further Data")

    @staticmethod
    def _validate_record_id(data: str) -> str:
        if len(data) != 2 and len(data) != 4:
            raise ValidationError("Record ID must be 2 or 4 digits")
        data = data.upper()
        if len(data) == 2:
            if data == "00":
                raise ValidationError("Record ID cannot be zeroes")
            data = data.encode("cp037").hex().upper()
        else:
            if data == "0000":
                raise ValidationError("Record ID cannot be zeroes")
            try:
                int(data, 16)
            except ValueError:
                raise ValidationError("Invalid hex characters")
        return data

    @staticmethod
    def validate_macro_name(_, macro_name: StringField):
        macro_name.data = form_validate_macro_name(macro_name.data)

    def validate_rec_id(self, rec_id: StringField):
        rec_id.data = self._validate_record_id(rec_id.data)

    @staticmethod
    def validate_fixed_type(_, fixed_type: StringField):
        fixed_type.data = fixed_type.data.upper()
        if not fixed_type.data.isdigit():
            label_ref = Server.search_field(fixed_type.data)
            if not label_ref:
                raise ValidationError(f"Equate {fixed_type.data} not found")
            fixed_type.data = str(label_ref["dsp"])
        return

    @staticmethod
    def validate_fixed_ordinal(_, fixed_ordinal: StringField):
        fixed_ordinal.data = fixed_ordinal.data.upper()
        if len(fixed_ordinal.data) % 2 == 0:
            try:
                int(fixed_ordinal.data, 16)
            except ValueError:
                raise ValidationError("Invalid hex characters")
        else:
            if not fixed_ordinal.data.isdigit():
                raise ValidationError("Invalid number")
            fixed_ordinal.data = hex(int(fixed_ordinal.data))[2:].upper()
            fixed_ordinal.data = fixed_ordinal.data if len(fixed_ordinal.data) % 2 == 0 else "0" + fixed_ordinal.data
        return

    def validate_fixed_fch_label(self, fixed_fch_label: StringField):
        if self.fixed_fch_count.data > 0 and not fixed_fch_label.data:
            raise ValidationError("Forward chain label required if forward chain count > 0")
        if fixed_fch_label.data:
            fixed_fch_label.data = form_field_lookup(fixed_fch_label.data, self.macro_name.data)
        return

    def validate_fixed_field_data(self, fixed_field_data: TextAreaField):
        if not fixed_field_data.data:
            return
        fixed_field_data.data = form_validate_multiple_field_data(fixed_field_data.data, self.macro_name.data)

    def validate_fixed_item_field(self, fixed_item_field: StringField):
        if not fixed_item_field.data:
            return
        fixed_item_field.data = form_field_lookup(fixed_item_field.data, self.macro_name.data)

    def validate_fixed_item_count(self, fixed_item_count: StringField):
        if not fixed_item_count.data:
            return
        fixed_item_count.data = form_field_lookup(fixed_item_count.data, self.macro_name.data)

    def validate_fixed_item_field_data(self, fixed_item_field_data: StringField):
        if not fixed_item_field_data.data and self.fixed_item_field.data:
            raise ValidationError("Item field data required when item field specified")
        if not fixed_item_field_data.data:
            return
        fixed_item_field_data.data = form_validate_multiple_field_data(fixed_item_field_data.data, self.macro_name.data)

    @staticmethod
    def validate_pool_macro_name(_, pool_macro_name: StringField):
        if not pool_macro_name.data:
            return
        pool_macro_name.data = form_validate_macro_name(pool_macro_name.data)

    def validate_pool_rec_id(self, pool_rec_id: StringField):
        if not pool_rec_id.data and self.pool_macro_name.data:
            raise ValidationError("Pool Record ID required if Pool Macro Name is specified")
        if not pool_rec_id.data:
            return
        if not self.pool_macro_name.data:
            raise ValidationError("Specify Pool Macro Name before specifying Record ID")
        pool_rec_id.data = self._validate_record_id(pool_rec_id.data)

    def validate_pool_index_field(self, pool_index_field: StringField):
        if not pool_index_field.data and self.pool_macro_name.data:
            raise ValidationError("Index Field required if Pool Macro Name is specified")
        if not pool_index_field.data:
            return
        if not self.pool_macro_name.data:
            raise ValidationError("Specify Pool Macro Name before specifying this field")
        pool_index_field.data = form_field_lookup(pool_index_field.data, self.macro_name.data)

    def validate_pool_fch_label(self, pool_fch_label: StringField):
        if self.pool_fch_count.data > 0 and not pool_fch_label.data:
            raise ValidationError("Forward chain label required if forward chain count > 0")
        if not pool_fch_label.data:
            return
        if not self.pool_macro_name.data:
            raise ValidationError("Specify Pool Macro Name before specifying this field")
        pool_fch_label.data = form_field_lookup(pool_fch_label.data, self.pool_macro_name.data)
        return

    def validate_pool_field_data(self, pool_field_data: TextAreaField):
        if not pool_field_data.data:
            return
        if not self.pool_macro_name.data:
            raise ValidationError("Specify Pool Macro Name before specifying this field")
        pool_field_data.data = form_validate_multiple_field_data(pool_field_data.data, self.pool_macro_name.data)

    def validate_pool_item_field(self, pool_item_field: StringField):
        if not pool_item_field.data:
            return
        if not self.pool_macro_name.data:
            raise ValidationError("Specify Pool Macro Name before specifying this field")
        pool_item_field.data = form_field_lookup(pool_item_field.data, self.pool_macro_name.data)

    def validate_pool_item_count(self, pool_item_count: StringField):
        if not pool_item_count.data:
            return
        if not self.pool_macro_name.data:
            raise ValidationError("Specify Pool Macro Name before specifying this field")
        pool_item_count.data = form_field_lookup(pool_item_count.data, self.pool_macro_name.data)

    def validate_pool_item_field_data(self, pool_item_field_data: StringField):
        if not pool_item_field_data.data and self.pool_item_field.data:
            raise ValidationError("Item field data required when item field specified")
        if not pool_item_field_data.data:
            return
        if not self.pool_macro_name.data:
            raise ValidationError("Specify Pool Macro Name before specifying this field")
        pool_item_field_data.data = form_validate_multiple_field_data(pool_item_field_data.data,
                                                                      self.pool_macro_name.data)


class RenameCopyVariation(FlaskForm):
    new_name = StringField("New Variation Name")
    save = SubmitField("___ Variation")

    def __init__(self, test_data_id: str, td_element: dict, v_type: str, action: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = [("Variation Name", td_element["variation_name"])]
        self.response: dict = dict()
        self.save.label.text = "Rename Variation" if action == "rename" else "Copy Variation"
        if request.method == "GET":
            self.new_name.data = td_element["variation_name"]
            if action == "copy":
                self.new_name.data = f"{self.new_name.data} - Copy"
        if request.method == "POST":
            body = {"new_name": self.new_name.data}
            if action == "rename":
                self.response = Server.rename_variation(test_data_id, v_type, td_element["variation"], body)
            else:
                self.response = Server.copy_variation(test_data_id, v_type, td_element["variation"], body)

    def validate_new_name(self, _):
        if "error" in self.response and self.response["error"]:
            if "message" in self.response and self.response["message"]:
                raise ValidationError(self.response["message"])
            if "new_name" in self.response["error_fields"]:
                raise ValidationError(self.response["error_fields"]["new_name"])
        return
