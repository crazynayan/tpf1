import unittest

from config import config
from test.input_td import TD


class NonConditional1(unittest.TestCase):
    def setUp(self) -> None:
        self.state = TD.state
        self.state.init_run()

    def test_ts14(self):
        self.state.run('TS14')
        aaa = self.state.regs.get_value('R1')
        self.assertEqual(0xFFFFC1C1 - 0x100000000, self.state.regs.get_value('R2'))
        self.assertEqual(bytearray([0xC1, 0xC1]), self.state.vm.get_bytes(aaa + 0x344, 2))
        self.assertEqual(0x0000C1C10000, self.state.vm.get_value(aaa + 0x342, 6))
        self.assertEqual(2, self.state.regs.get_value('R3'))
        self.assertEqual(0x02, self.state.vm.get_value(aaa + 0x03F, 1))
        self.assertEqual(2, self.state.regs.get_value('R5'))
        self.assertEqual(-2, self.state.regs.get_value('R6'))
        self.assertEqual(4, self.state.regs.get_value('R7'))
        self.assertEqual(2, self.state.regs.get_value('R10'))
        self.assertEqual(0x00000100, self.state.regs.get_value('R4'))
        self.assertEqual(0x00000000, self.state.regs.get_value('R11'))
        self.assertEqual(-1, self.state.regs.get_value('R12'))
        self.assertEqual(aaa + 0x03F, self.state.regs.get_value('R13'))
        self.assertEqual(aaa + 0x041, self.state.regs.get_value('R14'))
        self.assertEqual(5, self.state.regs.get_value('R15'))
        self.assertEqual(bytearray([0x02]), self.state.vm.get_bytes(config.ECB + 8))
        self.assertEqual(bytearray([0x40] * 6), self.state.vm.get_bytes(config.ECB + 9, 6))
        self.assertEqual(bytearray([0x00] * 6), self.state.vm.get_bytes(config.ECB + 16, 6))
        self.assertTrue(self.state.vm.is_updated(config.ECB + 16, 6))
        self.assertFalse(self.state.vm.is_updated(config.ECB + 15, 1))
        self.assertEqual(0x42, self.state.vm.get_value(config.ECB + 24, 1))
        self.assertEqual(0x40, self.state.vm.get_value(config.ECB + 25, 1))
        self.assertEqual(0x80, self.state.vm.get_byte(aaa + 0x030))
        self.assertTrue(self.state.vm.is_updated_bit(aaa + 0x030, 0x80))
        self.assertFalse(self.state.vm.is_updated_bit(aaa + 0x030, 0x40))


if __name__ == '__main__':
    unittest.main()
