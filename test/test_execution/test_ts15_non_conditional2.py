import unittest

from execution.ex5_execute import Execute
from firestore.test_data import TestData


class NonConditional2(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestData()
        self.output = self.test_data.output
        ecb_fields = [('EBW000', 4), ('EBW004', 2), ('EBW008', 12), ('EBW020', 12), ('EBW032', 6), ('EBW040', 8),
                      ('EBW048', 8), ('EBW056', 8), ('EBW064', 6)]
        self.ecb = self.test_data.add_core_with_len(ecb_fields, 'EB0EB')
        self.output.add_all_regs()

    def test_ts15(self):
        self.tpf_server.run('TS15', self.test_data)
        self.assertEqual(23, self.output.regs['R2'])
        self.assertEqual('00000017', self.ecb['EBW000'].hex)
        self.assertEqual(-2, self.output.regs['R3'])
        self.assertEqual('FF00', self.ecb['EBW004'].hex)
        self.assertEqual(0x40404040, self.output.regs['R15'])
        self.assertEqual(0xC1404040, self.output.get_unsigned_value('R0'))
        self.assertEqual(0x40C14040, self.output.regs['R1'])
        self.assertEqual('40404040C140404040C14040', self.ecb['EBW008'].hex)
        self.assertEqual('40404040C140404040C14040', self.ecb['EBW020'].hex)
        self.assertEqual('000000000002048C', self.ecb['EBW040'].hex)
        self.assertEqual(2048, self.output.regs['R4'])
        self.assertEqual('000000000012048C', self.ecb['EBW048'].hex)
        self.assertEqual(12048, self.output.regs['R5'])
        self.assertEqual(14096, self.output.regs['R6'])
        self.assertEqual('000000000014096C', self.ecb['EBW056'].hex)
        self.assertEqual('F0F1F4F0F9C6', self.ecb['EBW032'].hex)
        self.assertEqual('F0F1F4F0F9F6', self.ecb['EBW064'].hex)
        self.assertEqual(4, self.output.regs['R7'])
        self.assertEqual(22, self.output.regs['R11'] - self.output.regs['R8'])
        self.assertEqual(2, self.output.regs['R12'])


if __name__ == '__main__':
    unittest.main()
