from urllib.parse import unquote

from flask import url_for, render_template, request, flash
from munch import Munch
from werkzeug.utils import redirect

from d29_frontend.flask_app import tpf2_app
from d29_frontend.flask_app.server import Server, RequestType
from d29_frontend.flask_app.template_constants import TemplateConstant, LINK_DELETE
from d29_frontend.flask_app.template_forms import TemplateRenameCopyForm, PnrCreateForm, PnrAddForm, PnrUpdateForm, \
    TemplateDeleteForm, GlobalCreateForm, GlobalAddForm, \
    GlobalUpdateForm, AaaCreateForm, AaaUpdateForm, TemplateMergeLinkForm, TemplateUpdateLinkForm
from d29_frontend.flask_app.user import cookie_login_required, error_check, flash_message


@tpf2_app.route("/templates/<string:template_type>")
@cookie_login_required
@error_check
def view_templates(template_type: str):
    tc = TemplateConstant(template_type)
    if not tc.is_type_valid:
        flash("Invalid Template Type")
        return redirect(url_for("home"))
    templates = Server.get_templates(tc.type.lower())
    return render_template("template_list.html", title=f"{tc.type} templates", templates=templates, tc=tc)


@tpf2_app.route("/templates/name", methods=["GET", "POST"])
@cookie_login_required
@error_check
def view_template():
    name = unquote(request.args.get("name", str()))
    templates = Server.get_template_by_name(name)
    if not templates:
        flash("Template not found.")
        return redirect(url_for("home"))
    tc = TemplateConstant(templates[0].type)
    if not tc.is_type_valid:
        flash("Invalid Template Type")
        return redirect(url_for("home"))
    form = TemplateDeleteForm(name)
    if not form.validate_on_submit():
        return render_template("template_view.html", title="Template", templates=templates, form=form, name=name, tc=tc)
    flash_message(form.response)
    return redirect(url_for("view_template", name=name)) if form.template_id.data \
        else redirect(url_for("view_templates", template_type=tc.type))


@tpf2_app.route("/templates/rename", methods=["GET", "POST"])
@cookie_login_required
@error_check
def rename_template():
    name = unquote(request.args.get("name", str()))
    templates = Server.get_template_by_name(name)
    if not templates:
        return redirect(url_for("view_template", name=name))
    form = TemplateRenameCopyForm(templates[0], action="rename")
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Rename Template", form=form, name=name)
    flash_message(form.response)
    return redirect(url_for("view_template", name=form.name.data))


@tpf2_app.route("/templates/copy", methods=["GET", "POST"])
@cookie_login_required
@error_check
def copy_template():
    name = unquote(request.args.get("name", str()))
    templates = Server.get_template_by_name(name)
    if not templates:
        return redirect(url_for("view_template", name=name))
    form = TemplateRenameCopyForm(templates[0], action="copy")
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Copy Template", form=form, name=name)
    flash_message(form.response)
    return redirect(url_for("view_template", name=form.name.data))


@tpf2_app.route("/templates/pnr/create", methods=["GET", "POST"])
@cookie_login_required
@error_check
def create_pnr_template():
    form = PnrCreateForm()
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Create PNR Template", form=form, name=str())
    flash_message(form.response)
    return redirect(url_for("view_template", name=form.name.data))


@tpf2_app.route("/templates/global/create", methods=["GET", "POST"])
@cookie_login_required
@error_check
def create_global_template():
    form = GlobalCreateForm()
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Create Global Template", form=form, name=str())
    flash_message(form.response)
    return redirect(url_for("view_template", name=form.name.data))


@tpf2_app.route("/templates/aaa/create", methods=["GET", "POST"])
@cookie_login_required
@error_check
def create_aaa_template():
    form = AaaCreateForm()
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Create AAA Template", form=form, name=str())
    flash_message(form.response)
    return redirect(url_for("view_template", name=form.name.data))


@tpf2_app.route("/templates/pnr/add", methods=["GET", "POST"])
@cookie_login_required
@error_check
def add_pnr_template():
    name = unquote(request.args.get("name", str()))
    form = PnrAddForm(name)
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Add to PNR Template", form=form, name=name)
    flash_message(form.response)
    return redirect(url_for("view_template", name=name))


