from flask import request
from flask_wtf import FlaskForm
from munch import Munch
from wtforms import SelectField, StringField, TextAreaField, SubmitField, HiddenField, BooleanField

from d29_frontend.config import Config
from d29_frontend.flask_app.form_prompts import PNR_KEY_PROMPT, PNR_LOCATOR_PROMPT, PNR_TEXT_PROMPT, PNR_INPUT_FIELD_DATA_PROMPT, \
    TEMPLATE_NAME_PROMPT, TEMPLATE_DESCRIPTION_PROMPT, VARIATION_PROMPT, VARIATION_NAME_PROMPT, GLOBAL_NAME_PROMPT, \
    IS_GLOBAL_RECORD_PROMPT, GLOBAL_HEX_DATA_PROMPT, GLOBAL_SEG_NAME_PROMPT, GLOBAL_FIELD_DATA_PROMPT, \
    MACRO_FIELD_DATA_PROMPT, evaluate_error, init_body
from d29_frontend.flask_app.server import Server, RequestType
from d29_frontend.flask_app.template_constants import PNR, GLOBAL, AAA, LINK_UPDATE


class PnrCreateForm(FlaskForm):
    template_type = PNR
    name = StringField(TEMPLATE_NAME_PROMPT)
    description = TextAreaField(TEMPLATE_DESCRIPTION_PROMPT, render_kw={"rows": "5"})
    key = SelectField(PNR_KEY_PROMPT, choices=Config.PNR_KEYS, default="header")
    locator = StringField(PNR_LOCATOR_PROMPT)
    text = StringField(PNR_TEXT_PROMPT)
    field_data = TextAreaField(PNR_INPUT_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Create New PNR Template")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: Munch = Munch()
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEMPLATE_PNR_CREATE)
            self.response = Server.create_new_pnr_template(body)

    def validate_name(self, _):
        evaluate_error(self.response, "name", message=True)

    def validate_description(self, _):
        evaluate_error(self.response, "description")

    def validate_key(self, _):
        evaluate_error(self.response, "key")

    def validate_locator(self, _):
        evaluate_error(self.response, "locator")

    def validate_text(self, _):
        evaluate_error(self.response, "text")

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data")


class GlobalCreateForm(FlaskForm):
    template_type = GLOBAL
    name = StringField(TEMPLATE_NAME_PROMPT)
    description = TextAreaField(TEMPLATE_DESCRIPTION_PROMPT, render_kw={"rows": "5"})
    global_name = StringField(GLOBAL_NAME_PROMPT)
    is_global_record = BooleanField(IS_GLOBAL_RECORD_PROMPT)
    hex_data = StringField(GLOBAL_HEX_DATA_PROMPT)
    seg_name = StringField(GLOBAL_SEG_NAME_PROMPT)
    field_data = TextAreaField(GLOBAL_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Create New Global Template")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: Munch = Munch()
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEMPLATE_GLOBAL_CREATE)
            self.response = Server.create_new_global_template(body)

    def validate_name(self, _):
        evaluate_error(self.response, "name", message=True)

    def validate_description(self, _):
        evaluate_error(self.response, "description")

    def validate_global_name(self, _):
        evaluate_error(self.response, "global_name")

    def validate_is_global_record(self, _):
        evaluate_error(self.response, "is_global_record")

    def validate_hex_data(self, _):
        evaluate_error(self.response, "hex_data")

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data")

    def validate_seg_name(self, _):
        evaluate_error(self.response, "seg_name")


class AaaCreateForm(FlaskForm):
    template_type = AAA
    name = StringField(TEMPLATE_NAME_PROMPT)
    description = TextAreaField(TEMPLATE_DESCRIPTION_PROMPT, render_kw={"rows": "5"})
    field_data = TextAreaField(MACRO_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Create New AAA Template")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: Munch = Munch()
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEMPLATE_AAA_CREATE)
            self.response = Server.create_new_aaa_template(body)

    def validate_name(self, _):
        evaluate_error(self.response, "name", message=True)

    def validate_description(self, _):
        evaluate_error(self.response, "description")

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data")


class PnrAddForm(FlaskForm):
    key = SelectField(f"{PNR_KEY_PROMPT} (Only select a key that is not already added)", choices=Config.PNR_KEYS,
                      default="header")
    text = StringField(PNR_TEXT_PROMPT)
    field_data = TextAreaField(PNR_INPUT_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Add Key To PNR Template")

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: Munch = Munch()
        self.display_fields = [("Name", name)]
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEMPLATE_PNR_ADD)
            body.name = name
            self.response = Server.add_to_existing_pnr_template(body)

    def validate_key(self, _):
        evaluate_error(self.response, ["key", "name"], message=True)

    def validate_text(self, _):
        evaluate_error(self.response, "text")

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data")


