import unittest

from v2.state import Registers, Storage
from v2.data_type import Register


class StateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.regs = Registers()
        self.storage = Storage()

    def test_registers(self):
        # Check set and get value
        self.regs.set_value(10, 'R1')
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x0A]), self.regs.R1)
        self.assertEqual(10, self.regs.get_value('R1'))
        self.regs.set_value(-1, 'R2')
        self.assertEqual(bytearray([0xFF, 0xFF, 0xFF, 0xFF]), self.regs.R2)
        self.assertEqual(-1, self.regs.get_value('R2'))
        # Check set and get bytes including from mask
        self.regs.set_bytes(bytearray([0x12, 0x34, 0x56, 0x78]), 'R3')
        self.assertEqual(bytearray([0x12, 0x34, 0x56, 0x78]), self.regs.R3)
        self.assertEqual(bytearray([0x12, 0x56]), self.regs.get_bytes_from_mask('R3', 0b1010))
        self.regs.set_bytes_from_mask(bytearray([0x85, 0x23]), 'R3', 0b1010)
        self.assertEqual(bytearray([0x85, 0x34, 0x23, 0x78]), self.regs.get_bytes('R3'))
        # Check next reg
        self.assertEqual('R7', self.regs.next_reg('R6'))
        self.assertEqual('R0', self.regs.next_reg('R15'))
        # Check get address
        self.regs.set_value(0x00001000, 'R9')
        self.regs.set_value(0x00001000, 'R0')
        self.regs.set_value(0x00000010, 'R4')
        self.assertEqual(0x00001234, self.regs.get_address(Register('R9'), 0x234))
        self.assertEqual(0x00000234, self.regs.get_address(Register('RAC'), 0x234))
        self.assertEqual(0x00001244, self.regs.get_address(Register('R9'), 0x234, Register('4')))
        self.assertEqual(0x00001234, self.regs.get_address(Register('REB'), 0x234, Register('0')))
        # Check errors and exceptions
        self.assertRaises(AttributeError, self.regs.get_value, 'RAC')
        self.assertRaises(AttributeError, self.regs.get_address, 'R1', 0)
        self.assertRaises(AttributeError, self.regs.get_address, Register('R16'), 0)
        self.assertRaises(AttributeError, self.regs.get_address, Register('R0'), 0, '0')
        self.assertRaises(AttributeError, self.regs.get_address, Register('R0'), 0, Register('-1'))
        self.assertRaises(AttributeError, self.regs.next_reg, 'F1')
        self.assertRaises(AttributeError, self.regs.get_bytes, '-1')
        self.assertRaises(AttributeError, self.regs.get_bytes_from_mask, '1', 15)
        self.assertRaises(IndexError, self.regs.get_bytes_from_mask, 'R1', 0b10001)
        self.assertRaises(AttributeError, self.regs.set_bytes, bytearray([0x00] * 4), 'REB')
        self.assertRaises(ValueError, self.regs.set_bytes, bytearray([0x00] * 3), 'R9')
        self.assertRaises(AttributeError, self.regs.set_value, 0, '0')
        self.assertRaises(AttributeError, self.regs.set_bytes_from_mask, bytearray([0x00] * 4), 'R04', 0b1111)
        self.assertRaises(ValueError, self.regs.set_bytes_from_mask, bytearray([0x00] * 2), 'R9', 0b0111)
        self.assertRaises(IndexError, self.regs.set_bytes_from_mask, bytearray([0x00] * 2), 'R1', 0b10000)

    def test_storage(self):
        pass


if __name__ == '__main__':
    unittest.main()
