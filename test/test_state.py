import unittest

from config import config
from v2.data_type import Register
from v2.execute import Execute
from v2.segment import Program
from v2.state import Registers, Storage


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
        # Check errors and exceptions
        self.assertRaises(AttributeError, self.regs.get_value, 'RAC')
        self.assertRaises(AttributeError, self.regs.get_address, 'R01', 0)
        self.assertRaises(AttributeError, self.regs.get_address, Register('R16'), 0)
        self.assertRaises(AttributeError, self.regs.get_address, Register('R0'), 0, '0')
        self.assertRaises(AttributeError, self.regs.get_address, Register('R0'), 0, Register('-1'))
        self.assertRaises(AttributeError, self.regs.next_reg, 'F1')
        self.assertRaises(AttributeError, self.regs.get_bytes, '-1')
        self.assertRaises(AttributeError, self.regs.get_bytes_from_mask, '1', 15)
        self.assertRaises(IndexError, self.regs.get_bytes_from_mask, 'R1', 0b10001)
        self.assertRaises(AttributeError, self.regs.set_bytes, bytearray([0x00] * 4), 23)
        self.assertRaises(ValueError, self.regs.set_bytes, bytearray([0x00] * 3), 'R9')
        self.assertRaises(AttributeError, self.regs.set_value, 0, '0')
        self.assertRaises(AttributeError, self.regs.set_bytes_from_mask, bytearray([0x00] * 4), 'R04', 0b1111)
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


class StateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.state = Execute(Program())

    def test_ts14(self):
        self.state.seg_name = 'TS14'
        self.state.run()
        self.assertListEqual(list(), self.state.global_program.segments[self.state.seg_name].errors)
        self.assertListEqual(list(), self.state.errors)
        self.assertEqual(0x00012000, self.state.regs.get_value('R1'))
        self.assertEqual(0xFFFFC1C1 - 0x100000000, self.state.regs.get_value('R2'))
        self.assertEqual(bytearray([0xC1, 0xC1]), self.state.vm.get_bytes(0x00012344, 2))
        self.assertEqual(0x0000C1C10000, self.state.vm.get_value(0x00012342, 6))
        self.assertEqual(2, self.state.regs.get_value('R3'))
        self.assertEqual(0x02, self.state.vm.get_value(0x0001203F, 1))
        self.assertEqual(2, self.state.regs.get_value('R5'))
        self.assertEqual(-2, self.state.regs.get_value('R6'))
        self.assertEqual(4, self.state.regs.get_value('R7'))
        self.assertEqual(2, self.state.regs.get_value('R10'))
        self.assertEqual(0x00000100, self.state.regs.get_value('R4'))
        self.assertEqual(0x00000000, self.state.regs.get_value('R11'))
        self.assertEqual(-1, self.state.regs.get_value('R12'))
        self.assertEqual(0x0001203F, self.state.regs.get_value('R13'))
        self.assertEqual(0x00012041, self.state.regs.get_value('R14'))
        self.assertEqual(5, self.state.regs.get_value('R15'))
        self.assertEqual(bytearray([0x02]), self.state.vm.get_bytes(config.ECB + 8))
        self.assertEqual(bytearray([0x40] * 6), self.state.vm.get_bytes(config.ECB + 9, 6))
        self.assertEqual(bytearray([0x00] * 6), self.state.vm.get_bytes(config.ECB + 16, 6))
        self.assertTrue(self.state.vm.is_updated(config.ECB + 16, 6))
        self.assertFalse(self.state.vm.is_updated(config.ECB + 15, 1))
        self.assertEqual(0x42, self.state.vm.get_value(config.ECB + 24, 1))
        self.assertEqual(0x40, self.state.vm.get_value(config.ECB + 25, 1))
        self.assertEqual(0x80, self.state.vm.get_byte(0x00012030))
        self.assertTrue(self.state.vm.is_updated_bit(0x00012030, 0x80))
        self.assertFalse(self.state.vm.is_updated_bit(0x00012030, 0x40))

    def test_ts15(self):
        self.state.seg_name = 'TS15'
        self.state.run()
        self.assertListEqual(list(), self.state.global_program.segments[self.state.seg_name].errors)
        self.assertListEqual(list(), self.state.errors)
        self.assertEqual(23, self.state.regs.get_value('R2'))
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x17]), self.state.vm.get_bytes(config.ECB + 8, 4))
        self.assertEqual(-2, self.state.regs.get_value('R3'))
        self.assertEqual(bytearray([0xFF, 0x00]), self.state.vm.get_bytes(config.ECB + 12, 2))
        self.assertEqual(0x40404040, self.state.regs.get_value('R15'))
        self.assertEqual(0xC1404040 - 0x100000000, self.state.regs.get_value('R0'))
        self.assertEqual(0x40C14040, self.state.regs.get_value('R1'))
        self.assertEqual(0x40404040C140404040C14040, self.state.vm.get_value(config.ECB + 28, 12))
        self.assertEqual(0x000000000002048C, self.state.vm.get_value(config.ECB + 48, 8))
        self.assertEqual(2048, self.state.regs.get_value('R4'))
        self.assertEqual(0x000000000012048C, self.state.vm.get_value(config.ECB + 56, 8))
        self.assertEqual(12048, self.state.regs.get_value('R5'))
        self.assertEqual(14096, self.state.regs.get_value('R6'))
        self.assertEqual(0x000000000014096C, self.state.vm.get_value(config.ECB + 64, 8))
        self.assertEqual(bytearray([0xF0, 0xF1, 0xF4, 0xF0, 0xF9, 0xC6]), self.state.vm.get_bytes(config.ECB + 40, 6))
        self.assertEqual(bytearray([0xF0, 0xF1, 0xF4, 0xF0, 0xF9, 0xF6]), self.state.vm.get_bytes(config.ECB + 72, 6))


if __name__ == '__main__':
    unittest.main()
