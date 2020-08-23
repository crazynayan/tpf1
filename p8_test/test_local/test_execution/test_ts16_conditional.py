import unittest

from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class Conditional(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()
        ecb_fields = ['EBW015', 'EBW016', 'EBW010', 'EBW011', 'EBW012', 'EBW013', ('EBW020', 4), ('EBW024', 4)]
        self.test_data.add_fields(ecb_fields, 'EB0EB')
        # self.i_regs = self.test_data.output.add_all_regs()

    def test_ts16_1(self):
        # Default state is 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1.1, 7.2.1, 7.3.1, 7.4.1
        test_data = self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(1, test_data.output.regs['R0'])
        self.assertEqual(2, test_data.output.regs['R1'])
        self.assertEqual(1, test_data.output.regs['R2'])
        self.assertEqual(1, test_data.output.regs['R3'])
        self.assertEqual(1, test_data.output.regs['R4'])
        self.assertEqual(1, test_data.output.regs['R5'])
        self.assertEqual('C2C2C200', test_data.get_field('EBW020'))
        self.assertEqual(0x32, test_data.output.regs['R7'])
        self.assertEqual('0000123C', test_data.get_field('EBW024'))
        self.assertEqual('10', test_data.get_field('EBW015'))
        self.assertEqual('02', test_data.get_field('EBW016'))
        # Test subroutines
        self.assertEqual('0A', test_data.get_field('EBW010'))
        self.assertEqual('00', test_data.get_field('EBW011'))
        self.assertEqual('0C', test_data.get_field('EBW012'))
        self.assertEqual('0D', test_data.get_field('EBW013'))

    def test_ts16_2(self):
        # Update state to 1.2, 2.2, 3.2, 4.2, 5.2, 7.1.2, 7.2.2, 7.3.2, 7.4.2
        self.test_data.set_field('EBW000', bytearray([0xC1, 0xC2, 0xC3, 0xC4]))
        self.test_data.set_field('EBW004', bytearray([0xC1, 0xC2, 0xC3, 0xC5]))
        self.test_data.set_field('EBW008', bytearray([0xC1]))
        self.test_data.set_field('EBW009', bytearray([0x11]))
        self.test_data.regs['R15'] = -10
        self.test_data.regs['R14'] = 23
        test_data = self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(2, test_data.output.regs['R0'])
        self.assertEqual(3, test_data.output.regs['R1'])
        self.assertEqual(2, test_data.output.regs['R2'])
        self.assertEqual(1, test_data.output.regs['R3'])
        self.assertEqual(2, test_data.output.regs['R4'])
        self.assertEqual(2, test_data.output.regs['R5'])
        self.assertEqual('0B', test_data.get_field('EBW011'))
        self.assertEqual('C2C2C2C2', test_data.get_field('EBW020'))
        self.assertEqual(0x33, test_data.output.regs['R7'])
        self.assertEqual('0001234C', test_data.get_field('EBW024'))
        self.assertEqual('0F', test_data.get_field('EBW015'))
        self.assertEqual('03', test_data.get_field('EBW016'))

    def test_ts16_3(self) -> None:
        # Update state to 3.3, 5.3
        self.test_data.regs['R15'] = 10
        self.test_data.set_field('EBW009', bytearray([0x10]))
        test_data = self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(3, test_data.output.regs['R2'])
        self.assertEqual(2, test_data.output.regs['R3'])
        self.assertEqual(3, test_data.output.regs['R5'])


if __name__ == '__main__':
    unittest.main()
