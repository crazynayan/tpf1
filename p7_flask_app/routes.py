from functools import wraps
from typing import Dict, List
from urllib.parse import unquote

from flask import Response, jsonify, request, g

from config import config
from p2_assembly.mac0_generic import LabelReference
from p2_assembly.mac2_data_macro import macros
from p2_assembly.seg6_segment import seg_collection
from p3_db.test_data import TestData
from p3_db.test_data_elements import Pnr, Tpfdf, FixedFile, PnrOutput
from p4_execution.ex5_execute import TpfServer
from p7_flask_app import tpf1_app
from p7_flask_app.auth import token_auth, User
from p7_flask_app.errors import error_response


def test_data_required(func):
    @wraps(func)
    def test_data_wrapper(test_data_id, *args, **kwargs):
        test_data: TestData = TestData.get_test_data(test_data_id)
        if not test_data:
            return error_response(404, "Test data id not found")
        kwargs[test_data_id] = test_data
        return func(test_data_id, *args, **kwargs)

    return test_data_wrapper


# role_check_required should only be used after test_data_required
def role_check_required(func):
    @wraps(func)
    def role_check_wrapper(test_data_id, *args, **kwargs):
        test_data: TestData = kwargs[test_data_id]
        if test_data.owner != g.current_user.email:
            return error_response(403, "Insufficient privileges to perform this action")
        return func(test_data_id, *args, **kwargs)

    return role_check_wrapper


@tpf1_app.route("/users/<string:doc_id>")
@token_auth.login_required
def get_user(doc_id: str) -> Response:
    user: Dict[str, str] = User.get_user(doc_id)
    if user is None:
        return error_response(404)
    return jsonify(user)


@tpf1_app.route("/test_data", methods=["POST"])
@token_auth.login_required
def create_test_data() -> Response:
    test_data: dict = request.get_json()
    test_data: TestData = TestData.create_test_data(test_data)
    if not test_data:
        return error_response(400, "Invalid format of test data. Need unique name and seg_name only.")
    return jsonify(test_data.cascade_to_dict())


@tpf1_app.route("/test_data")
@token_auth.login_required
def get_test_data_header() -> Response:
    name: str = request.args.get("name")
    if name is not None:
        name = unquote(name)
        test_data: TestData = TestData.get_test_data_by_name(name)
        if not test_data:
            return error_response(404, f"No test data found by this name")
        return jsonify([test_data.get_header_dict()])
    test_data_list = [test_data.get_header_dict() for test_data in TestData.get_all()]
    return jsonify(test_data_list)


