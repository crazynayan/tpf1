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


@tpf1_app.route('/test_data/<string:test_data_id>/output/cores', methods=['POST'])
@token_auth.login_required
def add_output_core(test_data_id: str) -> Response:
    test_data: TestData = TestData.get_test_data(test_data_id)
    if not test_data:
        return error_response(404, 'Test data id not found')
    core_dict = request.get_json()
    if 'macro_name' not in core_dict or not core_dict['macro_name']:
        return error_response(400, 'Attribute macro_name not present or empty')
    base_reg = core_dict['base_reg'] if 'base_reg' in core_dict else str()
    core = test_data.output.create_core(core_dict['macro_name'], base_reg)
    if not core:
        return error_response(404, 'Macro does not exists in the tool')
    return jsonify({'core_id': core.id})


@tpf1_app.route('/test_data/<string:test_data_id>/output/cores/<string:macro_name>/fields', methods=['POST'])
@token_auth.login_required
def add_output_field(test_data_id: str, macro_name: str) -> Response:
    field_byte_dict: dict = request.get_json()
    if 'field' not in field_byte_dict or not field_byte_dict['field']:
        return error_response(400, 'Attribute field not present or empty')
    test_data: TestData = TestData.get_test_data(test_data_id)
    if not test_data:
        return error_response(404, 'Test data id not found')
    core = next((core for core in test_data.output.cores if core.macro_name == macro_name), None)
    if not core:
        return error_response(400, 'Macro does not exist in test data')
    field_byte = next((field_byte for field_byte in core.field_bytes if field_byte.field == field_byte_dict['field']),
                      None)
    if not field_byte:
        field_byte = core.create_field_byte(field_byte_dict['field'])
    if macro_name not in macros:
        return error_response(404, 'Macro does not exists in the tool')
    macros[macro_name].load()
    if not macros[macro_name].check(field_byte_dict['field']):
        return error_response(400, 'Field name not present in macro')
    field_byte.length = field_byte_dict['length'] if 'length' in field_byte_dict and field_byte_dict['length'] \
        else macros[macro_name].evaluate(f"L'{field_byte_dict['field']}")
    field_byte.save()
    return jsonify({'field_byte_id': field_byte.id})


@tpf1_app.route('/test_data/<string:test_data_id>/output/cores/<string:macro_name>/fields/<string:field_name>',
                methods=['DELETE'])
@token_auth.login_required
def delete_output_field(test_data_id: str, macro_name: str, field_name: str) -> Response:
    field_name = unquote(field_name)
    test_data: TestData = TestData.get_test_data(test_data_id)
    if not test_data:
        return error_response(404, 'Test data id not found')
    core = next((core for core in test_data.output.cores if core.macro_name == macro_name), None)
    if not core:
        return error_response(404, 'Core not found with this macro name')
    field_byte_id = core.delete_field_byte(field_name)
    if not field_byte_id:
        return error_response(404, 'Field not found with this field name')
    if not core.field_bytes:
        test_data.output.delete_core(macro_name)
    return jsonify({'field_byte_id': field_byte_id})


@tpf1_app.route('/test_data/<string:test_data_id>/output/regs', methods=['POST'])
@token_auth.login_required
def add_output_regs(test_data_id: str) -> Response:
    test_data: TestData = TestData.get_test_data(test_data_id)
    if not test_data:
        return error_response(404, 'Test data id not found')
    reg_dict = request.get_json()
    if 'regs' not in reg_dict:
        return error_response(400, 'Attribute regs not present')
    if not test_data.output.create_regs(reg_dict['regs']):
        return error_response(400, 'Invalid format of Registers')
    return jsonify({'test_data_id': test_data_id})


@tpf1_app.route('/test_data/<string:test_data_id>/output/regs', methods=['DELETE'])
@token_auth.login_required
def delete_output_regs(test_data_id: str) -> Response:
    test_data: TestData = TestData.get_test_data(test_data_id)
    if not test_data:
        return error_response(404, 'Test data id not found')
    test_data.output.delete_regs()
    return jsonify({'test_data_id': test_data_id})


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
