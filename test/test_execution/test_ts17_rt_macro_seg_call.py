import unittest

from config import config
from execution.ex5_execute import Execute


class RealTimeMacro(unittest.TestCase):
    def setUp(self) -> None:
        self.state = Execute()
        self.state.init_run()

    def test_ts17(self):
        self.state.run('TS17')
        self.assertEqual(0xC1, self.state.vm.get_unsigned_value(self.state.regs.get_value('R1'), 1))
        self.assertEqual(0xC2, self.state.vm.get_unsigned_value(self.state.regs.get_value('R2'), 1))
        self.assertEqual(0xC3, self.state.vm.get_unsigned_value(self.state.regs.get_value('R3'), 1))
        self.assertEqual(0xC4C4, self.state.vm.get_unsigned_value(self.state.regs.get_value('R4'), 2))
        self.assertListEqual(['021014', '19000'], self.state.dumps)
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'", self.state.message)
        self.assertEqual(self.state.heap['TS17PDWK'], self.state.regs.get_value('R4'))
        self.assertEqual(1, len(self.state.detac_stack['2']))
        self.assertEqual(0, len(self.state.detac_stack['1']))

    def test_segment_call(self):
        # Flow is TS10 <-> TS01 -> TS02 -< TS10 => TS13
        self.state.run('TS10')
        # Check if OI EBT000,1 is executed (Proof of execution of TS01)
        self.assertTrue(self.state.vm.all_bits_on(config.ECB + 0x70, 0x01))
        # Check if BCTR R5,0 is executed (Proof of execution of TS02)
        self.assertEqual(-1, self.state.regs.get_value('R5'))
        # Check if MVC EBW000,EBT000 is executed (Proof of execution of TS13)
        self.assertEqual(0x01, self.state.vm.get_value(config.ECB + 8, 1))


if __name__ == '__main__':
    unittest.main()
