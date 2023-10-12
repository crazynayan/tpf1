from typing import List

from flask import request
from flask_wtf import FlaskForm
from munch import Munch
from wtforms import StringField, SelectMultipleField, SubmitField

from d29_frontend.flask_app.form_prompts import evaluate_error
from d29_frontend.flask_app.server import Server, RequestType


class ProfilerRunForm(FlaskForm):
    seg_name: StringField = StringField("Segment Name (Must exists in the system)")
    test_data_list: SelectMultipleField = SelectMultipleField("Select all test data that covers the above segment")
    submit: SubmitField = SubmitField("Run Profiler")

    def __init__(self, test_data_list: List[Munch], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_data_list.choices = [(test_data.id, test_data.name) for test_data in test_data_list]
        self.response = Munch()
        if request.method == "POST":
            body = RequestType().profiler_run
            body.seg_name = self.seg_name.data
            body.test_data_ids = self.test_data_list.data
            self.response = Server.run_profiler(body.__dict__)
        return

    def validate_seg_name(self, _):
        evaluate_error(self.response, "seg_name")

    def validate_test_data_list(self, _):
        evaluate_error(self.response, "test_data_ids")
