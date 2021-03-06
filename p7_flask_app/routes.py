from functools import wraps
from typing import Dict, List
from urllib.parse import unquote

from flask import Response, jsonify, request

from p2_assembly.mac0_generic import LabelReference
from p2_assembly.mac2_data_macro import macros
from p2_assembly.seg6_segment import segments
from p3_db.test_data import TestData
from p3_db.test_data_elements import Pnr, Tpfdf, FixedFile
from p4_execution.ex5_execute import TpfServer
from p7_flask_app import tpf1_app
from p7_flask_app.auth import token_auth, User
from p7_flask_app.errors import error_response


def test_data_required(func):
    @wraps(func)
    def test_data_wrapper(test_data_id, *args, **kwargs):
        test_data: TestData = TestData.get_test_data(test_data_id)
        if not test_data:
            return error_response(404, 'Test data id not found')
        kwargs[test_data_id] = test_data
        return func(test_data_id, *args, **kwargs)

    return test_data_wrapper


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
    test_data: TestData = TestData.create_test_data(test_data)
    if not test_data:
        return error_response(400, 'Invalid format of test data. Need unique name and seg_name only.')
    return jsonify(test_data.cascade_to_dict())


@tpf1_app.route('/test_data')
@token_auth.login_required
def get_test_data_header() -> Response:
    name: str = request.args.get('name')
    if name is not None:
        name = unquote(name)
        test_data: TestData = TestData.get_test_data_by_name(name)
        if not test_data:
            return error_response(404, f'No test data found by this name')
        return jsonify([test_data.get_header_dict()])
    test_data_list = [test_data.get_header_dict() for test_data in TestData.get_all()]
    return jsonify(test_data_list)


