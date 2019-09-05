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
        self.regs.set_bytes('R3', bytearray([0x12, 0x34, 0x56, 0x78]))
        self.assertEqual(bytearray([0x12, 0x34, 0x56, 0x78]), self.regs.R3)
        self.assertEqual(bytearray([0x12, 0x56]), self.regs.get_bytes_from_mask('R3', 10))
        self.regs.set_bytes_from_mask('R3', bytearray([0x85, 0x23]), 10)
        self.assertEqual(bytearray([0x85, 0x34, 0x23, 0x78]), self.regs.get_bytes('R3'))


if __name__ == '__main__':
    unittest.main()
