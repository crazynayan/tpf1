import unittest

from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class Ts26Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()

    def test_ts26(self):
        test_data = self.tpf_server.run("TS26", self.test_data)
        self.assertIn("EXECUTION ERROR", test_data.output.messages)
        self.assertIn("000003", test_data.output.dumps)
        self.assertEqual("$$TS26$$.1", test_data.output.last_line)


if __name__ == '__main__':
    unittest.main()
