import unittest

from execution.ex5_execute import TpfServer
from test import TestDataUTS


class Ts25Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_fields([('EBW000', 3), 'EBW003', ('EBW004', 4), ('EBW008', 8), 'EBW020', ('EBW028', 4),
                                   ('EBW032', 4), ('EBW036', 4), ('EBW040', 4), ('EBW044', 4), ('EBW024', 4)], 'EB0EB')

    def test_ts25(self):
        test_data = self.tpf_server.run('TS25', self.test_data)
        self.assertEqual('00789C', test_data.get_field('EBW000'))
        self.assertEqual('01', test_data.get_field('EBW003'))
        self.assertEqual('0000000C', test_data.get_field('EBW004'))
        self.assertEqual('000000000000053C', test_data.get_field('EBW008'))
        self.assertEqual('0000093D', test_data.get_field('EBW028'))
        self.assertEqual('0000186D', test_data.get_field('EBW032'))
        self.assertEqual('0000225D', test_data.get_field('EBW036'))
        self.assertEqual('0000132D', test_data.get_field('EBW040'))
        self.assertEqual('0005148C', test_data.get_field('EBW044'))
        self.assertEqual('132D000C', test_data.get_field('EBW024'))

    def test_tp_valid(self):
        self.test_data.set_field('EBW016', bytes([0x00, 0x12, 0x34, 0x5C]))
        test_data = self.tpf_server.run('TS25', self.test_data)
        self.assertEqual('F0', test_data.get_field('EBW020'))

    def test_tp_sign_invalid(self):
        self.test_data.set_field('EBW016', bytes([0x00, 0x12, 0x34, 0x59]))
        test_data = self.tpf_server.run('TS25', self.test_data)
        self.assertEqual('F1', test_data.get_field('EBW020'))

    def test_tp_digit_invalid(self):
        self.test_data.set_field('EBW016', bytes([0x00, 0x12, 0x3A, 0x5C]))
        test_data = self.tpf_server.run('TS25', self.test_data)
        self.assertEqual('F2', test_data.get_field('EBW020'))

    def test_tp_sign_invalid_and_digit_invalid(self):
        self.test_data.set_field('EBW016', bytes([0x00, 0x12, 0x3A, 0x59]))
        test_data = self.tpf_server.run('TS25', self.test_data)
        self.assertEqual('F3', test_data.get_field('EBW020'))


if __name__ == '__main__':
    unittest.main()
