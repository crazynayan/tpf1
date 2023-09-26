from typing import List

from flask import render_template, redirect, url_for
from flask_login import current_user

from d29_frontend.flask_app import tpf2_app
from d29_frontend.flask_app.forms import UploadForm
from d29_frontend.flask_app.server import Server
from d29_frontend.flask_app.user import cookie_login_required


@tpf2_app.route("/")
@tpf2_app.route("/index")
def home():
    return render_template("home.html")


@tpf2_app.route("/segments")
@cookie_login_required
def segments():
    response = Server.segments()
    if not current_user.is_authenticated:
        return redirect(url_for("logout"))
    segment_attributes = [(seg_name, response["attributes"][seg_name]) for seg_name in response["segments"]]
    return render_template("segments.html", title="Segments", segments=segment_attributes)


@tpf2_app.route("/segments/upload", methods=["GET", "POST"])
@cookie_login_required
def upload_segments():
    form = UploadForm()
    if not form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for("logout"))
        return render_template("upload_form.html", form=form, title="Upload", response=dict())
    response: dict = Server.upload_segment(form.blob_name)
    if not current_user.is_authenticated:
        return redirect(url_for("logout"))
    return render_template("upload_form.html", form=form, title="Upload", response=response)


@tpf2_app.route("/segments/<string:seg_name>/instructions")
@cookie_login_required
def instructions(seg_name: str):
    response: dict = Server.instructions(seg_name)
    total_count: int = len(response["formatted_instructions"])
    unsupported_count: int = len(response["formatted_not_supported"])
    supported_percentage: int = (total_count - unsupported_count) * 100 // total_count if total_count > 0 else 0
    if not current_user.is_authenticated:
        return redirect(url_for("logout"))
    return render_template("instructions.html", title="Assembly", instructions=response["formatted_instructions"],
                           seg_name=seg_name, not_supported_instructions=response["formatted_not_supported"],
                           response=response, supported_percentage=supported_percentage)


@tpf2_app.route("/macros")
@cookie_login_required
def macros():
    macro_list: List[str] = Server.macros()
    if not current_user.is_authenticated:
        return redirect(url_for("logout"))
    return render_template("macros.html", title="Data Macro", macros=macro_list)


@tpf2_app.route("/macro/<string:macro_name>/instructions")
@cookie_login_required
def symbol_table_view(macro_name: str):
    symbol_table: List[dict] = Server.symbol_table(macro_name)
    if not current_user.is_authenticated:
        return redirect(url_for("logout"))
    return render_template("symbol_table.html", title="Symbol Table", symbol_table=symbol_table, macro_name=macro_name)


@tpf2_app.route("/unsupported_instructions")
@cookie_login_required
def unsupported_instructions():
    commands: dict = Server.unsupported_instructions()
    if not current_user.is_authenticated:
        return redirect(url_for("logout"))
    return render_template("unsupported_instructions.html", title="Unsupported Instructions",
                           commands=commands["unsupported_instructions"])
