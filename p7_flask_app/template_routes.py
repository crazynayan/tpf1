from urllib.parse import unquote

from flask import jsonify, request

from p3_db.template import create_new_pnr_template, add_to_existing_pnr_template, get_templates_by_type, \
    get_templates_by_name, rename_template, update_pnr_template, delete_template_by_id, delete_template_by_name, \
    get_templates_by_id
from p3_db.template_models import PNR
from p7_flask_app import tpf1_app
from p7_flask_app.auth import token_auth


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


@tpf1_app.route("/templates/pnr/update", methods=["POST"])
@token_auth.login_required
def templates_pnr_update():
    return jsonify(update_pnr_template(request.get_json()))


@tpf1_app.route("/templates/<string:template_id>", methods=["DELETE"])
@token_auth.login_required
def templates_delete(template_id: str):
    return jsonify(delete_template_by_id(template_id))


@tpf1_app.route("/templates/name/delete", methods=["POST"])
@token_auth.login_required
def templates_name_delete():
    return jsonify(delete_template_by_name(request.get_json()))
