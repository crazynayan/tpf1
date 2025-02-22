from typing import Dict, List, Optional, Union
from urllib.parse import unquote

from flask import Response, jsonify, request, g
# noinspection PyPackageRequirements
from google.cloud.storage import Client

from d21_backend.config import config
from d21_backend.p1_utils.domain import get_bucket
from d21_backend.p2_assembly.mac0_generic import LabelReference
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p2_assembly.seg9_collection import get_seg_collection, SegLst, get_seg_lst_for_domain
from d21_backend.p3_db.startup_script import test_data_create, test_data_update
from d21_backend.p3_db.test_data import TestData
from d21_backend.p3_db.test_data_elements import Tpfdf, FixedFile
from d21_backend.p3_db.test_data_variations import rename_variation, copy_variation, delete_variation
from d21_backend.p3_db.test_results_crud import update_comment, create_test_result, get_test_results, delete_test_result, \
    get_test_result
from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p7_flask_app import tpf1_app
from d21_backend.p7_flask_app.auth import token_auth, User
from d21_backend.p7_flask_app.errors import error_response
from d21_backend.p7_flask_app.route_decorators import test_data_required, role_check_required, test_data_with_links_required
from d21_backend.p7_flask_app.segment import reset_seg_assembly


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
    return jsonify(test_data_create(request.get_json()))


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
    test_data_list.sort(key=lambda item: item["name"])
    return jsonify({"test_data_list": test_data_list})


@tpf1_app.route("/test_data/<string:test_data_id>/rename", methods=["POST"])
@token_auth.login_required
@test_data_required
@role_check_required
def rename_test_data(test_data_id: str, **kwargs) -> Response:
    return jsonify(test_data_update(kwargs[test_data_id], request.get_json()))


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
@test_data_with_links_required
def run_test_data(test_data_id: str, **kwargs) -> Response:
    test_data: TestData = kwargs[test_data_id]
    if not get_seg_collection().is_seg_present(test_data.seg_name):
        return error_response(400, "Error in segment name")
    tpf_server = TpfServer()
    output_test_data = tpf_server.run(test_data.seg_name, test_data)
    final_test_data = output_test_data.cascade_to_dict()
    # Indicate which type of test data variation is present
    final_test_data["test_data_variation"] = {"core": False, "pnr": False, "tpfdf": False, "file": False}
    for variation_type in final_test_data["test_data_variation"]:
        if any(output["variation"][variation_type] != final_test_data["outputs"][0]["variation"][variation_type]
               for output in final_test_data["outputs"]):
            final_test_data["test_data_variation"][variation_type] = True
    return jsonify(final_test_data)


@tpf1_app.route("/test_data/<string:test_data_id>")
@token_auth.login_required
@test_data_with_links_required
def get_test_data(test_data_id: str, **kwargs) -> Response:
    test_data: TestData = kwargs[test_data_id]
    return jsonify(test_data.cascade_to_dict())


@tpf1_app.route("/test_data/<string:test_data_id>/save_results", methods=["POST"])
@token_auth.login_required
@test_data_with_links_required
def test_results_create(test_data_id: str, **kwargs) -> Response:
    return jsonify(create_test_result(kwargs[test_data_id], request.get_json()))


@tpf1_app.route("/test_results")
@token_auth.login_required
def test_results_get() -> Response:
    name = request.args.get("name", str())
    return jsonify(get_test_results(name))


@tpf1_app.route("/test_results/delete", methods=["DELETE"])
@token_auth.login_required
def test_results_delete() -> Response:
    name = request.args.get("name", str())
    return jsonify(delete_test_result(name))


@tpf1_app.route("/test_results/<string:test_result_id>", methods=["GET"])
@token_auth.login_required
def test_result_get_comment(test_result_id: str) -> Response:
    return jsonify(get_test_result(test_result_id))


@tpf1_app.route("/test_results/<string:test_result_id>/comment", methods=["POST"])
@token_auth.login_required
def test_result_comment(test_result_id: str) -> Response:
    return jsonify(update_comment(test_result_id, request.get_json()))


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


