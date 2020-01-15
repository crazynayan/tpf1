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
        aaa_fields = [('WA0BBR', 2), ('WA0QHR', 6), 'WA0TKK', 'WA0TY1']
        self.test_data.add_fields(aaa_fields, 'WA0AA')
        ecb_fields = [('EBW001', 6), ('EBW008', 6), 'EBW000', 'EBW016', 'EBW017', 'EBW018']
        self.test_data.add_fields(ecb_fields, 'EB0EB')

    def test_ts14(self):
        test_data = self.tpf_server.run('TS14', self.test_data)
        aaa = config.AAA
        self.assertEqual(0xFFFFC1C1, test_data.output.get_unsigned_value('R2'))
        self.assertEqual('C1C1', test_data.get_field('WA0BBR'))
        self.assertEqual('00000000C1C1', test_data.get_field('WA0QHR'))
        self.assertEqual(2, test_data.output.regs['R3'])
        self.assertEqual('02', test_data.get_field('WA0TKK'))
        self.assertEqual(2, test_data.output.regs['R5'])
        self.assertEqual(-2, test_data.output.regs['R6'])
        self.assertEqual(4, test_data.output.regs['R7'])
        self.assertEqual(2, test_data.output.regs['R10'])
        self.assertEqual(0x00000100, test_data.output.regs['R4'])
        self.assertEqual(0x00000000, test_data.output.regs['R11'])
        self.assertEqual(-1, test_data.output.regs['R12'])
        self.assertEqual(config.AAA + macros['WA0AA'].evaluate('WA0TKK'), test_data.output.regs['R13'])
        self.assertEqual(config.AAA + macros['WA0AA'].evaluate('WA0DAR') + 1, test_data.output.regs['R14'])
        self.assertEqual(5, test_data.output.regs['R15'])
        self.assertEqual('02', test_data.get_field('EBW000'))
        self.assertEqual('40' * 6, test_data.get_field('EBW001'))
        self.assertEqual('00' * 6, test_data.get_field('EBW008'))
        self.assertTrue(self.tpf_server.vm.is_updated(config.ECB + 16, 6))
        self.assertFalse(self.tpf_server.vm.is_updated(config.ECB + 15, 1))
        self.assertEqual('42', test_data.get_field('EBW016'))
        self.assertEqual('40', test_data.get_field('EBW017'))
        self.assertEqual(f"{macros['WA0AA'].evaluate('#WA0GEN'):02X}", test_data.get_field('WA0TY1'))
        self.assertTrue(self.tpf_server.vm.is_updated_bit(aaa + 0x030, 0x80))
        self.assertFalse(self.tpf_server.vm.is_updated_bit(aaa + 0x030, 0x40))
        self.assertEqual(f"{0xFF - macros['WA0AA'].evaluate('#WA0GEN'):02X}",
                         test_data.get_field('EBW018'))


if __name__ == '__main__':
    unittest.main()
