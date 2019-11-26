from typing import Dict, List
from urllib.parse import unquote

from flask import Response, jsonify, request

from assembly.mac2_data_macro import macros
from assembly.seg6_segment import segments
from execution.ex5_execute import Execute
from firestore.auth import User
from firestore.test_data import TestData
from flask_app import tpf1_app
from flask_app.auth import token_auth
from flask_app.errors import error_response


@tpf1_app.route('/users/<string:doc_id>')
@token_auth.login_required
def get_user(doc_id: str) -> Response:
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
    if 'name' not in test_data or not test_data['name']:
        return error_response(400, 'Name is required for the test data')
    if 'seg_name' not in test_data or not test_data['seg_name']:
        return error_response(400, 'Seg Name is required for the test data')
    if TestData.name_exists(test_data['name']):
        return error_response(400, 'Name of the test data should be unique')
    if test_data['seg_name'] not in segments:
        return error_response(400, 'Segment is not present')
    test_data_id = TestData.create_test_data(test_data)
    response_dict = dict()
    response_dict['test_data_id'] = test_data_id
    return jsonify(response_dict)


@tpf1_app.route('/test_data')
@token_auth.login_required
def get_test_data_header() -> Response:
    name = request.args.get('name')
    if name:
        name = unquote(name)
        test_data = TestData.get_test_data_by_name(name)
        if not test_data:
            return error_response(404, f'No test data found by this name - {name}')
        return jsonify(test_data.get_header_dict())
    test_data_list = [test_data.get_header_dict() for test_data in TestData.get_all()]
    return jsonify(test_data_list)


@tpf1_app.route('/test_data/<string:test_data_id>/run')
@token_auth.login_required
def run_test_data(test_data_id: str) -> Response:
    test_data: TestData = TestData.get_test_data(test_data_id)
    if not test_data:
        return error_response(404, 'Test data id not found')
    if test_data.seg_name not in segments:
        return error_response(400, 'Segment not present - Test Data might be corrupted')
    tpf_server = Execute()
    tpf_server.run(test_data.seg_name, test_data)
    return jsonify(test_data.get_output_dict())


@tpf1_app.route('/test_data/<string:test_data_id>')
@token_auth.login_required
def get_test_data(test_data_id: str) -> Response:
    test_data: dict = TestData.get_test_data_dict(test_data_id)
    if not test_data:
        return error_response(404, 'Test data id not found')
    return jsonify(test_data)


@tpf1_app.route('/test_data/<string:test_data_id>', methods=['DELETE'])
@token_auth.login_required
def delete_test_data(test_data_id: str) -> Response:
    test_data_id: str = TestData.delete_test_data(test_data_id)
    if not test_data_id:
        return error_response(404, 'Test data id not found')
    response_dict = dict()
    response_dict['test_data_id'] = test_data_id
    return jsonify(response_dict)


@tpf1_app.route('/segments')
@token_auth.login_required
def segment_list() -> Response:
    seg_list: List[str] = sorted(list(segments))
    response_dict: Dict[str, List[str]] = {'segments': seg_list}
    return jsonify(response_dict)


@tpf1_app.route('/segments/<string:seg_name>/instructions')
@token_auth.login_required
def segment_instruction(seg_name: str) -> Response:
    if seg_name not in segments:
        return error_response(404, 'Segment not found')
    segments[seg_name].assemble()
    instructions: List[str] = [str(node) for _, node in segments[seg_name].nodes.items()]
    instructions.sort()
    response_dict = {'seg_name': seg_name, 'instructions': instructions}
    return jsonify(response_dict)


@tpf1_app.route('/macros')
@token_auth.login_required
def macro_list() -> Response:
    mac_list: List[str] = sorted(list(macros))
    response_dict: Dict[str, List[str]] = {'macros': mac_list}
    return jsonify(response_dict)


@tpf1_app.route('/macros/<string:macro_name>/symbol_table')
@token_auth.login_required
def macro_symbol_table(macro_name: str) -> Response:
    if macro_name not in macros:
        return error_response(404, 'Macro not found')
    macros[macro_name].load()
    symbol_table = [label_ref.to_dict() for _, label_ref in macros[macro_name].all_labels.items()
                    if label_ref.name == macro_name]
    response_dict = {'macro_name': macro_name, 'symbol_table': symbol_table}
    return jsonify(response_dict)


@tpf1_app.route('/fields/<string:field_name>')
@token_auth.login_required
def find_field(field_name: str) -> Response:
    if not field_name:
        return error_response(400, 'Field name cannot be empty')
    field_name = field_name.upper()
    label_ref = None
    for _, data_macro in macros.items():
        data_macro.load()
        if data_macro.check(field_name):
            label_ref = data_macro.lookup(field_name)
            break
    if label_ref is None:
        return error_response(404, 'Field name not found')
    return jsonify(label_ref.to_dict())
