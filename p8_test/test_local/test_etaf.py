import unittest

from p1_utils.data_type import DataType
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class EtafTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()

    def test_etaf_vanilla(self) -> None:
        self.test_data.output.debug = ["ETAF"]
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAF1300.1", test_data.output.last_line, test_data.output.last_node)
        self.assertIn("ITINERARY REQUIRED TO COMPLETE TRANSACTION", test_data.output.messages)
        self.assertEqual(list(), test_data.output.dumps)
