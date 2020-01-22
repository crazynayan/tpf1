import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS


class Ts23Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.test_data.add_fields([('EBW000', 28), 'CE1$UID'], 'EB0EB')
        self.test_data.add_fields(['@HAALC'], 'GLOBAL')

    def test_tpfdf_ts23(self):
        test_data = self.tpf_server.run('TS23', self.test_data)
        self.assertEqual('00000001000000020000000300000004000000050000000600000007', test_data.get_field('EBW000'))
        self.assertEqual('E5E7', test_data.get_field('@HAALC'))
        self.assertEqual('44', test_data.get_field('CE1$UID'))


if __name__ == '__main__':
    unittest.main()
