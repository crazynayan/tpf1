from base64 import b64decode, b64encode
from copy import deepcopy
from itertools import product
from typing import Dict, List, Optional, Union

from firestore_ci import FirestoreDocument

import p3_db.pnr as db_pnr
from config import config
from p1_utils.data_type import Register
from p1_utils.errors import InvalidBaseRegError
from p2_assembly.mac2_data_macro import macros, DataMacro
from p2_assembly.seg9_collection import seg_collection
from p3_db.test_data_elements import Core, Pnr, Tpfdf, Output, FixedFile, PnrOutput
from p3_db.test_data_validators import get_response_body_for_hex_and_field_data, create_core_for_hex_and_field_data, \
    get_response_body_for_macro, create_core


class TestData(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.owner: str = ""  # Email address of the user who created the test data
        self.seg_name: str = ""
        self.stop_segments: List[str] = list()
        self.cores: List[Core] = list()
        self.pnr: List[Pnr] = list()
        self.tpfdf: List[Tpfdf] = list()
        self.fixed_files: List[FixedFile] = list()
        self.errors: List[str] = list()
        self.outputs: List[Output] = [Output()]
        self.partition: str = str()
        self.regs: Dict[str, int] = dict()

    @property
    def output(self):
        return self.outputs[0]

    def get_field(self, field_name: str, core_variation: int = 0, pnr_variation: int = 0, tpfdf_variation: int = 0):
        output = self.get_output(core_variation, pnr_variation, tpfdf_variation)
        field_data = next(field_data for core in output.cores for field_data in core.field_data
                          if field_data["field"] == field_name)
        return b64decode(field_data["data"]).hex().upper()

    def get_pnr_field(self, field_name: str, core_variation: int = 0, pnr_variation: int = 0, tpfdf_variation: int = 0):
        output = self.get_output(core_variation, pnr_variation, tpfdf_variation)
        field_data = next(field_data for pnr_output in output.pnr_outputs for field_data in pnr_output.field_data
                          if field_data["field"] == field_name)
        return b64decode(field_data["data"]).hex().upper()

    def get_output(self, core_variation: int = 0, pnr_variation: int = 0, tpfdf_variation: int = 0) -> Output:
        return next(output for output in self.outputs if output.variation["core"] == core_variation and
                    output.variation["pnr"] == pnr_variation and output.variation["tpfdf"] == tpfdf_variation)

    def get_unsigned_value(self, reg: str) -> int:
        if reg not in self.output.regs:
            raise InvalidBaseRegError
        return self.output.regs[reg] & config.REG_MAX

    def set_field(self, field_name: str, data: Union[bytearray, bytes], variation: int = 0) -> None:
        macro_name = DataMacro.get_label_reference(field_name).name
        field_dict = {"field": field_name, "data": b64encode(data).decode(), "variation": variation,
                      "variation_name": str()}
        self.create_field_byte(macro_name, field_dict, persistence=False)

    def yield_variation(self):
        core_variation = max(core.variation for core in self.cores) if self.cores else 0
        pnr_variation = max(pnr.variation for pnr in self.pnr) if self.pnr else 0
        df_variation = max(df.variation for df in self.tpfdf) if self.tpfdf else 0
        file_variation = max(file.variation for file in self.fixed_files) if self.fixed_files else 0
        for variation in product(range(core_variation + 1), range(pnr_variation + 1), range(df_variation + 1),
                                 range(file_variation + 1)):
            test_data = deepcopy(self)
            test_data.cores = [core for core in test_data.cores if core.variation == variation[0]]
            test_data.pnr = [pnr for pnr in test_data.pnr if pnr.variation == variation[1]]
            test_data.tpfdf = [df for df in test_data.tpfdf if df.variation == variation[2]]
            test_data.fixed_files = [file for file in test_data.fixed_files if file.variation == variation[3]]
            test_data.output.variation["core"] = variation[0]
            test_data.output.variation["pnr"] = variation[1]
            test_data.output.variation["tpfdf"] = variation[2]
            test_data.output.variation["file"] = variation[3]
            if test_data.cores:
                test_data.output.variation_name["core"] = test_data.cores[0].variation_name
            if test_data.pnr:
                test_data.output.variation_name["pnr"] = test_data.pnr[0].variation_name
            if test_data.tpfdf:
                test_data.output.variation_name["tpfdf"] = test_data.tpfdf[0].variation_name
            if test_data.fixed_files:
                test_data.output.variation_name["file"] = test_data.fixed_files[0].variation_name
            yield test_data
        return

    @classmethod
    def _validate_header(cls, header: dict) -> bool:
        if not header:
            return False
        if "name" not in header or "seg_name" not in header:
            return False
        header["seg_name"] = header["seg_name"].upper()
        if not seg_collection.is_seg_present(header["seg_name"]) or not header["name"]:
            return False
        if "stop_segments" in header and any(len(segment) != 4 or not segment.isalnum()
                                             for segment in header["stop_segments"]):
            return False
        return True

    def _validate_and_update_variation(self, item_dict: dict, input_type: str) -> bool:
        variation_types: dict = {"core": self.cores, "pnr": self.pnr, "tpfdf": self.tpfdf, "file": self.fixed_files}
        if input_type not in variation_types:
            return False
        max_variation = max(item.variation for item in variation_types[input_type]) \
            if variation_types[input_type] else -1
        if item_dict["variation"] in range(max_variation + 1):
            item_dict["variation_name"] = next(item.variation_name for item in variation_types[input_type]
                                               if item.variation == item_dict["variation"])
            return True
        if item_dict["variation"] != max_variation + 1:
            return False
        return True

    @classmethod
    def create_test_data(cls, header: dict) -> Optional["TestData"]:
        if not cls._validate_header(header):
            return None
        if cls.objects.filter_by(name=header["name"]).first() is not None:
            return None
        test_data = cls.create_from_dict(header)
        return test_data

    def rename(self, header: dict) -> bool:
        if not self._validate_header(header):
            return False
        self.name = header["name"]
        self.seg_name = header["seg_name"]
        self.stop_segments = header["stop_segments"]
        return self.save()

    def copy(self) -> Optional["TestData"]:
        if self.name.endswith(config.COPY_SUFFIX):
            return None
        name_copy = f"{self.name}{config.COPY_SUFFIX}"
        if self.objects.filter_by(name=name_copy).first() is not None:
            return None
        test_data_dict = self.cascade_to_dict()
        test_data_dict["name"] = name_copy
        return self.create_from_dict(test_data_dict)

    @classmethod
    def get_all(cls) -> List["TestData"]:
        return cls.objects.order_by("name").get()

    @classmethod
    def get_test_data_by_name(cls, name: str) -> Optional["TestData"]:
        return cls.objects.filter_by(name=name).first()

    @classmethod
    def get_test_data(cls, test_data_id: str) -> "TestData":
        return cls.get_by_id(test_data_id, cascade=True)

    @classmethod
    def delete_test_data(cls, test_data_id: str) -> str:
        test_data: cls = cls.get_by_id(test_data_id, cascade=True)
        return test_data.delete(cascade=True) if test_data else str()

    def get_header_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "seg_name": self.seg_name, "owner": self.owner,
                "stop_segments": self.stop_segments}

    def create_field_byte(self, macro_name, field_dict, persistence=True) -> dict:
        if not Core.validate_field_dict(macro_name, field_dict):
            return dict()
        if set(field_dict) != {"field", "data", "variation", "variation_name"}:
            return dict()
        if not isinstance(field_dict["data"], str) or not field_dict["data"]:
            return dict()
        if not self._validate_and_update_variation(field_dict, "core"):
            return dict()
        core_dict = {"macro_name": macro_name, "variation": field_dict["variation"],
                     "variation_name": field_dict["variation_name"]}
        field_dict = field_dict.copy()
        del field_dict["variation"]
        del field_dict["variation_name"]
        core = next((core for core in self.cores if core.macro_name == core_dict["macro_name"] and
                     core.variation == core_dict["variation"]), None)
        if not core:
            core: Core = Core.create_from_dict(core_dict) if persistence else Core.dict_to_doc(core_dict)
            self.cores.append(core)
            if persistence:
                self.save()
        field_byte = core.create_field_byte(field_dict, persistence)
        return field_byte

    def delete_field_byte(self, macro_name: str, field_name: str) -> dict:
        core: Core = next((core for core in self.cores if core.macro_name == macro_name), None)
        if not core:
            return dict()
        field_byte = core.delete_field_byte(field_name)
        if not field_byte:
            return dict()
        if not core.field_data:
            self.cores.remove(core)
            self.save()
            core.delete(cascade=True)
        return field_byte

    def create_macro(self, body: dict, persistence: bool = True) -> dict:
        response: dict = {"error": True, "message": str(), "error_fields": dict()}
        if set(body) != {"macro_name", "variation", "variation_name", "field_data"}:
            response["message"] = "Only 4 fields allowed (macro_name, variation, variation_name and field_data."
            return response
        if body["macro_name"] not in config.DEFAULT_MACROS:
            response["error_fields"]["macro_name"] = f"Invalid macro. Macro can only be from " \
                                                     f"{''.join(config.DEFAULT_MACROS)}."
        if not self._validate_and_update_variation(body, "core"):
            response["error_fields"]["variation"] = "Invalid variation."
        elif "macro_name" not in response["error_fields"]:
            if any(core.variation == body["variation"] and core.macro_name == body["macro_name"]
                   for core in self.cores):
                response["error_fields"]["macro_name"] = f"Macro {body['macro_name']} already exists for " \
                                                         f"variation {body['variation']}."
        updated_response, updated_body = get_response_body_for_macro(response, body, body["macro_name"])
        if updated_response["error_fields"]:
            return updated_response
        core_to_create: Core = create_core(updated_body)
        core_to_create.macro_name = body["macro_name"].upper()
        if persistence:
            core_to_create.create()
        self.cores.append(core_to_create)
        if persistence:
            self.save()
        response["message"] = f"Core with macro {core_to_create.macro_name} created successfully."
        response["error"] = False
        return response

    def update_macro(self, macro_name: str, variation: int, body: dict, persistence: bool = True):
        response: dict = {"error": True, "message": str(), "error_fields": dict()}
        core_to_update: Core = next((core for core in self.cores if core.variation == variation and
                                     core.macro_name == macro_name), None)
        if not core_to_update:
            response["message"] = f"Macro {macro_name} not found for variation {variation}."
            return response
        if set(body) != {"field_data"}:
            response["message"] = "Only field_data allowed and it is mandatory."
            return response
        updated_response, updated_body = get_response_body_for_macro(response, body, macro_name)
        if updated_response["error_fields"]:
            return updated_response
        core_to_update.field_data = updated_body["field_data"]
        core_to_update.original_field_data = updated_body["original_field_data"]
        if persistence:
            core_to_update.save()
        response["message"] = f"Core with macro {macro_name} updated successfully."
        response["error"] = False
        return response

    def delete_macro(self, macro_name: str, variation: int, persistence: bool = True) -> dict:
        response: dict = {"error": True, "message": str()}
        core: Core = next((core for core in self.cores if core.macro_name == macro_name.upper()
                           and core.variation == variation), None)
        if not core:
            response["message"] = f"Macro {macro_name} not found for variation {variation}."
            return response
        self.cores.remove(core)
        if persistence:
            self.save()
            core.delete()
        response["message"] = f"Macro {macro_name} for variation {variation} successfully deleted."
        response["error"] = False
        return response

    def create_heap(self, body: dict, persistence: bool = True) -> dict:
        response: dict = {"error": True, "message": str(), "error_fields": dict()}
        if set(body) != {"heap_name", "hex_data", "variation", "variation_name", "field_data", "seg_name"}:
            response["message"] = "Only 6 fields allowed (heap_name, hex_data, variation, variation_name, " \
                                  "field_data and seg_name) and all are mandatory."
            return response
        if not body["heap_name"] or not isinstance(body["heap_name"], str) or not body["heap_name"].isalnum():
            response["error_fields"]["heap_name"] = "Invalid heap name. It must be an alphanumeric string."
        if not self._validate_and_update_variation(body, "core"):
            response["error_fields"]["variation"] = "Invalid variation"
        elif "heap_name" not in response["error_fields"]:
            if any(core.variation == body["variation"] and core.heap_name == body["heap_name"].upper()
                   for core in self.cores):
                response["error_fields"]["heap_name"] = f"Heap {body['heap_name']} already exists for " \
                                                        f"variation {body['variation']}."
        updated_response, updated_body = get_response_body_for_hex_and_field_data(response, body)
        if updated_response["error_fields"]:
            return updated_response
        core_to_create: Core = create_core_for_hex_and_field_data(updated_body)
        core_to_create.heap_name = body["heap_name"].upper()
        if persistence:
            core_to_create.create()
        self.cores.append(core_to_create)
        if persistence:
            self.save()
        response["message"] = f"Core with heap name {core_to_create.ecb_level} created successfully."
        response["error"] = False
        return response

    def update_heap(self, heap_name: str, variation: int, body: dict, persistence: bool = True):
        response: dict = {"error": True, "message": str(), "error_fields": dict()}
        core_to_update: Core = next((core for core in self.cores if core.variation == variation and
                                     core.heap_name == heap_name), None)
        if not core_to_update:
            response["message"] = f"Heap {heap_name} not found for variation {variation}."
            return response
        if set(body) != {"hex_data", "field_data", "seg_name"}:
            response["message"] = "Only 3 fields allowed (hex_data, field_data and seg_name) and all are mandatory."
            return response
        updated_response, updated_body = get_response_body_for_hex_and_field_data(response, body)
        if updated_response["error_fields"]:
            return updated_response
        core_to_update.hex_data = updated_body["hex_data"]
        core_to_update.seg_name = updated_body["seg_name"]
        core_to_update.field_data = updated_body["field_data"]
        core_to_update.original_field_data = updated_body["original_field_data"]
        if persistence:
            core_to_update.save()
        response["message"] = f"Core with heap {heap_name} updated successfully."
        response["error"] = False
        return response

    def delete_heap(self, heap_name: str, variation: int, persistence: bool = True) -> dict:
        response: dict = {"error": True, "message": str()}
        core: Core = next((core for core in self.cores if core.heap_name == heap_name.upper()
                           and core.variation == variation), None)
        if not core:
            response["message"] = f"Heap {heap_name} not found for variation {variation}."
            return response
        self.cores.remove(core)
        if persistence:
            self.save()
            core.delete()
        response["message"] = f"Heap {heap_name} for variation {variation} successfully deleted."
        response["error"] = False
        return response

    def create_ecb_level(self, body: dict, persistence: bool = True) -> dict:
        response: dict = {"error": True, "message": str(), "error_fields": dict()}
        if set(body) != {"ecb_level", "hex_data", "variation", "variation_name", "field_data", "seg_name"}:
            response["message"] = "Only 6 fields allowed (ecb_level, hex_data, variation, variation_name, " \
                                  "field_data and seg_name) and all are mandatory."
            return response
        if body["ecb_level"] not in config.ECB_LEVELS:
            response["error_fields"]["ecb_level"] = "Invalid ECB level. Level should be between 0 to F."
        if not self._validate_and_update_variation(body, "core"):
            response["error_fields"]["variation"] = "Invalid variation"
        elif "ecb_level" not in response["error_fields"]:
            if any(core.variation == body["variation"] and core.ecb_level == body["ecb_level"] for core in self.cores):
                response["error_fields"]["ecb_level"] = f"ECB level {body['ecb_level']} already exists for " \
                                                        f"variation {body['variation']}."
        updated_response, updated_body = get_response_body_for_hex_and_field_data(response, body)
        if updated_response["error_fields"]:
            return updated_response
        core_to_create: Core = create_core_for_hex_and_field_data(updated_body)
        core_to_create.ecb_level = body["ecb_level"].upper()
        if persistence:
            core_to_create.create()
        self.cores.append(core_to_create)
        if persistence:
            self.save()
        response["message"] = f"Core with ECB level {core_to_create.ecb_level} created successfully."
        response["error"] = False
        return response

    def update_ecb_level(self, ecb_level: str, variation: int, body: dict, persistence: bool = True):
        response: dict = {"error": True, "message": str(), "error_fields": dict()}
        core_to_update: Core = next((core for core in self.cores if core.variation == variation and
                                     core.ecb_level == ecb_level), None)
        if not core_to_update:
            response["message"] = f"ECB level {ecb_level} not found for variation {variation}."
            return response
        if set(body) != {"hex_data", "field_data", "seg_name"}:
            response["message"] = "Only 3 fields allowed (hex_data, field_data and seg_name) and all are mandatory."
            return response
        updated_response, updated_body = get_response_body_for_hex_and_field_data(response, body)
        if updated_response["error_fields"]:
            return updated_response
        core_to_update.hex_data = updated_body["hex_data"]
        core_to_update.seg_name = updated_body["seg_name"]
        core_to_update.field_data = updated_body["field_data"]
        core_to_update.original_field_data = updated_body["original_field_data"]
        if persistence:
            core_to_update.save()
        response["message"] = f"Core with ECB level {ecb_level} updated successfully."
        response["error"] = False
        return response

    def delete_ecb_level(self, ecb_level: str, variation: int, persistence: bool = True) -> dict:
        response: dict = {"error": True, "message": str()}
        core: Core = next((core for core in self.cores if core.ecb_level == ecb_level.upper()
                           and core.variation == variation), None)
        if not core:
            response["message"] = f"ECB level {ecb_level} not found for variation {variation}."
            return response
        self.cores.remove(core)
        if persistence:
            self.save()
            core.delete()
        response["message"] = f"ECB level {ecb_level} for variation {variation} successfully deleted."
        response["error"] = False
        return response

    def add_reg(self, reg_dict: dict) -> bool:
        if "reg" not in reg_dict or not Register(reg_dict["reg"]).is_valid():
            return False
        if "value" not in reg_dict or not isinstance(reg_dict["value"], int):
            return False
        if len(reg_dict) != 2:
            return False
        if reg_dict["value"] < -0x80000000 or reg_dict["value"] > 0x7FFFFFFF:
            return False
        self.regs[reg_dict["reg"]] = reg_dict["value"]
        self.save()
        return True

    def delete_reg(self, reg: str) -> bool:
        if not Register(reg).is_valid():
            return False
        if reg not in self.regs:
            return False
        del self.regs[reg]
        self.save()
        return True

    def create_pnr_element(self, pnr_dict: dict, persistence: bool = True) -> Optional[Pnr]:
        if not Pnr.validate(pnr_dict):
            return None
        if not self._validate_and_update_variation(pnr_dict, "pnr"):
            return None
        pnr_dict["field_data"] = list()
        pnr_data = pnr_dict["data"].split(",")
        pnr = None
        for data in pnr_data:
            pnr_dict["data"] = data.strip()
            pnr = Pnr.create_from_dict(pnr_dict) if persistence else Pnr.dict_to_doc(pnr_dict)
            self.pnr.append(pnr)
        if persistence:
            self.save()
        return pnr

    def create_pnr_output(self, pnr_output_dict: dict, persistence: bool = True) -> Optional[PnrOutput]:
        if not {"field_len", "key"}.issubset(pnr_output_dict):
            return None
        if not pnr_output_dict["field_len"] or not isinstance(pnr_output_dict["field_len"], dict):
            return None
        if db_pnr.Pnr.get_attribute_by_name(pnr_output_dict["key"]) is None:
            return None
        if persistence:
            pnr_output: PnrOutput = PnrOutput.create_from_dict(pnr_output_dict)
        else:
            pnr_output: PnrOutput = PnrOutput.dict_to_doc(pnr_output_dict)
        self.output.pnr_outputs.append(pnr_output)
        if persistence:
            self.output.save()
        return pnr_output

    def delete_pnr_element(self, pnr_id: str) -> Optional[Pnr]:
        pnr: Pnr = next((pnr for pnr in self.pnr if pnr.id == pnr_id), None)
        if not pnr:
            return None
        copy_pnr = deepcopy(pnr)
        self.pnr.remove(pnr)
        self.save()
        pnr.delete(cascade=True)
        return copy_pnr

    def delete_pnr_output(self, pnr_id: str) -> Optional[PnrOutput]:
        pnr_output: PnrOutput = next((pnr for pnr in self.output.pnr_outputs if pnr.id == pnr_id), None)
        if not pnr_output:
            return None
        copy_pnr = deepcopy(pnr_output)
        self.output.pnr_outputs.remove(pnr_output)
        self.save()
        pnr_output.delete(cascade=True)
        return copy_pnr

    def create_pnr_field_data(self, pnr_id: str, core_dict: dict, persistence=True) -> Optional[Pnr]:
        pnr = next((pnr for pnr in self.pnr if pnr.id == pnr_id), None)
        if not pnr:
            return None
        if not isinstance(core_dict, dict) or "macro_name" not in core_dict or "field_data" not in core_dict:
            return None
        if core_dict["macro_name"] not in macros:
            return None
        macro: DataMacro = macros[core_dict["macro_name"]]
        macro.load()
        if not isinstance(core_dict["field_data"], dict):
            return None
        for field, value in core_dict["field_data"].items():
            if not macro.check(field):
                return None
            if not isinstance(value, str):
                return None
        for field, value in core_dict["field_data"].items():
            field_dict = {"field": field, "data": value}
            field_byte = next((field_byte for field_byte in pnr.field_data
                               if field_byte["field"] == field_dict["field"]), None)
            if not field_byte:
                field_byte = field_dict
                pnr.field_data.append(field_byte)
            else:
                field_byte["data"] = field_dict["data"]
        pnr.data = str()
        if persistence:
            pnr.save()
        return pnr

    def create_tpfdf_lrec(self, df_dict: dict, persistence=True) -> Optional[Tpfdf]:
        if set(df_dict) != {"key", "field_data", "macro_name", "variation", "variation_name"}:
            return None
        if not isinstance(df_dict["key"], str) or len(df_dict["key"]) != 2 or not df_dict["key"].isalnum():
            return None
        if df_dict["macro_name"] not in macros:
            return None
        df_macro = macros[df_dict["macro_name"]]
        df_macro.load()
        if not isinstance(df_dict["field_data"], dict) or not df_dict["field_data"]:
            return None
        if not self._validate_and_update_variation(df_dict, "tpfdf"):
            return None
        for field, value in df_dict["field_data"].items():
            if not df_macro.check(field):
                return None
            if not isinstance(value, str):
                return None
        df_dict = df_dict.copy()
        df_dict["key"] = df_dict["key"].upper()
        df_dict["field_data"] = [{"field": field, "data": value} for field, value in df_dict["field_data"].items()]
        df_lrec = next((lrec for lrec in self.tpfdf if lrec.field_data == df_dict["field_data"] and
                        lrec.macro_name == df_dict["macro_name"] and lrec.key == df_dict["key"] and
                        lrec.variation == df_dict["variation"]), None)
        if df_lrec:
            return None
        df_doc = Tpfdf.create_from_dict(df_dict) if persistence else Tpfdf.dict_to_doc(df_dict)
        self.tpfdf.append(df_doc)
        if persistence:
            self.save()
        return df_doc

    def delete_tpfdf_lrec(self, df_id: str) -> Optional[Tpfdf]:
        lrec: Tpfdf = next((lrec for lrec in self.tpfdf if lrec.id == df_id), None)
        if not lrec:
            return None
        copy_lrec = deepcopy(lrec)
        self.tpfdf.remove(lrec)
        self.save()
        lrec.delete(cascade=True)
        return copy_lrec

    def create_fixed_file(self, file_dict: dict, persistence: bool = True) -> Optional[FixedFile]:
        if not FixedFile.validate(file_dict):
            return None
        if not self._validate_and_update_variation(file_dict, "file"):
            return None
        if "pool_files" in file_dict:
            if not all(file_dict["macro_name"] == pool_file["index_macro_name"]
                       for pool_file in file_dict["pool_files"]):
                return None
        fixed_file = next((file for file in self.fixed_files
                           if file.macro_name == file_dict["macro_name"] and
                           file.rec_id == file_dict["rec_id"] and
                           file.fixed_ordinal == file_dict["fixed_ordinal"] and
                           file.fixed_type == file_dict["fixed_type"] and
                           file.variation == file_dict["variation"]), None)
        if fixed_file:
            return None
        fixed_file = FixedFile.create_from_dict(file_dict) if persistence else \
            FixedFile.dict_to_doc(file_dict, cascade=True)
        self.fixed_files.append(fixed_file)
        if persistence:
            self.save()
        return fixed_file

    def delete_fixed_file(self, file_id: str) -> Optional[FixedFile]:
        file: FixedFile = next((file for file in self.fixed_files if file.id == file_id), None)
        if not file:
            return None
        copy_file = deepcopy(file)
        self.fixed_files.remove(file)
        self.save()
        file.delete(cascade=True)
        return copy_file


TestData.init("test_data")
