import unittest

from config import config
from utils.test_data import T


class Conditional(unittest.TestCase):
    def setUp(self) -> None:
        self.state = T.state
        self.state.init_run()

    def test_ts16(self):
        self.state.run('TS16')
        # Default state is 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1.1, 7.2.1, 7.3.1, 7.4.1
        self.assertEqual(1, self.state.regs.get_value('R0'))
        self.assertEqual(2, self.state.regs.get_value('R1'))
        self.assertEqual(1, self.state.regs.get_value('R2'))
        self.assertEqual(1, self.state.regs.get_value('R3'))
        self.assertEqual(1, self.state.regs.get_value('R4'))
        self.assertEqual(1, self.state.regs.get_value('R5'))
        self.assertEqual(0xC2C2C200, self.state.vm.get_unsigned_value(config.ECB + 28))
        self.assertEqual(0x32, self.state.regs.get_value('R7'))
        self.assertEqual(0x0000123C, self.state.vm.get_unsigned_value(config.ECB + 32))
        self.assertEqual(16, self.state.vm.get_unsigned_value(config.ECB + 23, 1))
        self.assertEqual(2, self.state.vm.get_unsigned_value(config.ECB + 24, 1))
        # Test subroutines
        self.assertEqual(10, self.state.vm.get_value(config.ECB + 18, 1))
        self.assertEqual(0, self.state.vm.get_value(config.ECB + 19, 1))
        self.assertEqual(12, self.state.vm.get_value(config.ECB + 20, 1))
        self.assertEqual(13, self.state.vm.get_value(config.ECB + 21, 1))
        # Update state to 1.2, 2.2, 3.2, 4.2, 5.2, 7.1.2, 7.2.2, 7.3.2, 7.4.2
        self.state.vm.set_bytes(bytearray([0xC1, 0xC2, 0xC3, 0xC4]), config.ECB + 8, 4)
        self.state.vm.set_bytes(bytearray([0xC1, 0xC2, 0xC3, 0xC5]), config.ECB + 12, 4)
        self.state.vm.set_bytes(bytearray([0xC1]), config.ECB + 16)
        self.state.regs.set_value(-10, 'R15')
        self.state.regs.set_value(23, 'R14')
        self.state.vm.set_bytes(bytearray([0x11]), config.ECB + 17)
        self.state.run()
        self.assertEqual(2, self.state.regs.get_value('R0'))
        self.assertEqual(3, self.state.regs.get_value('R1'))
        self.assertEqual(2, self.state.regs.get_value('R2'))
        self.assertEqual(1, self.state.regs.get_value('R3'))
        self.assertEqual(2, self.state.regs.get_value('R4'))
        self.assertEqual(2, self.state.regs.get_value('R5'))
        self.assertEqual(11, self.state.vm.get_value(config.ECB + 19, 1))
        self.assertEqual(0xC2C2C2C2, self.state.vm.get_unsigned_value(config.ECB + 28))
        self.assertEqual(0x33, self.state.regs.get_value('R7'))
        self.assertEqual(0x0001234C, self.state.vm.get_unsigned_value(config.ECB + 32))
        self.assertEqual(15, self.state.vm.get_unsigned_value(config.ECB + 23, 1))
        self.assertEqual(3, self.state.vm.get_unsigned_value(config.ECB + 24, 1))
        # Update state to 3.3, 5.3
        self.state.regs.set_value(10, 'R15')
        self.state.vm.set_bytes(bytearray([0x10]), config.ECB + 17)
        self.state.run()
        self.assertEqual(3, self.state.regs.get_value('R2'))
        self.assertEqual(2, self.state.regs.get_value('R3'))
        self.assertEqual(3, self.state.regs.get_value('R5'))
        self.state.run()


if __name__ == '__main__':
    unittest.main()
