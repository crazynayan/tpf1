from urllib.parse import unquote

from flask import Response, request, jsonify

from flask_app.api import bp
from flask_app.api.constants import TEST_DATA, SuccessMsg, ErrorMsg
from flask_app.api.test_data import TestData
from flask_app.auth import token_auth


@bp.route("/test_data", methods=["POST"])
@token_auth.login_required
def create_test_data() -> Response:
    status, payload = TestData.create_test_data(request.get_json())
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
