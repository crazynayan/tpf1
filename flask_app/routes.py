from typing import Dict

from flask import Response, jsonify

from firestore.auth import get_user_dict_by_id
from flask_app import tpf1_app
from flask_app.auth import token_auth
from flask_app.errors import error_response


@tpf1_app.route('/users/<string:doc_id>', methods=['GET'])
@token_auth.login_required
def get_user(doc_id) -> Response:
    user: Dict[str, str] = get_user_dict_by_id(doc_id)  # TODO remove this test and also its method
    if user is None:
        return error_response(404)
    return jsonify(user)