@tpf1_app.route("/test_data/<string:test_data_id>/input/global", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_input_global(test_data_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].create_global(request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/global/<string:core_id>", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def update_input_global(test_data_id: str, core_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].update_global(core_id, request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/core/<string:core_id>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_input_core(test_data_id: str, core_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].delete_core(core_id))


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


@tpf1_app.route("/test_data/<string:test_data_id>/output/pnr", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_pnr_output(test_data_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].create_pnr_output(request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/output/pnr/<string:pnr_output_id>", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def update_pnr_output(test_data_id: str, pnr_output_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].update_pnr_output(pnr_output_id, request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/output/pnr/<string:pnr_output_id>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_pnr_output(test_data_id: str, pnr_output_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].delete_pnr_output(pnr_output_id))


@tpf1_app.route("/test_data/<string:test_data_id>/input/pnr", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def add_pnr_input(test_data_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].create_pnr_input(request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/pnr/<string:pnr_input_id>", methods=["PATCH"])
@token_auth.login_required
@test_data_required
@role_check_required
def update_pnr_input(test_data_id: str, pnr_input_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].update_pnr_input(pnr_input_id, request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/pnr/<string:pnr_input_id>", methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_pnr_input(test_data_id: str, pnr_input_id: str, **kwargs) -> Response:
    return jsonify(kwargs[test_data_id].delete_pnr_input(pnr_input_id))


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


@tpf1_app.route("/test_data/<string:test_data_id>/input/types/<string:v_type>/variations/<int:variation>/rename",
                methods=["POST"])
@token_auth.login_required
@test_data_required
@role_check_required
def rename_variation_by_type(test_data_id: str, v_type: str, variation: int, **kwargs) -> Response:
    return jsonify(rename_variation(kwargs[test_data_id], variation, v_type, request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/types/<string:v_type>/variations/<int:variation>/copy",
                methods=["POST"])
@token_auth.login_required
@test_data_required
@role_check_required
def copy_variation_by_type(test_data_id: str, v_type: str, variation: int, **kwargs) -> Response:
    return jsonify(copy_variation(kwargs[test_data_id], variation, v_type, request.get_json()))


@tpf1_app.route("/test_data/<string:test_data_id>/input/types/<string:v_type>/variations/<int:variation>/delete",
                methods=["DELETE"])
@token_auth.login_required
@test_data_required
@role_check_required
def delete_variation_by_type(test_data_id: str, v_type: str, variation: int, **kwargs) -> Response:
    return jsonify(delete_variation(kwargs[test_data_id], variation, v_type))


@tpf1_app.route("/fields/<string:field_name>")
@token_auth.login_required
def find_field(field_name: str) -> Response:
    if not field_name:
        return error_response(400, "Field name cannot be empty")
    field_name = field_name.upper()
    macros = get_macros()
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
    seg_lst: List[SegLst] = get_seg_lst_for_domain()
    attributes: Dict[str, dict] = dict()
    for seg in seg_lst:
        attributes[seg.seg_name] = seg.doc_to_dict()
        attributes[seg.seg_name]["execution_percentage"] = seg.execution_percentage
        attributes[seg.seg_name]["assembly_error"] = seg.assembly_error
    response_dict: Dict[str, List[str]] = {"segments": [seg.seg_name for seg in seg_lst], "attributes": attributes}
    return jsonify(response_dict)


def close_jsonify(response: dict, client: Optional[Client] = None):
    if client:
        client.close()
    return jsonify(response)


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
        return close_jsonify(response)
    blob_name = blob_name.lower()
    client = Client()
    blob = client.bucket(get_bucket()).blob(blob_name)
    if not blob.exists():
        # The blob needs to be uploaded by the client before calling the server.
        # If this message is being reported then server and client are out of sync. Most likely trying to upload seg in base domain.
        response["message"] = "File does NOT exists in cloud storage."
        return close_jsonify(response, client)
    valid_extensions = {f".{config.LST}", f".{config.ASM}"}
    blob_extension = blob_name[-4:]
    if blob_extension not in valid_extensions:
        response["message"] = "Filenames should have an extension of lst or asm."
        blob.delete()
        return close_jsonify(response, client)
    seg_name = blob_name[:4].upper()
    file_type = blob_extension[-3:]
    if get_seg_collection().is_seg_local(seg_name):
        response["message"] = "Cannot upload segments which are present in local."
        blob.delete()
        return close_jsonify(response, client)
    blobs = client.list_blobs(get_bucket())
    duplicate_blobs = [blob for blob in blobs if blob.name != blob_name and blob.name[:4].upper() == seg_name]
    if duplicate_blobs:
        duplicate_names = ", ".join([blob.name for blob in duplicate_blobs])
        for blob in duplicate_blobs:
            blob.delete()
        response["warning"] = f"Earlier file with the same segment name ({duplicate_names}) deleted."
    seg: SegLst = reset_seg_assembly(blob_name, file_type)
    if seg.assembly_error:
        response["message"] = f"Segment successfully added but assembly error on the instruction {seg.assembly_error}."
    else:
        response["message"] = f"Segment successfully added. Tool can execute {seg.execution_percentage} of code."
    response["error"] = False
    return close_jsonify(response, client)


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
    segment = get_seg_collection().get_seg(seg_name)
    if not segment:
        response["message"] = f"{seg_name} segment not found."
        return jsonify(response)
    segment.assemble()
    if segment.error_constant:
        response["message"] = f"Error in assembling constant at {segment.error_constant}."
        return jsonify(response)
    elif segment.error_line:
        response["message"] = f"Error in assembling line: {segment.error_line}."
        return jsonify(response)
    response["constants"]: List[dict] = [{"label": dc.label, "length": dc.length, "dsp": f"{dc.start:03X}",
                                          "data": (dc.data * dc.duplication_factor).hex().upper()
                                          if dc.duplication_factor else str(), }
                                         for dc in segment.dc_list]
    response["literals"]: List[dict] = [{"label": dc.label, "length": dc.length, "dsp": f"{dc.start:03X}",
                                         "data": (dc.data * dc.duplication_factor).hex().upper()
                                         if dc.duplication_factor else str(), }
                                        for dc in segment.literal_list]
    response["instructions"]: List[str] = [str(node) for _, node in segment.nodes.items()]
    response["instructions"].sort()
    response["not_supported"]: List[str] = [str(node) for _, node in segment.nodes.items()
                                            if node.command not in TpfServer().supported_commands]
    response["error"] = False
    return jsonify(response)


@tpf1_app.route("/macros")
@token_auth.login_required
def macro_list() -> Response:
    mac_list: List[str] = sorted(list(get_macros()))
    response_dict: Dict[str, List[str]] = {"macros": mac_list}
    return jsonify(response_dict)


@tpf1_app.route("/macros/<string:macro_name>/symbol_table")
@token_auth.login_required
def macro_symbol_table(macro_name: str) -> Response:
    macros = get_macros()
    if macro_name not in macros:
        return error_response(404, "Macro not found")
    macros[macro_name].load()
    symbol_table = [label_ref.to_dict() for _, label_ref in macros[macro_name].all_labels.items()
                    if label_ref.name == macro_name]
    response_dict = {"macro_name": macro_name, "symbol_table": symbol_table}
    return jsonify(response_dict)


@tpf1_app.route("/unsupported_instructions")
@token_auth.login_required
def unsupported_instructions() -> Response:
    if g.current_user.role != config.ADMIN:
        return error_response(401, "Only Admins can view this list")
    seg_lst: List[SegLst] = SegLst.objects.filter("error_cmds", ">", list()).filter_by(file_type=config.LST).get()
    unsupported_commands: List[List[Union[str, List]]] = list()
    for seg in seg_lst:
        for command in seg.error_cmds:
            cmd_seg_lst: List = next((cmd_seg for cmd_seg in unsupported_commands if cmd_seg[0] == command), None)
            if not cmd_seg_lst:
                unsupported_commands.append([command, [seg.seg_name]])
                continue
            cmd_seg_lst[1].append(seg.seg_name)
    unsupported_commands.sort()
    return jsonify({"unsupported_instructions": unsupported_commands})