@tpf1_app.route('/test_data/<string:test_data_id>/rename', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def rename_test_data(test_data_id: str, **kwargs) -> Response:
    header: dict = request.get_json()
    test_data: TestData = kwargs[test_data_id]
    if not test_data.rename(header):
        return error_response(400, 'Error in renaming test data')
    return jsonify(test_data.get_header_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/copy', methods=['POST'])
@token_auth.login_required
@test_data_required
def copy_test_data(test_data_id: str, **kwargs) -> Response:
    new_test_data: TestData = kwargs[test_data_id].copy()
    if not new_test_data:
        return error_response(400, 'Error in copying test data')
    return jsonify(new_test_data.get_header_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/run')
@token_auth.login_required
@test_data_required
def run_test_data(test_data_id: str, **kwargs) -> Response:
    test_data: TestData = kwargs[test_data_id]
    if test_data.seg_name not in segments:
        return error_response(400, 'Error in segment name')
    tpf_server = TpfServer()
    test_data = tpf_server.run(test_data.seg_name, test_data)
    return jsonify(test_data.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>')
@token_auth.login_required
@test_data_required
def get_test_data(test_data_id: str, **kwargs) -> Response:
    test_data: TestData = kwargs[test_data_id]
    return jsonify(test_data.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>', methods=['DELETE'])
@token_auth.login_required
def delete_test_data(test_data_id: str) -> Response:
    test_data_id: str = TestData.delete_test_data(test_data_id)
    if not test_data_id:
        return error_response(404, 'Test data id not found')
    return jsonify({'test_data_id': test_data_id})


@tpf1_app.route('/test_data/<string:test_data_id>/output/regs', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_output_regs(test_data_id: str, **kwargs) -> Response:
    test_data: TestData = kwargs[test_data_id]
    reg_dict: dict = request.get_json()
    if not test_data.output.create_regs(reg_dict):
        return error_response(400, 'Invalid format of Registers')
    return jsonify({'test_data_id': test_data_id})


@tpf1_app.route('/test_data/<string:test_data_id>/output/cores/<string:macro_name>/fields', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_output_field(test_data_id: str, macro_name: str, **kwargs) -> Response:
    field_byte_dict: dict = request.get_json()
    field_byte: dict = kwargs[test_data_id].output.create_field_byte(macro_name, field_byte_dict)
    if not field_byte:
        return error_response(400, 'Error in adding field')
    return jsonify(field_byte)


@tpf1_app.route('/test_data/<string:test_data_id>/output/cores/<string:macro_name>/fields/<string:field_name>',
                methods=['DELETE'])
@token_auth.login_required
@test_data_required
def delete_output_field(test_data_id: str, macro_name: str, field_name: str, **kwargs) -> Response:
    field_byte: dict = kwargs[test_data_id].output.delete_field_byte(macro_name, unquote(field_name))
    if not field_byte:
        return error_response(400, 'Error in deleting field')
    return jsonify(field_byte)


@tpf1_app.route('/test_data/<string:test_data_id>/input/cores/<string:macro_name>/fields', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_input_field(test_data_id: str, macro_name: str, **kwargs) -> Response:
    field_byte_dict: dict = request.get_json()
    field_byte: dict = kwargs[test_data_id].create_field_byte(macro_name, field_byte_dict)
    if not field_byte:
        return error_response(400, 'Error in adding field')
    return jsonify(field_byte)


@tpf1_app.route('/test_data/<string:test_data_id>/input/cores/<string:macro_name>/fields/<string:field_name>',
                methods=['DELETE'])
@token_auth.login_required
@test_data_required
def delete_input_field(test_data_id: str, macro_name: str, field_name: str, **kwargs) -> Response:
    field_byte: dict = kwargs[test_data_id].delete_field_byte(macro_name, unquote(field_name))
    if not field_byte:
        return error_response(400, 'Error in deleting field')
    return jsonify(field_byte)


@tpf1_app.route('/test_data/<string:test_data_id>/input/regs', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_input_regs(test_data_id: str, **kwargs) -> Response:
    if not kwargs[test_data_id].add_reg(request.get_json()):
        return error_response(400, 'Invalid format of input Register')
    return jsonify({'test_data_id': test_data_id})


@tpf1_app.route('/test_data/<string:test_data_id>/input/regs/<string:reg>', methods=['DELETE'])
@token_auth.login_required
@test_data_required
def delete_input_regs(test_data_id: str, reg: str, **kwargs) -> Response:
    if not kwargs[test_data_id].delete_reg(reg):
        return error_response(400, 'Invalid Register')
    return jsonify({'test_data_id': test_data_id})


@tpf1_app.route('/test_data/<string:test_data_id>/input/pnr', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_input_pnr(test_data_id: str, **kwargs) -> Response:
    pnr: Pnr = kwargs[test_data_id].create_pnr_element(request.get_json())
    if not pnr:
        return error_response(400, 'Error in adding PNR element')
    return jsonify(pnr.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/input/pnr/<string:pnr_id>/fields', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_pnr_fields(test_data_id: str, pnr_id: str, **kwargs) -> Response:
    pnr: Pnr = kwargs[test_data_id].create_pnr_field_data(pnr_id, request.get_json())
    if not pnr:
        return error_response(400, 'Error in adding PNR field')
    return jsonify(pnr.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/input/pnr/<string:pnr_id>', methods=['DELETE'])
@token_auth.login_required
@test_data_required
def delete_pnr_element(test_data_id: str, pnr_id: str, **kwargs) -> Response:
    pnr: Pnr = kwargs[test_data_id].delete_pnr_element(pnr_id)
    if not pnr:
        return error_response(400, 'Error in deleting PNR')
    return jsonify(pnr.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/input/tpfdf', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_tpfdf_lrec(test_data_id: str, **kwargs) -> Response:
    df: Tpfdf = kwargs[test_data_id].create_tpfdf_lrec(request.get_json())
    if not df:
        return error_response(400, 'Error in adding Tpfdf lrec')
    return jsonify(df.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/input/tpfdf/<string:df_id>', methods=['DELETE'])
@token_auth.login_required
@test_data_required
def delete_tpfdf_lrec(test_data_id: str, df_id: str, **kwargs) -> Response:
    df: Tpfdf = kwargs[test_data_id].delete_tpfdf_lrec(df_id)
    if not df:
        return error_response(400, 'Error in deleting Tpfdf lrec')
    return jsonify(df.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/input/fixed_files', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_fixed_file(test_data_id: str, **kwargs) -> Response:
    file: FixedFile = kwargs[test_data_id].create_fixed_file(request.get_json())
    if not file:
        return error_response(400, 'Error in adding Fixed File')
    return jsonify(file.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/input/fixed_files/<string:file_id>', methods=['DELETE'])
@token_auth.login_required
@test_data_required
def delete_fixed_file(test_data_id: str, file_id: str, **kwargs) -> Response:
    file: FixedFile = kwargs[test_data_id].delete_fixed_file(file_id)
    if not file:
        return error_response(400, 'Error in deleting Fixed File')
    return jsonify(file.cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/output/debug', methods=['PATCH'])
@token_auth.login_required
@test_data_required
def add_debug(test_data_id: str, **kwargs) -> Response:
    if not kwargs[test_data_id].output.add_debug_seg(request.get_json()):
        return error_response(400, 'Error in adding debug segments')
    return jsonify(kwargs[test_data_id].cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/output/debug/<string:seg_name>', methods=['DELETE'])
@token_auth.login_required
@test_data_required
def delete_debug(test_data_id: str, seg_name: str, **kwargs) -> Response:
    if not kwargs[test_data_id].output.delete_debug_seg(seg_name):
        return error_response(400, 'Error in deleting debug segment')
    return jsonify(kwargs[test_data_id].cascade_to_dict())


@tpf1_app.route('/test_data/<string:test_data_id>/variations')
@token_auth.login_required
@test_data_required
def get_variations(test_data_id: str, **kwargs) -> Response:
    variation_types = {'core': kwargs[test_data_id].cores, 'pnr': kwargs[test_data_id].pnr,
                       'tpfdf': kwargs[test_data_id].tpfdf, 'file': kwargs[test_data_id].fixed_files}
    variation = request.args.get('type')
    if variation not in variation_types:
        return error_response(400, 'Invalid variation type')
    variation_list = [{'variation': item.variation, 'variation_name': item.variation_name}
                      for item in variation_types[variation]]
    variation_list = list({frozenset(item.items()): item for item in variation_list}.values())
    variation_list.sort(key=lambda item: item['variation'])
    return jsonify({'type': variation, 'variations': variation_list})


@tpf1_app.route('/fields/<string:field_name>')
@token_auth.login_required
def find_field(field_name: str) -> Response:
    if not field_name:
        return error_response(400, 'Field name cannot be empty')
    field_name = field_name.upper()
    if field_name in macros:
        return jsonify(LabelReference(name=field_name, label=field_name, dsp=0, length=0).to_dict())
    label_ref = None
    for _, data_macro in macros.items():
        data_macro.load()
        if data_macro.check(field_name):
            label_ref = data_macro.lookup(field_name)
            break
    if label_ref is None:
        return error_response(404, 'Field name not found')
    return jsonify(label_ref.to_dict())


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
