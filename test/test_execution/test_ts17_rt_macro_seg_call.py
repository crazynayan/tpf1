import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS


class RealTimeMacro(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.output = self.test_data.output
        self.output.add_all_reg_pointers(2)
        self.output.add_regs(['R5'])
        self.test_data.add_fields(['EBT000', 'EBW000'], 'EB0EB')

    def test_ts17(self):
        test_data = self.tpf_server.run('TS17', self.test_data)
        self.assertEqual('C100', test_data.output.reg_pointers['R1'])
        self.assertEqual('C200', test_data.output.reg_pointers['R2'])
        self.assertEqual('C300', test_data.output.reg_pointers['R3'])
        self.assertEqual('C4C4', test_data.output.reg_pointers['R4'])
        self.assertListEqual(['021014', '19000'], test_data.output.dumps)
        self.assertIn("MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR", test_data.output.messages)
        self.assertEqual(self.tpf_server.heap['TS17PDWK'], self.tpf_server.regs.get_value('R4'))
        self.assertEqual(1, len(self.tpf_server.detac_stack['2']))
        self.assertEqual(0, len(self.tpf_server.detac_stack['1']))

    def test_segment_call(self):
        # Flow is TS10 <-> TS01 -> TS02 -< TS10 => TS13
        test_data = self.tpf_server.run('TS10', self.test_data)
        # Check if OI EBT000,1 is executed (Proof of execution of TS01)
        self.assertEqual('01', test_data.get_field('EBT000'))
        # Check if BCTR R5,0 is executed (Proof of execution of TS02)
        self.assertEqual(-1, test_data.output.regs['R5'])
        # Check if MVC EBW000,EBT000 is executed (Proof of execution of TS13)
        self.assertEqual('01', test_data.get_field('EBW000'))


if __name__ == '__main__':
    unittest.main()
