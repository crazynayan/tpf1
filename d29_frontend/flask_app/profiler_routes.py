from typing import List

from flask import render_template
from munch import Munch

from d29_frontend.flask_app import tpf2_app
from d29_frontend.flask_app.profiler_forms import ProfilerRunForm
from d29_frontend.flask_app.server import Server
from d29_frontend.flask_app.user import cookie_login_required, error_check


@tpf2_app.route("/profiler/run", methods=["GET", "POST"])
@cookie_login_required
@error_check
def profiler_run():
    test_data_list: List[Munch] = Server.get_all_test_data().test_data_list
    form: ProfilerRunForm = ProfilerRunForm(test_data_list)
    if not form.validate_on_submit():
        return render_template("profiler_form.html", title="Run Profiler", form=form)
    title: str = f"{form.seg_name.data.upper()} Profiler"
    return render_template("profiler_data.html", title=title, data=form.response.data)
