import unittest

from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS
from p8_test.test_local.test_eta5_execution import tr1gaa


class DbTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_fields(['EBW000'], 'EB0EB')
        self.test_data.add_all_regs()

    def test_tpfdf_ts20(self):
        self.test_data.add_tpfdf(tr1gaa, '40', 'TR1GAA')
        test_data = self.tpf_server.run('TS20', self.test_data)
        self.assertEqual(21, test_data.output.regs['R0'])
        self.assertEqual('80', test_data.get_field('EBW000'))


if __name__ == '__main__':
    unittest.main()
