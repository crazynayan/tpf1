import unittest

from p1_utils.data_type import DataType
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class Eta1Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()

    def test_eta1_vanilla(self):
        self.test_data.output.debug = ["ETA1"]
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAX0000", test_data.output.last_line, test_data.output.last_node)
        self.assertNotIn("EXECUTION ERROR", test_data.output.messages)
        self.assertEqual(list(), test_data.output.dumps)

    def test_eta1_el(self):
        self.test_data.output.debug = ["ETA1"]
        self.test_data.add_fields([("EBW000", 10)], "EB0EB")
        self.test_data.set_field("MI0ACC", DataType("C", input="EL").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.set_field("WA0UB4", DataType("X", input="08").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("$$UIO1$$.1", test_data.output.last_line, test_data.output.last_node)
        self.assertEqual("D9C5E2E3D9C9C3E3C5C4", test_data.get_field("EBW000"))  # RESTRICTED