@tpf1_app.route("/test_data/<string:test_data_id>/rename", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def rename_test_data(test_data_id: str, **kwargs) -> Response:
    header: dict = request.get_json()
    test_data: TestData = kwargs[test_data_id]
    if not test_data.rename(header):
        return error_response(400, "Error in renaming test data")
    return jsonify(test_data.get_header_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/copy", methods=["POST"])
@token_auth.login_required
@test_data_required
def copy_test_data(test_data_id: str, **kwargs) -> Response:
    new_test_data: TestData = kwargs[test_data_id].copy()
    if not new_test_data:
        return error_response(400, "Error in copying test data")
    new_test_data.owner = g.current_user.email
    new_test_data.save()
    return jsonify(new_test_data.get_header_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/run")
@token_auth.login_required
@test_data_required
def run_test_data(test_data_id: str, **kwargs) -> Response:
    test_data: TestData = kwargs[test_data_id]
    if not seg_collection.is_seg_present(test_data.seg_name):
        return error_response(400, "Error in segment name")
    tpf_server = TpfServer()
    test_data = tpf_server.run(test_data.seg_name, test_data)
    return jsonify(test_data.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>")
@token_auth.login_required
@test_data_required
def get_test_data(test_data_id: str, **kwargs) -> Response:
    test_data: TestData = kwargs[test_data_id]
    return jsonify(test_data.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_test_data(test_data_id: str, **_) -> Response:
    test_data_id: str = TestData.delete_test_data(test_data_id)
    if not test_data_id:
        return error_response(404, "Test data id not found")
    return jsonify({"test_data_id": test_data_id})


@tpf1_app.route("/test_data/<string:test_data_id>/output/regs", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_output_regs(test_data_id: str, **kwargs) -> Response:
    test_data: TestData = kwargs[test_data_id]
    reg_dict: dict = request.get_json()
    if not test_data.output.create_regs(reg_dict):
        return error_response(400, "Invalid format of Registers")
    return jsonify({"test_data_id": test_data_id})


@tpf1_app.route("/test_data/<string:test_data_id>/output/cores/<string:macro_name>/fields", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_output_field(test_data_id: str, macro_name: str, **kwargs) -> Response:
    field_byte_dict: dict = request.get_json()
    field_byte: dict = kwargs[test_data_id].output.create_field_byte(macro_name, field_byte_dict)
    if not field_byte:
        return error_response(400, "Error in adding field")
    return jsonify(field_byte)


@tpf1_app.route("/test_data/<string:test_data_id>/output/cores/<string:macro_name>/fields/<string:field_name>",
                methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_output_field(test_data_id: str, macro_name: str, field_name: str, **kwargs) -> Response:
    field_byte: dict = kwargs[test_data_id].output.delete_field_byte(macro_name, unquote(field_name))
    if not field_byte:
        return error_response(400, "Error in deleting field")
    return jsonify(field_byte)


@tpf1_app.route("/test_data/<string:test_data_id>/input/cores/<string:macro_name>/fields", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_input_field(test_data_id: str, macro_name: str, **kwargs) -> Response:
    field_byte_dict: dict = request.get_json()
    field_byte: dict = kwargs[test_data_id].create_field_byte(macro_name, field_byte_dict)
    if not field_byte:
        return error_response(400, "Error in adding field")
    return jsonify(field_byte)


@tpf1_app.route("/test_data/<string:test_data_id>/input/cores/<string:macro_name>/fields/<string:field_name>",
                methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_input_field(test_data_id: str, macro_name: str, field_name: str, **kwargs) -> Response:
    field_byte: dict = kwargs[test_data_id].delete_field_byte(macro_name, unquote(field_name))
    if not field_byte:
        return error_response(400, "Error in deleting field")
    return jsonify(field_byte)


@tpf1_app.route("/test_data/<string:test_data_id>/input/macro", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_input_macro(test_data_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].create_macro(request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/macro/<string:macro_name>/variations/<int:variation>",
                methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def update_input_macro(test_data_id: str, macro_name: str, variation: int, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].update_macro(macro_name, variation, request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/macro/<string:macro_name>/variations/<int:variation>",
                methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_input_macro(test_data_id: str, macro_name: str, variation: int, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].delete_macro(macro_name, variation))


@tpf1_app.route("/test_data/<string:test_data_id>/input/heap", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_input_heap(test_data_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].create_heap(request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/heap/<string:heap_name>/variations/<int:variation>",
                methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def update_input_heap(test_data_id: str, heap_name: str, variation: int, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].update_heap(heap_name, variation, request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/heap/<string:heap_name>/variations/<int:variation>",
                methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_input_heap(test_data_id: str, heap_name: str, variation: int, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].delete_heap(heap_name, variation))


@tpf1_app.route("/test_data/<string:test_data_id>/input/ecb_level", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_input_ecb_level(test_data_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].create_ecb_level(request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/ecb_level/<string:ecb_level>/variations/<int:variation>",
                methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def update_input_ecb_level(test_data_id: str, ecb_level: str, variation: int, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].update_ecb_level(ecb_level, variation, request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/ecb_level/<string:ecb_level>/variations/<int:variation>",
                methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_input_ecb_level(test_data_id: str, ecb_level: str, variation: int, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].delete_ecb_level(ecb_level, variation))


@tpf1_app.route("/test_data/<string:test_data_id>/input/regs", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_input_regs(test_data_id: str, **kwargs) -> Response:
    if not kwargs[test_data_id].add_reg(request.get_json()):
        return error_response(400, "Invalid format of input Register")
    return jsonify({"test_data_id": test_data_id})


@tpf1_app.route("/test_data/<string:test_data_id>/input/regs/<string:reg>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_input_regs(test_data_id: str, reg: str, **kwargs) -> Response:
    if not kwargs[test_data_id].delete_reg(reg):
        return error_response(400, "Invalid Register")
    return jsonify({"test_data_id": test_data_id})


@tpf1_app.route("/test_data/<string:test_data_id>/input/pnr", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_input_pnr(test_data_id: str, **kwargs) -> Response:
    pnr: Pnr = kwargs[test_data_id].create_pnr_element(request.get_json())
    if not pnr:
        return error_response(400, "Error in adding PNR element")
    return jsonify(pnr.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/output/pnr", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_pnr_output(test_data_id: str, **kwargs) -> Response:
    pnr: PnrOutput = kwargs[test_data_id].create_pnr_output(request.get_json())
    if not pnr:
        return error_response(400, "Error in adding PNR Output")
    return jsonify(pnr.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/output/pnr/<string:pnr_output_id>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_pnr_output(test_data_id: str, pnr_output_id: str, **kwargs) -> Response:
    pnr: PnrOutput = kwargs[test_data_id].delete_pnr_output(pnr_output_id)
    if not pnr:
        return error_response(400, "Error in deleting PNR")
    return jsonify(pnr.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/input/pnr/<string:pnr_id>/fields", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_pnr_fields(test_data_id: str, pnr_id: str, **kwargs) -> Response:
    pnr: Pnr = kwargs[test_data_id].create_pnr_field_data(pnr_id, request.get_json())
    if not pnr:
        return error_response(400, "Error in adding PNR field")
    return jsonify(pnr.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/input/pnr/<string:pnr_id>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_pnr_element(test_data_id: str, pnr_id: str, **kwargs) -> Response:
    pnr: Pnr = kwargs[test_data_id].delete_pnr_element(pnr_id)
    if not pnr:
        return error_response(400, "Error in deleting PNR")
    return jsonify(pnr.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/input/tpfdf", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_tpfdf_lrec(test_data_id: str, **kwargs) -> Response:
    df: Tpfdf = kwargs[test_data_id].create_tpfdf_lrec(request.get_json())
    if not df:
        return error_response(400, "Error in adding Tpfdf lrec")
    return jsonify(df.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/input/tpfdf/<string:df_id>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_tpfdf_lrec(test_data_id: str, df_id: str, **kwargs) -> Response:
    df: Tpfdf = kwargs[test_data_id].delete_tpfdf_lrec(df_id)
    if not df:
        return error_response(400, "Error in deleting Tpfdf lrec")
    return jsonify(df.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/input/fixed_files", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_fixed_file(test_data_id: str, **kwargs) -> Response:
    file: FixedFile = kwargs[test_data_id].create_fixed_file(request.get_json())
    if not file:
        return error_response(400, "Error in adding Fixed File")
    return jsonify(file.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/input/fixed_files/<string:file_id>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_fixed_file(test_data_id: str, file_id: str, **kwargs) -> Response:
    file: FixedFile = kwargs[test_data_id].delete_fixed_file(file_id)
    if not file:
        return error_response(400, "Error in deleting Fixed File")
    return jsonify(file.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/output/debug", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_debug(test_data_id: str, **kwargs) -> Response:
    if not kwargs[test_data_id].output.add_debug_seg(request.get_json()):
        return error_response(400, "Error in adding debug segments")
    return jsonify(kwargs[test_data_id].cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/output/debug/<string:seg_name>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_debug(test_data_id: str, seg_name: str, **kwargs) -> Response:
    if not kwargs[test_data_id].output.delete_debug_seg(seg_name):
        return error_response(400, "Error in deleting debug segment")
    return jsonify(kwargs[test_data_id].cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/variations")
@token_auth.login_required
@test_data_required
def get_variations(test_data_id: str, **kwargs) -> Response:
    variation_types = {"core": kwargs[test_data_id].cores, "pnr": kwargs[test_data_id].pnr,
                       "tpfdf": kwargs[test_data_id].tpfdf, "file": kwargs[test_data_id].fixed_files}
    variation = request.args.get("type")
    if variation not in variation_types:
        return error_response(400, "Invalid variation type")
    variation_list = [{"variation": item.variation, "variation_name": item.variation_name}
                      for item in variation_types[variation]]
    variation_list = list({frozenset(item.items()): item for item in variation_list}.values())
    variation_list.sort(key=lambda item: item["variation"])
    return jsonify({"type": variation, "variations": variation_list})


@tpf1_app.route("/fields/<string:field_name>")
@token_auth.login_required
def find_field(field_name: str) -> Response:
    if not field_name:
        return error_response(400, "Field name cannot be empty")
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
        return error_response(404, "Field name not found")
    return jsonify(label_ref.to_dict())


@tpf1_app.route("/segments")
@token_auth.login_required
def segment_list() -> Response:
    segments: dict = seg_collection.get_all_segments()
    attributes: Dict[dict] = dict()
    for name, segment in segments.items():
        attribute = dict()
        attributes[name] = attribute
        attribute["source"] = segment.source
        attribute["filename"] = segment.file_name
        attribute["file_type"] = segment.file_type
        attribute["blob_name"] = segment.blob_name
    response_dict: Dict[str, List[str]] = {"segments": list(sorted(segments)), "attributes": attributes}
    return jsonify(response_dict)


@tpf1_app.route("/segments/upload", methods=["POST"])
@token_auth.login_required
def segment_upload() -> Response:
    response = {
        "error": True,
        "message": str(),
        "warning": str()
    }
    payload = request.get_json()
    blob_name = payload["blob_name"] if "blob_name" in payload else str()
    if not blob_name:
        response["message"] = "No filename specified."
        return jsonify(response)
    blob_name = blob_name.lower()
    # noinspection PyPackageRequirements
    from google.cloud.storage import Client
    blob = Client().bucket(config.BUCKET).blob(blob_name)
    if not blob.exists():
        response["message"] = "File does NOT exists in cloud storage."
        return jsonify(response)
    if blob_name[-4:] != ".lst":
        response["message"] = "Filenames should always end with lst."
        blob.delete()
        return jsonify(response)
    seg_name = blob_name[:4].upper()
    if seg_collection.is_seg_local(seg_name):
        response["message"] = "Cannot upload segments which are present in local."
        blob.delete()
        return jsonify(response)
    blobs = Client().list_blobs(config.BUCKET)
    duplicate_blobs = [blob for blob in blobs if blob.name != blob_name and blob.name[:4].upper() == seg_name]
    if duplicate_blobs:
        duplicate_names = ", ".join([blob.name for blob in duplicate_blobs])
        for blob in duplicate_blobs:
            blob.delete()
        response["warning"] = f"Earlier file with the same segment name ({duplicate_names}) deleted."
    seg_collection.init_from_cloud(blob_name)
    response["error"] = False
    response["message"] = "Segment successfully added."
    return jsonify(response)


@tpf1_app.route("/segments/<string:seg_name>/instructions")
@token_auth.login_required
def segment_instruction(seg_name: str) -> Response:
    response = {
        "seg_name": seg_name,
        "error": True,
        "message": str(),
        "instructions": list(),
        "not_supported": list()
    }
    if not seg_collection.is_seg_present(seg_name):
        response["message"] = f"{seg_name} segment not found."
        return jsonify(response)
    segment = seg_collection.get_seg(seg_name)
    segment.assemble()
    if segment.error_constant:
        response["message"] = f"Error in assembling constant at {segment.error_constant}."
        return jsonify(response)
    elif segment.error_line:
        response["message"] = f"Error in assembling line: {segment.error_line}."
        return jsonify(response)
    response["constants"]: List[dict] = [{"label": dc.label, "length": dc.length, "dsp": f"{dc.start:03X}",
                                          "data": (dc.data * dc.duplication_factor).hex().upper(), } for dc in
                                         segment.dc_list]
    response["literals"]: List[dict] = [{"label": dc.label, "length": dc.length, "dsp": f"{dc.start:03X}",
                                         "data": (dc.data * dc.duplication_factor).hex().upper(), } for dc in
                                        segment.literal_list]
    response["instructions"]: List[str] = [str(node) for _, node in segment.nodes.items()]
    response["instructions"].sort()
    response["not_supported"]: List[str] = [str(node) for _, node in segment.nodes.items()
                                            if node.command not in TpfServer().supported_commands]
    response["error"] = False
    return jsonify(response)


@tpf1_app.route("/macros")
@token_auth.login_required
def macro_list() -> Response:
    mac_list: List[str] = sorted(list(macros))
    response_dict: Dict[str, List[str]] = {"macros": mac_list}
    return jsonify(response_dict)


@tpf1_app.route("/macros/<string:macro_name>/symbol_table")
@token_auth.login_required
def macro_symbol_table(macro_name: str) -> Response:
    if macro_name not in macros:
        return error_response(404, "Macro not found")
    macros[macro_name].load()
    symbol_table = [label_ref.to_dict() for _, label_ref in macros[macro_name].all_labels.items()
                    if label_ref.name == macro_name]
    response_dict = {"macro_name": macro_name, "symbol_table": symbol_table}
    return jsonify(response_dict)
