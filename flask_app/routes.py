from typing import Dict

from flask import Response, jsonify, request

from firestore.auth import User
from firestore.test_data import TestData
from flask_app import tpf1_app
from flask_app.auth import token_auth
from flask_app.errors import error_response


@tpf1_app.route('/users/<string:doc_id>', methods=['GET'])
@token_auth.login_required
def get_user(doc_id) -> Response:
    user: Dict[str, str] = User.get_user(doc_id)
    if user is None:
        return error_response(404)
    return jsonify(user)


@tpf1_app.route('/test_data', methods=['POST'])
@token_auth.login_required
def create_test_data() -> Response:
    test_data: dict = request.get_json()
    if not test_data:
        return error_response(400, 'Test data is empty')
    test_data_id = TestData.create_test_data(test_data)
    response_dict = dict()
    response_dict['test_data_id'] = test_data_id
    return jsonify(response_dict)


@tpf1_app.route('/test_data/<string:test_data_id>', methods=['GET'])
@token_auth.login_required
def get_test_data(test_data_id) -> Response:
    test_data: dict = TestData.get_test_data(test_data_id)
    if not test_data:
        return error_response(404, 'Test data id not found')
    return jsonify(test_data)


@tpf1_app.route('/test_data/<string:test_data_id>', methods=['DELETE'])
@token_auth.login_required
def delete_test_data(test_data_id) -> Response:
    test_data_id: str = TestData.delete_test_data(test_data_id)
    if not test_data_id:
        return error_response(404, 'Test data id not found')
    response_dict = dict()
    response_dict['test_data_id'] = test_data_id
    return jsonify(response_dict)
