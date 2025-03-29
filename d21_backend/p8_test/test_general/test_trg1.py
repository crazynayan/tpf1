import unittest
from base64 import b64encode
from copy import deepcopy

from munch import Munch

from d21_backend.p1_utils.data_type import DataType
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p3_db.profiler_methods import run_profiler
from d21_backend.p3_db.startup_script import test_data_create
from d21_backend.p3_db.test_data import TestData
from d21_backend.p3_db.test_data_elements import FixedFile, PoolFile, FileItem
from d21_backend.p3_db.test_data_get import get_whole_test_data
from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class CctTest(unittest.TestCase):
    tpf_server: TpfServer = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.tpf_server = TpfServer()

    @classmethod
    def tearDownClass(cls) -> None:
        return

    def setUp(self) -> None:
        self.tpf_server.init_run("TRG1")
        self.test_data = TestDataUTS()
        # Test data display fields
        self.test_data.add_fields([("EBW000",2),("EBX00",2),("EBT000",2)],"EB0EB")

    @staticmethod
    def file_setup(test_data: TestData, u4_chain_count: int = 0, persistence: bool = False):
        # Fixed File setup
        fixed_file = FixedFile()
        fixed_file.variation = 0
        fixed_file.rec_id = DataType("C", input="4T").value
        fixed_file.macro_name = "T404T"
        fixed_file.fixed_type = get_macros()["SYSEQC"].evaluate("#MISCL")
        fixed_file.fixed_ordinal = 0x6E
        # Fixed File item
        item = FileItem()
        fixed_file.file_items.append(item)
        item.macro_name = "T404T"
        item.field = "T40ITM"
        t40ccd_field: Munch = Munch()
        t40ccd_field.field = "T40CCD"
        t40ccd_field.data = b64encode(DataType("C", input="AA").to_bytes()).decode()
        item.field_data = [t40ccd_field]
        item.count_field = "T40NBR"
        item.adjust = True
        # Pool File setup
        pool_file = PoolFile()
        fixed_file.pool_files.append(pool_file)
        pool_file.macro_name = "U404U"
        pool_file.rec_id = DataType("C", input="4U").value
        pool_file.index_macro_name = "T404T"
        pool_file.index_field = "T40FAD"
        pool_file.forward_chain_label = "U40FCH"
        pool_file.forward_chain_count = u4_chain_count
        # Pool File item
        item = FileItem()
        pool_file.file_items.append(item)
        item.macro_name = "U404U"
        item.field = "U40ITM"
        u49car_field: Munch = Munch()
        u49car_field.field = "U49CAR"
        u49car_field.data = b64encode(DataType("C", input="AA").to_bytes()).decode()
        u49nam_field = Munch()
        u49nam_field.field = "U49NAM"
        u49nam_field.data = b64encode(DataType("C", input="AMERICAN AIRLINES").to_bytes()).decode()
        item.field_data = [u49car_field, u49nam_field]
        item.count_field = "U40NBR"
        item.adjust = False
        # Update test data
        file_dict = fixed_file.cascade_to_dict()
        del file_dict["id"]
        del file_dict["file_items"][0]["id"]
        del file_dict["pool_files"][0]["id"]
        del file_dict["pool_files"][0]["file_items"][0]["id"]
        test_data.create_fixed_file(file_dict, persistence=persistence)
        return

    def create_cct01_carrier_code_to_airline_name_translation(self, test_data: TestData, persistence: bool = False) -> None:
        create_global_request: Munch = Munch()
        create_global_request.global_name = "@TRROR"
        create_global_request.variation_name = ""
        create_global_request.is_global_record = False
        create_global_request.hex_data = "0000006E"
        create_global_request.seg_name = ""
        create_global_request.field_data = ""
        create_global_request0 = deepcopy(create_global_request)
        create_global_request0.variation = 0
        test_data.create_global(create_global_request0, persistence=persistence)
        create_global_request1 = deepcopy(create_global_request)
        create_global_request1.variation = 1
        test_data.create_global(create_global_request1, persistence=persistence)
        create_global_request2 = deepcopy(create_global_request)
        create_global_request2.variation = 2
        test_data.create_global(create_global_request2, persistence=persistence)
        create_global_request3 = deepcopy(create_global_request)
        create_global_request3.variation = 3
        test_data.create_global(create_global_request3, persistence=persistence)
        create_ecb_level_request: Munch = Munch()
        create_ecb_level_request.variation_name = ""
        create_ecb_level_request.ecb_level = "0"
        create_ecb_level_request.field_data = ""
        create_ecb_level_request.seg_name = ""
        create_ecb_level_request0: Munch = deepcopy(create_ecb_level_request)
        create_ecb_level_request0.variation = 0
        create_ecb_level_request0.hex_data = "0000D96161C1C161C1C14E"
        test_data.create_ecb_level(create_ecb_level_request0, persistence=persistence)
        create_ecb_level_request1: Munch = deepcopy(create_ecb_level_request)
        create_ecb_level_request1.variation = 1
        create_ecb_level_request1.hex_data = "0000D96161C1C161C2C14E"
        test_data.create_ecb_level(create_ecb_level_request1, persistence=persistence)
        create_ecb_level_request2: Munch = deepcopy(create_ecb_level_request)
        create_ecb_level_request2.variation = 2
        create_ecb_level_request2.hex_data = "0000D96161C2C161C1C14E"
        test_data.create_ecb_level(create_ecb_level_request2, persistence=persistence)
        create_ecb_level_request3: Munch = deepcopy(create_ecb_level_request)
        create_ecb_level_request3.variation = 3
        create_ecb_level_request3.hex_data = "0000D96161C2C161C2C14E"
        test_data.create_ecb_level(create_ecb_level_request3, persistence=persistence)
        self.file_setup(test_data, persistence=persistence)
        test_data.output.debug = ["TRG1"]
        return

    def create_cct02_input_entry_validation(self, test_data, persistence: bool = False) -> None:
        # TODO: make this as above test_data creation
        test_data.create_ecb_level({"variation": 0, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161C1C1C14E",
                                    "field_data": str(), "seg_name": str()}, persistence=persistence)
        test_data.create_ecb_level({"variation": 1, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D76161C1C161C1C14E",
                                    "field_data": str(), "seg_name": str()}, persistence=persistence)
        test_data.create_ecb_level({"variation": 2, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C1C1C14E",
                                    "field_data": str(), "seg_name": str()}, persistence=persistence)
        test_data.create_ecb_level({"variation": 3, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161F1C161C1C14E",
                                    "field_data": str(), "seg_name": str()}, persistence=persistence)
        test_data.create_ecb_level({"variation": 4, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1F161C1C14E",
                                    "field_data": str(), "seg_name": str()}, persistence=persistence)
        test_data.create_ecb_level({"variation": 5, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161F1C14E",
                                    "field_data": str(), "seg_name": str()}, persistence=persistence)
        test_data.create_ecb_level({"variation": 6, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161C1F14E",
                                    "field_data": str(), "seg_name": str()}, persistence=persistence)
        self.file_setup(test_data, persistence=persistence)
        return

    def create_cct03_file_error(self, test_data, persistence: bool = False) -> None:
        # TODO: make this as above test_data creation
        test_data.set_global_field("@TRROR", "00000000", 0, persistence=persistence)  # This needs to be updated to use create_global
        test_data.create_ecb_level({"variation": 0, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161C1C14E",
                                    "field_data": str(), "seg_name": str()}, persistence=persistence)
        self.file_setup(test_data, persistence=persistence)
        return

    def test_cct01_carrier_code_to_airline_name_translation(self) -> None:
        self.create_cct01_carrier_code_to_airline_name_translation(self.test_data, persistence=False)
        test_data = self.tpf_server.run("TRG1", self.test_data)
        self.assertListEqual([],test_data.outputs[0].dumps)
        self.assertEqual("AMERICAN AIRLIN", test_data.outputs[0].messages[0][:15])
        self.assertIn("CARRIER CODE NOT PRESENT", test_data.outputs[1].messages)
        self.assertIn("TRAINEE CODE NOT PRESENT", test_data.outputs[2].messages)
        self.assertIn("TRAINEE CODE NOT PRESENT", test_data.outputs[3].messages)

    def test_cct02_input_entry_validation(self) -> None:
        self.create_cct02_input_entry_validation(self.test_data, persistence=False)
        test_data = self.tpf_server.run("TRG1", self.test_data)
        self.assertIn("INVALID CARRIER CODE", test_data.outputs[0].messages)
        self.assertIn("INVALID ACTION CODE", test_data.outputs[1].messages)
        self.assertIn("INVALID SEPARATOR", test_data.outputs[2].messages)
        self.assertIn("TRAINEE CODE NOT ALPHA", test_data.outputs[3].messages)
        self.assertIn("TRAINEE CODE NOT ALPHA", test_data.outputs[4].messages)
        self.assertIn("CARRIER CODE NOT ALPHA", test_data.outputs[5].messages)
        self.assertIn("CARRIER CODE NOT ALPHA", test_data.outputs[6].messages)

    def test_cct03_file_error(self) -> None:
        self.create_cct03_file_error(self.test_data, persistence=False)
        test_data = self.tpf_server.run("TRG1", self.test_data)
        self.assertIn("CAD002", test_data.outputs[0].dumps)

    def test_cct_profiler(self) -> None:
        create_test_data_request: Munch = Munch()
        create_test_data_request.seg_name = "TRG1"
        create_test_data_request.stop_segments = ""
        create_test_data_request.startup_script = ""
        cct01_create_test_data_request = deepcopy(create_test_data_request)
        cct01_create_test_data_request.name = "cct01"
        rsp = test_data_create(cct01_create_test_data_request)
        cct01_test_data_id = rsp["id"]
        self.assertIsNotNone(cct01_test_data_id)
        cct01_test_data = get_whole_test_data(cct01_test_data_id, link=False)
        self.create_cct01_carrier_code_to_airline_name_translation(cct01_test_data, persistence=True)
        # TODO: Add cct02 and cct03
        run_profiler_request: Munch = Munch()
        run_profiler_request.seg_name = "TRG1"
        run_profiler_request.test_data_ids = [cct01_test_data_id]
        rsp = Munch.fromDict(run_profiler(run_profiler_request))
        cct01_test_data.delete_test_data(cct01_test_data_id)
        self.assertEqual("Profiler ran successfully.", rsp.message, rsp.error_fields)
        self.assertEqual("58%", rsp.data.documentation_coverage)




if __name__ == "__main__":
    unittest.main()