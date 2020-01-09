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
        self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(1, self.output.regs['R0'])
        self.assertEqual(2, self.output.regs['R1'])
        self.assertEqual(1, self.output.regs['R2'])
        self.assertEqual(1, self.output.regs['R3'])
        self.assertEqual(1, self.output.regs['R4'])
        self.assertEqual(1, self.output.regs['R5'])
        self.assertEqual('C2C2C200', self.test_data.hex(self.ecb['EBW020']['data']))
        self.assertEqual(0x32, self.output.regs['R7'])
        self.assertEqual('0000123C', self.test_data.hex(self.ecb['EBW024']['data']))
        self.assertEqual('10', self.test_data.hex(self.ecb['EBW015']['data']))
        self.assertEqual('02', self.test_data.hex(self.ecb['EBW016']['data']))
        # Test subroutines
        self.assertEqual('0A', self.test_data.hex(self.ecb['EBW010']['data']))
        self.assertEqual('00', self.test_data.hex(self.ecb['EBW011']['data']))
        self.assertEqual('0C', self.test_data.hex(self.ecb['EBW012']['data']))
        self.assertEqual('0D', self.test_data.hex(self.ecb['EBW013']['data']))

    def test_ts16_2(self):
        # Update state to 1.2, 2.2, 3.2, 4.2, 5.2, 7.1.2, 7.2.2, 7.3.2, 7.4.2
        self.i_ecb['EBW000']['data'] = b64encode(bytearray([0xC1, 0xC2, 0xC3, 0xC4])).decode()
        self.i_ecb['EBW004']['data'] = b64encode(bytearray([0xC1, 0xC2, 0xC3, 0xC5])).decode()
        self.i_ecb['EBW008']['data'] = b64encode(bytearray([0xC1])).decode()
        self.i_ecb['EBW009']['data'] = b64encode(bytearray([0x11])).decode()
        self.i_regs['R15'] = -10
        self.i_regs['R14'] = 23
        self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(2, self.output.regs['R0'])
        self.assertEqual(3, self.output.regs['R1'])
        self.assertEqual(2, self.output.regs['R2'])
        self.assertEqual(1, self.output.regs['R3'])
        self.assertEqual(2, self.output.regs['R4'])
        self.assertEqual(2, self.output.regs['R5'])
        self.assertEqual('0B', self.test_data.hex(self.ecb['EBW011']['data']))
        self.assertEqual('C2C2C2C2', self.test_data.hex(self.ecb['EBW020']['data']))
        self.assertEqual(0x33, self.output.regs['R7'])
        self.assertEqual('0001234C', self.test_data.hex(self.ecb['EBW024']['data']))
        self.assertEqual('0F', self.test_data.hex(self.ecb['EBW015']['data']))
        self.assertEqual('03', self.test_data.hex(self.ecb['EBW016']['data']))

    def test_ts16_3(self) -> None:
        # Update state to 3.3, 5.3
        self.i_regs['R15'] = 10
        self.i_ecb['EBW009']['data'] = b64encode(bytearray([0x10])).decode()
        self.tpf_server.run('TS16', self.test_data)
        self.assertEqual(3, self.output.regs['R2'])
        self.assertEqual(2, self.output.regs['R3'])
        self.assertEqual(3, self.output.regs['R5'])


if __name__ == '__main__':
    unittest.main()
