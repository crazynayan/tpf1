import unittest

from execution.ex0_regs_store import Registers, Storage
from utils.data_type import Register
from utils.errors import RegisterInvalidError


class RegistersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.regs = Registers()

    def test_registers(self):
        # Check set and get value
        self.regs.set_value(10, 'R1')
        self.assertEqual(0x0000000A, self.regs.R1)
        self.assertEqual(10, self.regs.get_value(Register('RG1')))
        self.regs.set_value(-1, Register('2'))
        self.assertEqual(-1, self.regs.R2)
        self.assertEqual(-1, self.regs.get_value('R2'))
        self.assertEqual(0xFFFFFFFF, self.regs.get_unsigned_value('R2'))
        # Check set and get bytes including from mask
        self.regs.set_bytes(bytearray([0x12, 0x34, 0x56, 0x78]), Register('R03'))
        self.assertEqual(bytearray([0x12, 0x34, 0x56, 0x78]), self.regs.get_bytes('R3'))
        self.assertEqual(bytearray([0x12, 0x56]), self.regs.get_bytes_from_mask(Register('R3'), 0b1010))
        self.regs.set_bytes_from_mask(bytearray([0x85, 0x23]), Register('R3'), 0b1010)
        self.assertEqual(bytearray([0x85, 0x34, 0x23, 0x78]), self.regs.get_bytes('R3'))
        self.regs.set_bytes_from_mask(bytearray([0x85, 0x23]), Register('RGB'), 0b0011)
        self.assertEqual(bytearray([0x85, 0x34, 0x85, 0x23]), self.regs.get_bytes('R3'))
        self.assertEqual(bytearray([0x23]), self.regs.get_bytes_from_mask(Register('3'), 0b0001))
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
        # Check double value
        self.regs.set_double_value(-3, Register('0'))
        self.assertEqual(-1, self.regs.R0)
        self.assertEqual(-3, self.regs.R1)
        # Check errors and exceptions
        self.assertRaises(RegisterInvalidError, self.regs.get_value, 'RAC')
        self.assertRaises(RegisterInvalidError, self.regs.get_address, 'R01', 0)
        self.assertRaises(RegisterInvalidError, self.regs.get_address, Register('R16'), 0)
        self.assertRaises(RegisterInvalidError, self.regs.get_address, Register('R0'), 0, '0')
        self.assertRaises(RegisterInvalidError, self.regs.get_address, Register('R0'), 0, Register('-1'))
        self.assertRaises(RegisterInvalidError, self.regs.next_reg, 'F1')
        self.assertRaises(RegisterInvalidError, self.regs.get_bytes, '-1')
        self.assertRaises(RegisterInvalidError, self.regs.get_bytes_from_mask, '1', 15)
        self.assertRaises(IndexError, self.regs.get_bytes_from_mask, 'R1', 0b10001)
        self.assertRaises(RegisterInvalidError, self.regs.set_bytes, bytearray([0x00] * 4), 23)
        self.assertRaises(ValueError, self.regs.set_bytes, bytearray([0x00] * 3), 'R9')
        self.assertRaises(RegisterInvalidError, self.regs.set_value, 0, '0')
        self.assertRaises(RegisterInvalidError, self.regs.set_bytes_from_mask, bytearray([0x00] * 4), 'R04', 0b1111)
        self.assertRaises(ValueError, self.regs.set_bytes_from_mask, bytearray([0x00] * 2), 'R9', 0b0111)
        self.assertRaises(IndexError, self.regs.set_bytes_from_mask, bytearray([0x00] * 2), 'R1', 0b10000)


class StorageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.regs = Registers()
        self.storage = Storage()

    def test_storage(self):
        # 1. Check allocate, get allocated address, nab, base_key, dsp
        block = self.storage.allocate()
        self.assertEqual(0x00010000, block)
        self.assertEqual(bytearray([0x00, 0x01, 0x00, 0x00]), self.storage.get_allocated_address())
        self.assertEqual(0x00011000, self.storage.nab)
        self.assertEqual('12345000', self.storage.base_key(0x12345678))
        self.assertEqual(0x678, self.storage.dsp(0x12345678))
        # 2. Check extend frames and _frame
        block = self.storage.allocate()
        r1 = Register('R1')
        self.regs.set_value(block, r1)
        base_r1 = self.storage.base_key(block)
        self.assertEqual(bytearray([0x00]), self.storage.get_bytes(self.regs.get_value(r1)))
        self.assertEqual(bytearray([0x00] * 2), self.storage.get_bytes(self.regs.get_address(r1, 30), 2))
        self.assertEqual(32, len(self.storage.frames[base_r1]))
        self.assertEqual(bytearray([0xFF] * 32), self.storage._frame[base_r1])
        # 3. Check get & set of bytes & value
        self.regs.set_value(self.storage.allocate(), 'R2')
        base_r2 = self.storage.base_key(self.regs.get_value('R2'))
        self.storage.set_bytes(bytearray([0xD5, 0xE9]), self.regs.R2 + 0x012, 2)
        self.assertEqual(bytearray([0x00, 0x00, 0xD5, 0xE9]), self.storage.get_bytes(self.regs.R2 + 0x010, 4))
        self.assertEqual(bytearray([0xE9]), self.storage.get_bytes(self.regs.R2 + 0x013))
        self.storage.set_value(0x23, self.regs.R2)
        self.assertEqual(0x00000023, self.storage.get_value(self.regs.R2))
        self.assertEqual(0x23, self.storage.get_value(self.regs.R2 + 3, 1))
        self.storage.set_value(0x35, self.regs.R2 + 4, 1)
        self.assertEqual(0x35, self.storage.get_value(self.regs.R2 + 4, 1))
        # 4. Check init
        self.assertTrue(self.storage.is_updated(self.regs.R2))
        self.assertFalse(self.storage.is_updated(self.regs.R2 + 5))
        # Just updating some bytes out of a set of bytes will still indicate that the set of bytes is NOT updated.
        self.assertFalse(self.storage.is_updated(self.regs.R2 + 6, 6))
        self.assertFalse(self.storage.is_updated(self.regs.R2 + 0x010, 4))
        self.assertTrue(self.storage.is_updated(self.regs.R2 + 0x012, 2))
        # 5. Check bits
        byte = self.regs.R2 + 5
        self.assertFalse(self.storage.all_bits_on(byte, 0x80))
        self.storage.or_bit(byte, 0x80)
        self.assertTrue(self.storage.all_bits_on(byte, 0x80))
        self.assertFalse(self.storage.all_bits_on(byte, 0x40))
        self.assertFalse(self.storage.all_bits_off(byte, 0x80))
        self.assertTrue(self.storage.all_bits_off(byte, 0x40))
        self.storage.and_bit(byte, 0xFF - 0x80)
        self.assertFalse(self.storage.all_bits_on(byte, 0x80))
        self.assertEqual(0x00, self.storage.frames[base_r2][5])
        self.assertEqual(0x7F, self.storage._frame[base_r2][5])
        # Just updating a bit out of a byte will still indicate that the byte is NOT updated.
        self.assertFalse(self.storage.is_updated(byte))
        self.assertTrue(self.storage.is_updated_bit(byte, 0x80))
        self.assertFalse(self.storage.is_updated_bit(byte, 0x40))
        # Just updating a bit out of a set of bits will still indicate that the set of bits is NOT updated.
        self.assertFalse(self.storage.is_updated_bit(byte, 0xC0))
        # 6. Check multiple bits
        byte = self.regs.R2 + 6
        self.storage.or_bit(byte, 0x0E)
        self.assertFalse(self.storage.all_bits_on(byte, 0x1C))
        self.assertFalse(self.storage.all_bits_off(byte, 0x1C))
        self.assertTrue(self.storage.all_bits_on(byte, 0x0C))
        self.assertFalse(self.storage.all_bits_off(byte, 0x0C))
        self.assertFalse(self.storage.all_bits_on(byte, 0x11))
        self.assertTrue(self.storage.all_bits_off(byte, 0x11))
        self.assertTrue(self.storage.all_bits_on(byte, 0x08))
        self.assertFalse(self.storage.all_bits_off(byte, 0x08))
        self.assertFalse(self.storage.all_bits_on(byte, 0x10))
        self.assertTrue(self.storage.all_bits_off(byte, 0x10))
        self.storage.or_bit(byte, 0x30)
        self.assertEqual(0x3E, self.storage.get_byte(byte))
        self.storage.and_bit(byte, 0xFF - 0x18)
        self.assertEqual(0x26, self.storage.get_byte(byte))
