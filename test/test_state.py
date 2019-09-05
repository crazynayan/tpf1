import unittest

from v2.state import Registers


class StateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.regs = Registers()

    def test_registers(self):
        self.regs.set_value('R1', 10)
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x0A]), self.regs.R1)
        self.assertEqual(10, self.regs.get_value('R1'))
        self.regs.set_value('R2', -1)
        self.assertEqual(bytearray([0xFF, 0xFF, 0xFF, 0xFF]), self.regs.R2)
        self.assertRaises(AttributeError, self.regs.get_value, 'RAC')
        self.assertRaises(AttributeError, self.regs.set_value, '0', 0)


if __name__ == '__main__':
    unittest.main()