@tpf2_app.route("/templates/global/add", methods=["GET", "POST"])
@cookie_login_required
@error_check
def add_global_template():
    name = unquote(request.args.get("name", str()))
    form = GlobalAddForm(name)
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Add to Global Template", form=form, name=name)
    flash_message(form.response)
    return redirect(url_for("view_template", name=name))


@tpf2_app.route("/templates/pnr/update/<string:template_id>", methods=["GET", "POST"])
@cookie_login_required
@error_check
def update_pnr_template(template_id: str):
    template: Munch = Server.get_template_by_id(template_id)
    if not template:
        flash("Error in updating. Template not found")
        return redirect(url_for("view_pnr_templates"))
    form = PnrUpdateForm(template)
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Update PNR Template", form=form, name=template.name)
    flash_message(form.response)
    return redirect(url_for("view_template", name=template.name))


@tpf2_app.route("/templates/global/update/<string:template_id>", methods=["GET", "POST"])
@cookie_login_required
@error_check
def update_global_template(template_id: str):
    template: Munch = Server.get_template_by_id(template_id)
    if not template:
        flash("Error in updating. Template not found")
        return redirect(url_for("view_pnr_templates"))
    form = GlobalUpdateForm(template)
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Update Global Template", form=form, name=template.name)
    flash_message(form.response)
    return redirect(url_for("view_template", name=template.name))


@tpf2_app.route("/templates/aaa/update/<string:template_id>", methods=["GET", "POST"])
@cookie_login_required
@error_check
def update_aaa_template(template_id: str):
    template: Munch = Server.get_template_by_id(template_id)
    if not template:
        flash("Error in updating. Template not found")
        return redirect(url_for("view_pnr_templates"))
    form = AaaUpdateForm(template)
    if not form.validate_on_submit():
        return render_template("template_form.html", title="Update AAA Template", form=form, name=template.name)
    flash_message(form.response)
    return redirect(url_for("view_template", name=template.name))


@tpf2_app.route("/test_data/<test_data_id>/templates/<template_type>/<action_type>", methods=["GET", "POST"])
@cookie_login_required
@error_check
def merge_link_template(test_data_id: str, template_type: str, action_type: str):
    form = TemplateMergeLinkForm(test_data_id, template_type, action_type)
    if not form.validate_on_submit():
        return render_template("test_data_form.html", title=f"{action_type.title()} {template_type.upper()} Template",
                               form=form, test_data_id=test_data_id)
    flash_message(form.response)
    anchor = TemplateConstant(template_type).anchor
    return redirect(url_for("confirm_test_data", test_data_id=test_data_id, _anchor=anchor))


@tpf2_app.route("/test_data/<test_data_id>/templates/<template_type>/<t_name>/variations/<int:variation>/<v_name>/",
                methods=["GET", "POST"])
@cookie_login_required
@error_check
def update_link_template(test_data_id: str, template_type: str, t_name: str, variation: int, v_name: str):
    element: Munch = Munch(test_data_id=test_data_id, template_type=template_type, template_name=unquote(t_name),
                           variation=variation, variation_name=unquote(v_name))
    form = TemplateUpdateLinkForm(element)
    if not form.validate_on_submit():
        return render_template("test_data_form.html", title=f"Update Link to {template_type} Template", form=form,
                               test_data_id=test_data_id)
    flash_message(form.response)
    anchor = TemplateConstant(template_type).anchor
    return redirect(url_for("confirm_test_data", test_data_id=test_data_id, _anchor=anchor))


@tpf2_app.route("/test_data/<test_data_id>/templates/<template_type>/<t_name>/variations/<int:variation>/",
                methods=["GET"])
@cookie_login_required
@error_check
def delete_link_template(test_data_id: str, template_type: str, t_name: str, variation: int):
    body = RequestType.TEMPLATE_LINK_DELETE
    body.template_name = unquote(t_name)
    body.variation = variation
    response = Server.merge_link_template(test_data_id, body.__dict__, template_type, LINK_DELETE)
    flash_message(response)
    anchor = TemplateConstant(template_type).anchor
    return redirect(url_for("confirm_test_data", test_data_id=test_data_id, _anchor=anchor))
