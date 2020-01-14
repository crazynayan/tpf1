import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS


class NonConditional2(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.output = self.test_data.output
        ecb_fields = [('EBW000', 4), ('EBW004', 2), ('EBW008', 12), ('EBW020', 12), ('EBW032', 6), ('EBW040', 8),
                      ('EBW048', 8), ('EBW056', 8), ('EBW064', 6)]
        self.ecb = self.test_data.add_fields(ecb_fields, 'EB0EB')
        self.output.add_all_regs()

    def test_ts15(self):
        test_data = self.tpf_server.run('TS15', self.test_data)
        self.assertEqual(23, test_data.output.regs['R2'])
        self.assertEqual('00000017', test_data.field('EBW000'))
        self.assertEqual(-2, test_data.output.regs['R3'])
        self.assertEqual('FF00', test_data.field('EBW004'))
        self.assertEqual(0x40404040, test_data.output.regs['R15'])
        self.assertEqual(0xC1404040, test_data.output.get_unsigned_value('R0'))
        self.assertEqual(0x40C14040, test_data.output.regs['R1'])
        self.assertEqual('40404040C140404040C14040', test_data.field('EBW008'))
        self.assertEqual('40404040C140404040C14040', test_data.field('EBW020'))
        self.assertEqual('000000000002048C', test_data.field('EBW040'))
        self.assertEqual(2048, test_data.output.regs['R4'])
        self.assertEqual('000000000012048C', test_data.field('EBW048'))
        self.assertEqual(12048, test_data.output.regs['R5'])
        self.assertEqual(14096, test_data.output.regs['R6'])
        self.assertEqual('000000000014096C', test_data.field('EBW056'))
        self.assertEqual('F0F1F4F0F9C6', test_data.field('EBW032'))
        self.assertEqual('F0F1F4F0F9F6', test_data.field('EBW064'))
        self.assertEqual(4, test_data.output.regs['R7'])
        # self.assertEqual(22, test_data.output.regs['R11'] - self.output.regs['R8'])
        self.assertEqual(2, test_data.output.regs['R12'])


if __name__ == '__main__':
    unittest.main()
