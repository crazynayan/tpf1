import unittest

from assembly.mac2_data_macro import macros
from config import config
from execution.ex5_execute import Execute
from test import TestDataUTS


class NonConditional1(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.output = self.test_data.output
        self.output.add_regs(['R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15'])
        aaa_fields = [('WA0BBR', 2), ('WA0QHR', 6), ('WA0TKK', 1), ('WA0TY1', 1)]
        self.aaa = self.test_data.add_core_with_len(aaa_fields, 'WA0AA')
        ecb_fields = [('EBW001', 6), ('EBW008', 6)]
        self.ecb = self.test_data.add_core_with_len(ecb_fields, 'EB0EB')
        ecb_fields = ['EBW000', 'EBW016', 'EBW017', 'EBW018']
        ecb_len = self.test_data.add_core(ecb_fields, 'EB0EB', output=True)
        self.ecb = {**self.ecb, **ecb_len}

    def test_ts14(self):
        self.tpf_server.run('TS14', self.test_data)
        aaa = config.AAA
        self.assertEqual(0xFFFFC1C1, self.output.get_unsigned_value('R2'))
        self.assertEqual('C1C1', self.test_data.hex(self.aaa['WA0BBR']['data']))
        self.assertEqual('00000000C1C1', self.test_data.hex(self.aaa['WA0QHR']['data']))
        self.assertEqual(2, self.output.regs['R3'])
        self.assertEqual('02', self.test_data.hex(self.aaa['WA0TKK']['data']))
        self.assertEqual(2, self.output.regs['R5'])
        self.assertEqual(-2, self.output.regs['R6'])
        self.assertEqual(4, self.output.regs['R7'])
        self.assertEqual(2, self.output.regs['R10'])
        self.assertEqual(0x00000100, self.output.regs['R4'])
        self.assertEqual(0x00000000, self.output.regs['R11'])
        self.assertEqual(-1, self.output.regs['R12'])
        self.assertEqual(config.AAA + macros['WA0AA'].evaluate('WA0TKK'), self.output.regs['R13'])
        self.assertEqual(config.AAA + macros['WA0AA'].evaluate('WA0DAR') + 1, self.output.regs['R14'])
        self.assertEqual(5, self.output.regs['R15'])
        self.assertEqual('02', self.test_data.hex(self.ecb['EBW000']['data']))
        self.assertEqual('40' * 6, self.test_data.hex(self.ecb['EBW001']['data']))
        self.assertEqual('00' * 6, self.test_data.hex(self.ecb['EBW008']['data']))
        self.assertTrue(self.tpf_server.vm.is_updated(config.ECB + 16, 6))
        self.assertFalse(self.tpf_server.vm.is_updated(config.ECB + 15, 1))
        self.assertEqual('42', self.test_data.hex(self.ecb['EBW016']['data']))
        self.assertEqual('40', self.test_data.hex(self.ecb['EBW017']['data']))
        self.assertEqual(f"{macros['WA0AA'].evaluate('#WA0GEN'):02X}", self.test_data.hex(self.aaa['WA0TY1']['data']))
        self.assertTrue(self.tpf_server.vm.is_updated_bit(aaa + 0x030, 0x80))
        self.assertFalse(self.tpf_server.vm.is_updated_bit(aaa + 0x030, 0x40))
        self.assertEqual(f"{0xFF - macros['WA0AA'].evaluate('#WA0GEN'):02X}",
                         self.test_data.hex(self.ecb['EBW018']['data']))


if __name__ == '__main__':
    unittest.main()
