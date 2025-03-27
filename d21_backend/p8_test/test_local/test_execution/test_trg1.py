import unittest
from base64 import b64encode
from copy import deepcopy
from d21_backend.p1_utils.data_type import DataType
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p3_db.test_data_elements import FixedFile, PoolFile, FileItem
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
        # Item setup
        self.t4_item = [{"field": "T40CCD", "data": b64encode(bytearray([0xC1, 0xC1])).decode()}]
        self.u4_item = [{"field": "U49CAR", "data": b64encode(bytearray([0xC1, 0xC1])).decode()},
                        {"field": "U49NAM", "data": b64encode(bytearray([0xC1, 0xD4, 0xC5, 0xD9, 0xC9, 0xC3, 0xC1, 0xD5, 0x40, 0xC1, 0xC9, 0xD9, 0xD3, 0xC9, 0xD5, 0xC5, 0xE2])).decode()}]

    def _tjr_setup(self, u4_chain_count: int = 0):
        # Fixed File setup
        fixed_file = FixedFile()
        fixed_file.variation = 0
        fixed_file.rec_id = DataType("C", input="4T").value
        fixed_file.macro_name = "T404T"
        fixed_file.fixed_type = get_macros()["SYSEQC"].evaluate("#MISCL")
        fixed_file.fixed_ordinal = 0x6E
        item = FileItem()
        fixed_file.file_items.append(item)
        item.macro_name = "T404T"
        item.field = "T40ITM"
        item.field_data = deepcopy(self.t4_item)
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
        item = FileItem()
        pool_file.file_items.append(item)
        item.macro_name = "U404U"
        item.field = "U40ITM"
        item.field_data = deepcopy(self.u4_item)
        item.count_field = "U40NBR"
        item.adjust = False
        file_dict = fixed_file.cascade_to_dict()
        del file_dict["id"]
        del file_dict["file_items"][0]["id"]
        del file_dict["pool_files"][0]["id"]
        del file_dict["pool_files"][0]["file_items"][0]["id"]
        self.test_data.create_fixed_file(file_dict, persistence=False)
        return

    def test_cct01_carrier_code_to_airline_name_translation(self) -> None:
        # Test data setup
        self.test_data.set_global_field("@TRROR", "0000006E", 0)
        self.test_data.set_global_field("@TRROR", "0000006E", 1)
        self.test_data.set_global_field("@TRROR", "0000006E", 2)
        self.test_data.set_global_field("@TRROR", "0000006E", 3)
        self.test_data.create_ecb_level({"variation": 0, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161C1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 1, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161C2C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 2, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C2C161C1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 3, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C2C161C2C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self._tjr_setup()
        self.test_data.output.debug = ["TRG1"]
        test_data = self.tpf_server.run("TRG1", self.test_data)
        self.assertListEqual([],test_data.outputs[0].dumps)
        self.assertEqual("AMERICAN AIRLIN", test_data.outputs[0].messages[0][:15])
        self.assertIn("CARRIER CODE NOT PRESENT", test_data.outputs[1].messages)
        self.assertIn("TRAINEE CODE NOT PRESENT", test_data.outputs[2].messages)
        self.assertIn("TRAINEE CODE NOT PRESENT", test_data.outputs[3].messages)

    def test_cct02_input_entry_validation(self) -> None:
        self.test_data.create_ecb_level({"variation": 0, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161C1C1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 1, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D76161C1C161C1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 2, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C1C1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 3, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161F1C161C1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 4, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1F161C1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 5, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161F1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self.test_data.create_ecb_level({"variation": 6, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161C1F14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self._tjr_setup()
        test_data = self.tpf_server.run("TRG1", self.test_data)
        self.assertIn("INVALID CARRIER CODE", test_data.outputs[0].messages)
        self.assertIn("INVALID ACTION CODE", test_data.outputs[1].messages)
        self.assertIn("INVALID SEPARATOR", test_data.outputs[2].messages)
        self.assertIn("TRAINEE CODE NOT ALPHA", test_data.outputs[3].messages)
        self.assertIn("TRAINEE CODE NOT ALPHA", test_data.outputs[4].messages)
        self.assertIn("CARRIER CODE NOT ALPHA", test_data.outputs[5].messages)
        self.assertIn("CARRIER CODE NOT ALPHA", test_data.outputs[6].messages)

    def test_cct03_file_error(self) -> None:
        # Test data setup
        self.test_data.set_global_field("@TRROR", "00000000", 0)
        self.test_data.create_ecb_level({"variation": 0, "variation_name": str(), "ecb_level": "0", "hex_data": "0000D96161C1C161C1C14E",
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        self._tjr_setup()
        test_data = self.tpf_server.run("TRG1", self.test_data)
        self.assertIn("CAD002", test_data.outputs[0].dumps)

if __name__ == "__main__":
    unittest.main()