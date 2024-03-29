import unittest
from base64 import b64encode
from copy import deepcopy

from d21_backend.config import config
from d21_backend.p1_utils.data_type import DataType
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p3_db.test_data_elements import FixedFile, PoolFile, FileItem
from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class Tsj1Test(unittest.TestCase):
    tpf_server: TpfServer = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.tpf_server = TpfServer()

    @classmethod
    def tearDownClass(cls) -> None:
        return

    def setUp(self) -> None:
        self.tpf_server.init_run("TSJ1")
        self.test_data = TestDataUTS()
        # Test data setup
        self.test_data.add_pnr_element(["BJS-BOM3/GRANT ACCESS"], "group_plan")
        self.test_data.set_field("WA0POR", DataType("X", input="006F2F").to_bytes())
        self.test_data.set_field("WA0FNS", bytes([get_macros()["WA0AA"].evaluate("#WA0TVL")]))
        self.test_data.add_all_regs()
        # Item setup
        self.iy_item = [{"field": "IY9AON", "data": b64encode(bytearray([config.ZERO] * 4)).decode()},
                        {"field": "IY9AGY", "data": b64encode(bytearray([config.ZERO])).decode()}]

    def _tjr_setup(self, iy_chain_count: int = 0, variation: int = 0):
        fixed_file = FixedFile()
        fixed_file.variation = variation
        fixed_file.rec_id = DataType("C", input="TJ").value
        fixed_file.macro_name = "TJ0TJ"
        fixed_file.fixed_type = get_macros()["SYSEQC"].evaluate("#TJRRI")
        fixed_file.fixed_ordinal = 0x17F
        pool_file = PoolFile()
        fixed_file.pool_files.append(pool_file)
        pool_file.macro_name = "IY1IY"
        pool_file.rec_id = DataType("C", input="IY").value
        pool_file.index_macro_name = "TJ0TJ"
        pool_file.index_field = "TJ0ATH"
        pool_file.forward_chain_label = "IY1FCH"
        pool_file.forward_chain_count = iy_chain_count
        item = FileItem()
        pool_file.file_items.append(item)
        item.macro_name = "IY1IY"
        item.field = "IY1ATH"
        item.field_data = deepcopy(self.iy_item)
        item.count_field = "IY1CTR"
        file_dict = fixed_file.cascade_to_dict()
        del file_dict["id"]
        del file_dict["pool_files"][0]["id"]
        del file_dict["pool_files"][0]["file_items"][0]["id"]
        self.test_data.create_fixed_file(file_dict, persistence=False)
        return

    def test_branch_validation_fail_lok_off(self) -> None:
        self.iy_item[0]["data"] = b64encode(DataType("X", input="00006F2F").to_bytes()).decode()
        self._tjr_setup(2)
        test_data = self.tpf_server.run("TSJ1", self.test_data)
        self.assertEqual("TSJ1ERR.3", test_data.output.last_line)
        self.assertEqual(8, test_data.output.regs["R6"])

    def test_branch_validation_pass_lok_on(self) -> None:
        self.iy_item[0]["data"] = b64encode(DataType("X", input="00006F2F").to_bytes()).decode()
        get_macros()["IY1IY"].load()
        self.iy_item[1]["data"] = b64encode(bytearray([get_macros()["IY1IY"].evaluate("#IY1LOK")])).decode()
        self._tjr_setup()
        test_data = self.tpf_server.run("TSJ1", self.test_data)
        self.assertEqual("TSJ1PASS.3", test_data.output.last_line)

    def test_finwc_fail(self) -> None:
        self.iy_item[0]["data"] = b64encode(DataType("X", input="00006F2F").to_bytes()).decode()
        self._tjr_setup()
        self.test_data.errors.append("TSJ1FINE")
        test_data = self.tpf_server.run("TSJ1", self.test_data)
        self.assertEqual("TSJ1500.1", test_data.output.last_line)
        self.assertIn("BAD123", test_data.output.dumps)

    def test_variation(self):
        self.iy_item[0]["data"] = b64encode(DataType("X", input="00006F2F").to_bytes()).decode()
        self._tjr_setup()
        self.iy_item[1]["data"] = b64encode(bytearray([get_macros()["IY1IY"].evaluate("#IY1LOK")])).decode()
        self._tjr_setup(variation=1)
        test_data = self.tpf_server.run("TSJ1", self.test_data)
        self.assertEqual("TSJ1ERR.3", test_data.outputs[0].last_line)
        self.assertEqual(8, test_data.outputs[0].regs["R6"])
        self.assertEqual("TSJ1PASS.3", test_data.outputs[1].last_line)
        self.assertEqual(0, test_data.outputs[1].regs["R6"])


if __name__ == "__main__":
    unittest.main()
