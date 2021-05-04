import unittest

from p1_utils.data_type import DataType
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class EtaxTest(unittest.TestCase):
    DEBUG_DATA = list()

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.output.debug = ["ETAX"]
        self.output = None

    def tearDown(self) -> None:
        for debug_line in self.output.debug:
            if debug_line in self.DEBUG_DATA:
                continue
            self.DEBUG_DATA.append(debug_line)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"ETAX LOC = {len(cls.DEBUG_DATA)}")

    def test_etax_vanilla(self):
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAX265.6", test_data.output.last_line, test_data.output.last_node)
        self.assertIn("UNABLE TO END TRANSACTION - NO PNR PRESENT IN WORK AREA", test_data.output.messages)
        self.assertEqual(list(), test_data.output.dumps)
        self.output = test_data.output

    def test_etax_efp(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="EFP").to_bytes())
        self.test_data.add_fields(["UI2CNN"], "UI2PF", "R7")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("$$UIO1$$.2", test_data.output.last_line, test_data.output.last_node)
        self.assertEqual("33", test_data.get_field("UI2CNN"))
        self.output = test_data.output

    def test_etax_efc(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="EF$").to_bytes())
        self.test_data.add_fields(["UI2CNN"], "UI2PF", "R7")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("$$UIO1$$.2", test_data.output.last_line, test_data.output.last_node)
        self.assertEqual("33", test_data.get_field("UI2CNN"))
        self.output = test_data.output

    def test_etax_efs(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="EF*").to_bytes())
        self.test_data.add_fields(["UI2CNN"], "UI2PF", "R7")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAX265.6", test_data.output.last_line, test_data.output.last_node)
        self.assertIn("UNABLE TO END TRANSACTION - NO PNR PRESENT IN WORK AREA", test_data.output.messages)
        self.output = test_data.output
