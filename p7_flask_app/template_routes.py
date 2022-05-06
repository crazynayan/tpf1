from types import SimpleNamespace
from urllib.parse import unquote

from flask import jsonify, request, Response

from p3_db.template_crud import create_new_pnr_template, add_to_existing_pnr_template, get_templates_by_type, \
    get_templates_by_name, rename_template, update_pnr_template, delete_template_by_id, delete_template_by_name, \
    get_templates_by_id, copy_template, create_new_global_template, add_to_existing_global_template, \
    update_global_template, create_new_aaa_template, update_aaa_template, get_variations
from p3_db.template_merge import process_merge_link
from p3_db.template_models import PNR, GLOBAL, AAA, TD_REF
from p7_flask_app import tpf1_app
from p7_flask_app.auth import token_auth
from p7_flask_app.route_decorators import test_data_required, role_check_required


@tpf1_app.route("/templates/pnr/create", methods=["POST"])
@token_auth.login_required
def templates_pnr_create():
    return jsonify(create_new_pnr_template(request.get_json()))


@tpf1_app.route("/templates/global/create", methods=["POST"])
@token_auth.login_required
def templates_global_create():
    return jsonify(create_new_global_template(request.get_json()))


@tpf1_app.route("/templates/aaa/create", methods=["POST"])
@token_auth.login_required
def templates_aaa_create():
    return jsonify(create_new_aaa_template(request.get_json()))


@tpf1_app.route("/templates/pnr/add", methods=["POST"])
@token_auth.login_required
def templates_pnr_add():
    return jsonify(add_to_existing_pnr_template(request.get_json()))


@tpf1_app.route("/templates/global/add", methods=["POST"])
@token_auth.login_required
def templates_global_add():
    return jsonify(add_to_existing_global_template(request.get_json()))


@tpf1_app.route("/templates/pnr", methods=["GET"])
@token_auth.login_required
def templates_pnr_get():
    return jsonify(get_templates_by_type(PNR))


@tpf1_app.route("/templates/global", methods=["GET"])
@token_auth.login_required
def templates_global_get():
    return jsonify(get_templates_by_type(GLOBAL))


@tpf1_app.route("/templates/aaa", methods=["GET"])
@token_auth.login_required
def templates_aaa_get():
    return jsonify(get_templates_by_type(AAA))


@tpf1_app.route("/templates/<string:template_id>/pnr/update", methods=["POST"])
@token_auth.login_required
def templates_pnr_update(template_id: str):
    return jsonify(update_pnr_template(template_id, request.get_json()))


@tpf1_app.route("/templates/<string:template_id>/global/update", methods=["POST"])
@token_auth.login_required
def templates_global_update(template_id: str):
    return jsonify(update_global_template(template_id, request.get_json()))


@tpf1_app.route("/templates/<string:template_id>/aaa/update", methods=["POST"])
@token_auth.login_required
def templates_aaa_update(template_id: str):
    return jsonify(update_aaa_template(template_id, request.get_json()))


@tpf1_app.route("/templates/<string:template_id>", methods=["GET"])
@token_auth.login_required
def templates_get_by_id(template_id: str):
    return jsonify(get_templates_by_id(template_id))


@tpf1_app.route("/templates/name", methods=["GET"])
@token_auth.login_required
def templates_name_get():
    name = unquote(request.args.get("name", str()))
    return jsonify(get_templates_by_name(name))


@tpf1_app.route("/templates/rename", methods=["POST"])
@token_auth.login_required
def templates_rename():
    return jsonify(rename_template(request.get_json()))


@tpf1_app.route("/templates/copy", methods=["POST"])
@token_auth.login_required
def templates_copy():
    return jsonify(copy_template(request.get_json()))


@tpf1_app.route("/templates/<string:template_id>", methods=["DELETE"])
@token_auth.login_required
def templates_delete(template_id: str):
    return jsonify(delete_template_by_id(template_id))


@tpf1_app.route("/templates/name/delete", methods=["POST"])
@token_auth.login_required
def templates_name_delete():
    return jsonify(delete_template_by_name(request.get_json()))


@tpf1_app.route("/test_data/<test_data_id>/templates/<template_type>/<action_type>", methods=["POST"])
@token_auth.login_required
@test_data_required
@role_check_required
def templates_process(test_data_id: str, template_type: str, action_type: str, **kwargs) -> Response:
    return jsonify(process_merge_link(action_type, kwargs[test_data_id], request.get_json(), template_type))


@tpf1_app.route("/templates/<template_type>/test_data/<test_data_id>", methods=["GET"])
@token_auth.login_required
def templates_variations_get(template_type, test_data_id) -> Response:
    rsp = SimpleNamespace()
    rsp.templates = get_templates_by_type(template_type)
    rsp.variation_choices = get_variations(test_data_id, TD_REF[template_type]) if template_type in TD_REF else []
    return jsonify(rsp.__dict__)
