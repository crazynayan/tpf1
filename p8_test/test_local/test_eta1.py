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

    def test_eta1_el_restricted(self):
        self.test_data.add_fields([("EBW000", 10)], "EB0EB")
        self.test_data.set_field("MI0ACC", DataType("C", input="EL").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.set_field("WA0UB4", DataType("X", input="08").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("$$UIO1$$.2", test_data.output.last_line, test_data.output.last_node)
        self.assertIn("RESTRICTED" + 40 * " ", test_data.output.messages)

    def test_eta1_e_no_error(self):
        self.test_data.add_fields([("EBW000", 10)], "EB0EB")
        self.test_data.set_field("MI0ACC", DataType("C", input="E").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.set_field("WA0UB4", DataType("X", input="08").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAX0000", test_data.output.last_line, test_data.output.last_node)
        self.assertNotIn("EXECUTION ERROR", test_data.output.messages)
        self.assertEqual("00000000000000000000", test_data.get_field("EBW000"))  # NO ERROR

    def test_eta1_el_plus_off_queue(self):
        self.test_data.add_fields([("EBW000", 10)], "EB0EB")
        self.test_data.set_field("MI0ACC", DataType("C", input="EL+").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("$$UIO1$$.2", test_data.output.last_line, test_data.output.last_node)
        off_queue = "CANNOT DO THIS IF OFF QUEUE"
        self.assertIn(off_queue + (50 - len(off_queue)) * " ", test_data.output.messages)

    def test_eta1_el_off_queue(self):
        self.test_data.add_fields([("EBW000", 10)], "EB0EB")
        self.test_data.set_field("MI0ACC", DataType("C", input="EL").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAX0000", test_data.output.last_line, test_data.output.last_node)
        self.assertNotIn("EXECUTION ERROR", test_data.output.messages)
        self.assertEqual(list(), test_data.output.dumps)
