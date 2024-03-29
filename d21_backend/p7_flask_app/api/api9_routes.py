from typing import List
from urllib.parse import unquote

from flask import Response, request, jsonify

from d21_backend.p7_flask_app.api import bp
from d21_backend.p7_flask_app.api.api0_constants import TEST_DATA, SuccessMsg, ErrorMsg, Types
from d21_backend.p7_flask_app.api.api1_models import TestData
from d21_backend.p7_flask_app.api.api8_process_test_data import process_test_data
from d21_backend.p7_flask_app.auth import token_auth


@bp.route("/test_data", methods=["POST"])
@token_auth.login_required
def post_test_data() -> Response:
    status, payload = process_test_data(request.get_json())
    response: Response = jsonify(payload)
    response.status_code = status
    return response


@bp.route("/test_data", methods=["DELETE"])
@token_auth.login_required
def delete_test_data() -> Response:
    name = request.args.get("name")
    if not name:
        response: Response = jsonify({TEST_DATA: ErrorMsg.NOT_FOUND})
        response.status_code = 404
        return response
    success: str = TestData.objects.filter_by(name=unquote(name)).delete()
    if not success:
        response: Response = jsonify({TEST_DATA: ErrorMsg.NOT_FOUND})
        response.status_code = 404
        return response
    response: Response = jsonify({TEST_DATA: SuccessMsg.DELETE})
    response.status_code = 200
    return response


@bp.route("/test_data")
@token_auth.login_required
def get_test_data() -> Response:
    name = request.args.get("name")
    if name is None:
        test_data: List[dict] = TestData.objects.no_orm.filter_by(type=Types.INPUT_HEADER).get()
        test_data.sort(key=lambda element: element["name"])
        return jsonify(test_data)
    test_data: List[dict] = TestData.objects.no_orm.filter_by(name=unquote(name)).get()
    return jsonify(test_data)
