import unittest
from base64 import b64encode

from execution.ex5_execute import Execute
from test import TestDataUTS


class Conditional(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.output = self.test_data.output
        self.output.add_all_regs()
        ecb_fields = [('EBW020', 4), ('EBW024', 4)]
        self.ecb = self.test_data.add_fields(ecb_fields, 'EB0EB')
        ecb_fields = ['EBW015', 'EBW016', 'EBW010', 'EBW011', 'EBW012', 'EBW013']
        ecb_len = self.test_data.add_fields(ecb_fields, 'EB0EB', output=True)
        self.ecb = {**self.ecb, **ecb_len}
        ecb_fields = ['EBW000', 'EBW004', 'EBW008', 'EBW009']
        self.i_ecb = self.test_data.add_fields(ecb_fields, 'EB0EB')
        self.i_regs = self.test_data.add_all_regs()

    def test_ts16_1(self):
        # Default state is 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1.1, 7.2.1, 7.3.1, 7.4.1
        test_data = self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(1, test_data.output.regs['R0'])
        self.assertEqual(2, test_data.output.regs['R1'])
        self.assertEqual(1, test_data.output.regs['R2'])
        self.assertEqual(1, test_data.output.regs['R3'])
        self.assertEqual(1, test_data.output.regs['R4'])
        self.assertEqual(1, test_data.output.regs['R5'])
        self.assertEqual('C2C2C200', test_data.field('EBW020'))
        self.assertEqual(0x32, test_data.output.regs['R7'])
        self.assertEqual('0000123C', test_data.field('EBW024'))
        self.assertEqual('10', test_data.field('EBW015'))
        self.assertEqual('02', test_data.field('EBW016'))
        # Test subroutines
        self.assertEqual('0A', test_data.field('EBW010'))
        self.assertEqual('00', test_data.field('EBW011'))
        self.assertEqual('0C', test_data.field('EBW012'))
        self.assertEqual('0D', test_data.field('EBW013'))

    def test_ts16_2(self):
        # Update state to 1.2, 2.2, 3.2, 4.2, 5.2, 7.1.2, 7.2.2, 7.3.2, 7.4.2
        self.i_ecb['EBW000']['data'] = b64encode(bytearray([0xC1, 0xC2, 0xC3, 0xC4])).decode()
        self.i_ecb['EBW004']['data'] = b64encode(bytearray([0xC1, 0xC2, 0xC3, 0xC5])).decode()
        self.i_ecb['EBW008']['data'] = b64encode(bytearray([0xC1])).decode()
        self.i_ecb['EBW009']['data'] = b64encode(bytearray([0x11])).decode()
        self.i_regs['R15'] = -10
        self.i_regs['R14'] = 23
        test_data = self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(2, test_data.output.regs['R0'])
        self.assertEqual(3, test_data.output.regs['R1'])
        self.assertEqual(2, test_data.output.regs['R2'])
        self.assertEqual(1, test_data.output.regs['R3'])
        self.assertEqual(2, test_data.output.regs['R4'])
        self.assertEqual(2, test_data.output.regs['R5'])
        self.assertEqual('0B', test_data.field('EBW011'))
        self.assertEqual('C2C2C2C2', test_data.field('EBW020'))
        self.assertEqual(0x33, test_data.output.regs['R7'])
        self.assertEqual('0001234C', test_data.field('EBW024'))
        self.assertEqual('0F', test_data.field('EBW015'))
        self.assertEqual('03', test_data.field('EBW016'))

    def test_ts16_3(self) -> None:
        # Update state to 3.3, 5.3
        self.i_regs['R15'] = 10
        self.i_ecb['EBW009']['data'] = b64encode(bytearray([0x10])).decode()
        test_data = self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(3, test_data.output.regs['R2'])
        self.assertEqual(2, test_data.output.regs['R3'])
        self.assertEqual(3, test_data.output.regs['R5'])


if __name__ == '__main__':
    unittest.main()
