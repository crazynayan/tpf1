import unittest

from config import config
from test.input_td import TD


class NonConditional2(unittest.TestCase):
    def setUp(self) -> None:
        self.state = TD.state
        self.state.init_run()

    def test_ts15(self):
        self.state.run('TS15')
        self.assertEqual(23, self.state.regs.R2)
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x17]), self.state.vm.get_bytes(config.ECB + 8, 4))
        self.assertEqual(-2, self.state.regs.R3)
        self.assertEqual(bytearray([0xFF, 0x00]), self.state.vm.get_bytes(config.ECB + 12, 2))
        self.assertEqual(0x40404040, self.state.regs.R15)
        self.assertEqual(0xC1404040, self.state.regs.get_unsigned_value('R0'))
        self.assertEqual(0x40C14040, self.state.regs.R1)
        self.assertEqual(0x40404040C140404040C14040, self.state.vm.get_value(config.ECB + 28, 12))
        self.assertEqual(0x000000000002048C, self.state.vm.get_value(config.ECB + 48, 8))
        self.assertEqual(2048, self.state.regs.R4)
        self.assertEqual(0x000000000012048C, self.state.vm.get_value(config.ECB + 56, 8))
        self.assertEqual(12048, self.state.regs.R5)
        self.assertEqual(14096, self.state.regs.R6)
        self.assertEqual(0x000000000014096C, self.state.vm.get_value(config.ECB + 64, 8))
        self.assertEqual(bytearray([0xF0, 0xF1, 0xF4, 0xF0, 0xF9, 0xC6]), self.state.vm.get_bytes(config.ECB + 40, 6))
        self.assertEqual(0xF0F1F4F0F9F6, self.state.vm.get_unsigned_value(config.ECB + 72, 6))
        self.assertEqual(4, self.state.regs.R7)
        self.assertEqual(22, self.state.regs.R11 - self.state.regs.R8)
        self.assertEqual(2, self.state.regs.R12)


if __name__ == '__main__':
    unittest.main()
