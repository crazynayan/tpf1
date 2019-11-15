import unittest

from execution.ex5_execute import Execute
from firestore.test_data import TestData
from test.input_td import TD


class DbTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestData()
        self.ecb = self.test_data.add_core(['EBW000'], 'EB0EB', output=True)
        self.output = self.test_data.output
        self.output.add_regs(['R0'])

    def test_tpfdf_ts20(self):
        self.test_data.add_tpfdf(TD.tr1gaa, '40', 'TR1GAA')
        self.tpf_server.run('TS20', self.test_data)
        self.assertEqual(21, self.output.regs['R0'])
        self.assertEqual('80', self.ecb['EBW000'].hex)


if __name__ == '__main__':
    unittest.main()
