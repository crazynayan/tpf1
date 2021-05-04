import unittest

from p1_utils.data_type import DataType
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class EtafTest(unittest.TestCase):
    DEBUG_DATA = list()

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.output.debug = ["ETAF"]
        self.output = None

    def tearDown(self) -> None:
        if not self.output or not self.output.debug:
            return
        for debug_line in self.output.debug:
            if debug_line in self.DEBUG_DATA:
                continue
            self.DEBUG_DATA.append(debug_line)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"ETAF LOC = {len(cls.DEBUG_DATA)}")

    def test_etaf_vanilla(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAF1300.1", test_data.output.last_line, test_data.output.last_node)
        self.assertIn("ITINERARY REQUIRED TO COMPLETE TRANSACTION", test_data.output.messages)
        self.assertEqual(list(), test_data.output.dumps)
        self.output = test_data.output

    def test_etaf_itinerary(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertIn("000004", test_data.output.dumps)
        self.assertEqual("ETAZ2500.1", test_data.output.last_line, test_data.output.last_node)
        self.output = test_data.output
