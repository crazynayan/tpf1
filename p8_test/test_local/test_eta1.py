import unittest

from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class Eta1Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()

    def test_eta1(self):
        self.test_data.output.debug = ["ETA1"]
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.assertEqual("ETAX0000", test_data.output.last_line, test_data.output.last_node)
        self.assertNotIn("EXECUTION ERROR", test_data.output.messages)
        self.assertEqual(list(), test_data.output.dumps)
