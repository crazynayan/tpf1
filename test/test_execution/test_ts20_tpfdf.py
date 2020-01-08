import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS
from test.test_eta5_execution import tr1gaa


class DbTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.ecb = self.test_data.add_core(['EBW000'], 'EB0EB', output=True)
        self.output = self.test_data.output
        self.output.add_regs(['R0'])

    def test_tpfdf_ts20(self):
        self.test_data.add_tpfdf(tr1gaa, '40', 'TR1GAA')
        self.tpf_server.run('TS20', self.test_data)
        self.assertEqual(21, self.output.regs['R0'])
        self.assertEqual('80', self.test_data.hex(self.ecb['EBW000']['data']))


if __name__ == '__main__':
    unittest.main()
