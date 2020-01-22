import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS


class Ts23Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.test_data.add_fields([('EBW000', 28)], 'EB0EB')

    def test_tpfdf_ts20(self):
        test_data = self.tpf_server.run('TS23', self.test_data)
        self.assertEqual('00000001000000020000000300000004000000050000000600000007', test_data.get_field('EBW000'))


if __name__ == '__main__':
    unittest.main()
