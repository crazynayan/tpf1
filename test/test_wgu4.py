import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS


class Wgu4Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()

    def test_wgu4(self):
        test_data = self.tpf_server.run('WGU4', self.test_data)
        self.assertEqual('WGU4AA02.3', test_data.output.last_line)
        # self.assertEqual(list(), test_data.output.messages)
