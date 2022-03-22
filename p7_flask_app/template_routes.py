from urllib.parse import unquote

from flask import jsonify, request, Response

from p3_db.template_crud import create_new_pnr_template, add_to_existing_pnr_template, get_templates_by_type, \
    get_templates_by_name, rename_template, update_pnr_template, delete_template_by_id, delete_template_by_name, \
    get_templates_by_id, copy_template, create_new_global_template, add_to_existing_global_template, \
    update_global_template
from p3_db.template_merge import merge_pnr_template, create_link_pnr_template, update_link_pnr_template, \
    delete_link_pnr_template
from p3_db.template_models import PNR, GLOBAL
from p7_flask_app import tpf1_app
from p7_flask_app.auth import token_auth
from p7_flask_app.route_decorators import test_data_required, role_check_required


@tpf1_app.route("/templates/pnr/create", methods=["POST"])
@token_auth.login_required
def templates_pnr_create():
    return jsonify(create_new_pnr_template(request.get_json()))


@tpf1_app.route("/templates/pnr/add", methods=["POST"])
@token_auth.login_required
def templates_pnr_add():
    return jsonify(add_to_existing_pnr_template(request.get_json()))


@tpf1_app.route("/templates/pnr", methods=["GET"])
@token_auth.login_required
def templates_pnr_get():
    return jsonify(get_templates_by_type(PNR))


@tpf1_app.route("/templates/pnr/update", methods=["POST"])
@token_auth.login_required
def templates_pnr_update():
    return jsonify(update_pnr_template(request.get_json()))


@tpf1_app.route("/templates/global/create", methods=["POST"])
@token_auth.login_required
def templates_global_create():
    return jsonify(create_new_global_template(request.get_json()))


@tpf1_app.route("/templates/global/add", methods=["POST"])
@token_auth.login_required
def templates_global_add():
    return jsonify(add_to_existing_global_template(request.get_json()))


@tpf1_app.route("/templates/global", methods=["GET"])
@token_auth.login_required
def templates_global_get():
    return jsonify(get_templates_by_type(GLOBAL))


@tpf1_app.route("/templates/global/update", methods=["POST"])
@token_auth.login_required
def templates_global_update():
    return jsonify(update_global_template(request.get_json()))


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


@tpf1_app.route("/test_data/<string:test_data_id>/templates/pnr/merge", methods=["POST"])
@token_auth.login_required
@test_data_required
@role_check_required
def templates_pnr_merge(test_data_id: str, **kwargs) -> Response:
    return jsonify(merge_pnr_template(kwargs[test_data_id], request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/templates/pnr/link/create", methods=["POST"])
@token_auth.login_required
@test_data_required
@role_check_required
def templates_pnr_link_create(test_data_id: str, **kwargs) -> Response:
    return jsonify(create_link_pnr_template(kwargs[test_data_id], request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/templates/pnr/link/update", methods=["POST"])
@token_auth.login_required
@test_data_required
@role_check_required
def templates_pnr_link_update(test_data_id: str, **kwargs) -> Response:
    return jsonify(update_link_pnr_template(kwargs[test_data_id], request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/templates/pnr/link/delete", methods=["POST"])
@token_auth.login_required
@test_data_required
@role_check_required
def templates_pnr_link_delete(test_data_id: str, **kwargs) -> Response:
    return jsonify(delete_link_pnr_template(kwargs[test_data_id], request.get_json()))