class GlobalAddForm(FlaskForm):
    global_name = StringField(GLOBAL_NAME_PROMPT)
    is_global_record = BooleanField(IS_GLOBAL_RECORD_PROMPT)
    hex_data = StringField(GLOBAL_HEX_DATA_PROMPT)
    seg_name = StringField(GLOBAL_SEG_NAME_PROMPT)
    field_data = TextAreaField(GLOBAL_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Add Global To Template")

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: Munch = Munch()
        self.display_fields = [("Name", name)]
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEMPLATE_GLOBAL_ADD)
            body.name = name
            self.response = Server.add_to_existing_global_template(body)

    def validate_global_name(self, _):
        evaluate_error(self.response, ["name", "global_name"], message=True)

    def validate_is_global_record(self, _):
        evaluate_error(self.response, "is_global_record")

    def validate_hex_data(self, _):
        evaluate_error(self.response, "hex_data")

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data")

    def validate_seg_name(self, _):
        evaluate_error(self.response, "seg_name")


class PnrUpdateForm(FlaskForm):
    text = StringField(PNR_TEXT_PROMPT)
    field_data = TextAreaField(PNR_INPUT_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Update PNR")

    def __init__(self, template: Munch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        self.display_fields.append(("Name", template.name))
        pwc = f"{' (PNR Working copy)' if template.locator == Config.AAAPNR else str()}"
        self.display_fields.append(("PNR Locator", f"{template.locator}{pwc}"))
        self.display_fields.append(("Key", template.key.upper()))
        self.response: Munch = Munch()
        if request.method == "GET":
            self.text.data = template.text
            self.field_data.data = template.field_data
        if request.method == "POST":
            body: dict = init_body(self.data, RequestType.TEMPLATE_PNR_UPDATE)
            self.response = Server.update_pnr_template(template.id, body)
        return

    def validate_text(self, _):
        evaluate_error(self.response, "text", message=True)

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data")


class GlobalUpdateForm(FlaskForm):
    is_global_record = BooleanField(IS_GLOBAL_RECORD_PROMPT)
    hex_data = StringField(GLOBAL_HEX_DATA_PROMPT)
    seg_name = StringField(GLOBAL_SEG_NAME_PROMPT)
    field_data = TextAreaField(GLOBAL_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Update Global")

    def __init__(self, template: Munch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        self.display_fields.append(("Template Name", template.name))
        self.display_fields.append(("Global Name", template.global_name))
        self.response: Munch = Munch()
        if request.method == "GET":
            self.is_global_record.data = template.is_global_record
            self.hex_data.data = template.hex_data
            self.field_data.data = template.field_data
            self.seg_name.data = template.seg_name
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEMPLATE_GLOBAL_UPDATE)
            self.response = Server.update_global_template(template.id, body)

    def validate_is_global_record(self, _):
        evaluate_error(self.response, "is_global_record", message=True)

    def validate_hex_data(self, _):
        evaluate_error(self.response, "hex_data")

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data")

    def validate_seg_name(self, _):
        evaluate_error(self.response, "seg_name")


class AaaUpdateForm(FlaskForm):
    field_data = TextAreaField(MACRO_FIELD_DATA_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Update AAA")

    def __init__(self, template: Munch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        self.display_fields.append(("Template Name", template.name))
        self.response: Munch = Munch()
        if request.method == "GET":
            self.field_data.data = template.field_data
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEMPLATE_AAA_UPDATE)
            self.response = Server.update_aaa_template(template.id, body)

    def validate_field_data(self, _):
        evaluate_error(self.response, "field_data", message=True)


class TemplateRenameCopyForm(FlaskForm):
    name = StringField(TEMPLATE_NAME_PROMPT)
    description = TextAreaField(TEMPLATE_DESCRIPTION_PROMPT, render_kw={"rows": "5"})
    save = SubmitField("Template")

    def __init__(self, template: Munch, action: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = [("Existing Name", template.name)]
        self.response: Munch = Munch()
        self.save.label.text = "Rename Template" if action == "rename" else "Copy Template"
        if request.method == "GET" and action == "rename":
            self.name.data = template.name
            self.description.data = template.description
        if request.method == "POST":
            body = {"old_name": template.name, "new_name": self.name.data, "description": self.description.data}
            self.response = Server.rename_template(body) if action == "rename" else Server.copy_template(body)

    def validate_name(self, _):
        evaluate_error(self.response, ["new_name", "old_name"], message=True)

    def validate_description(self, _):
        evaluate_error(self.response, "description")


class TemplateDeleteForm(FlaskForm):
    template_id = HiddenField()
    submit = SubmitField("Yes - Delete")

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: Munch = Munch()
        if request.method == "POST":
            if self.template_id.data:
                self.response = Server.delete_template_by_id(self.template_id.data)
            else:
                self.response = Server.delete_template_by_name({"name": name})


class TemplateMergeLinkForm(FlaskForm):
    variation = SelectField(VARIATION_PROMPT, coerce=int)
    variation_name = StringField(VARIATION_NAME_PROMPT)
    template_name = SelectField("Select a template")
    save = SubmitField("Template with Test Data")

    def __init__(self, test_data_id: str, template_type: str, action_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rsp: Munch = Server.get_templates_and_test_data_variations(template_type, test_data_id)
        self.variation.choices = rsp.variation_choices
        self.template_name.choices = [(template.name, template.name) for template in rsp.templates]
        self.save.label.text = f"{action_type.title()} {self.save.label.text}"
        self.response: Munch = Munch()
        if request.method == "POST":
            body = init_body(self.data, RequestType.TEMPLATE_MERGE_LINK)
            self.response = Server.merge_link_template(test_data_id, body, template_type, action_type)

    def validate_variation(self, _):
        evaluate_error(self.response, "variation", message=True)

    def validate_variation_name(self, _):
        evaluate_error(self.response, "variation_name")

    def validate_template_name(self, _):
        evaluate_error(self.response, "template_name")


class TemplateUpdateLinkForm(FlaskForm):
    new_template_name = SelectField("Select a template")
    save = SubmitField("Update links")

    def __init__(self, element: Munch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        self.display_fields.append(("Variation", element.variation_name))
        self.display_fields.append(("Template Name", element.template_name))
        templates: Munch = Server.get_templates(template_type=element.template_type)
        self.new_template_name.choices = [(template.name, template.name) for template in templates]
        self.response = Munch()
        if request.method == "POST":
            body = RequestType.TEMPLATE_LINK_UPDATE
            body.template_name = element.template_name
            body.variation = element.variation
            body.new_template_name = self.new_template_name.data
            self.response = Server.merge_link_template(element.test_data_id, body.__dict__, element.template_type,
                                                       LINK_UPDATE)
        else:
            self.new_template_name.data = element.template_name

    def validate_new_template_name(self, _):
        evaluate_error(self.response, "new_template_name", message=True)


class CommentUpdateForm(FlaskForm):
    comment = TextAreaField("Enter comment", render_kw={"rows": "5"})
    save = SubmitField("Save")

    def __init__(self, test_result: Munch, comment_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ref = {
            "user_comment": ("Ending At", test_result.last_node),
            "pnr_comment": ("PNR Data", test_result.pnr_field_data),
            "core_comment": ("Field Data", test_result.core_field_data),
            "general_comment": ("General Observation", "A common comment for the entire result.")
        }
        self.display_fields = list()
        self.display_fields.append(("Name", test_result.name))
        self.display_fields.append(("Result No.", test_result.result_id))
        if comment_type in ref:
            self.display_fields.append(ref[comment_type])
        self.response = Munch()
        if request.method == "POST":
            body = RequestType.RESULT_COMMENT_UPDATE
            body.comment_type = comment_type
            body.comment = self.comment.data
            self.response = Server.update_comment(test_result.id, body.__dict__)
        else:
            self.comment.data = test_result.get(comment_type)

    def validate_comment(self, _):
        evaluate_error(self.response, ["comment", "comment_type"], message=True)


class SaveResultForm(FlaskForm):
    name = StringField("Enter Test Result Name (It must be unique)")
    save = SubmitField("Save Test Result")

    def __init__(self, test_data_id, test_data_name, seg_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_fields = list()
        self.display_fields.append(("Test Data Name", test_data_name))
        self.display_fields.append(("Start Seg", seg_name))
        self.response = Munch()
        if request.method == "POST":
            self.response = Server.save_test_results(test_data_id, self.name.data)
        else:
            self.name.data = test_data_name

    def validate_name(self, _):
        evaluate_error(self.response, "name", message=True)
