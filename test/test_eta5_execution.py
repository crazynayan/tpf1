import unittest

from assembly.program import program
from config import config
from db.pnr import Pnr
from execution.execute import Execute
from utils.data_type import DataType


class Eta5Test(unittest.TestCase):
    def setUp(self) -> None:
        self.state = Execute()
        program.macros['EB0EB'].load()
        program.macros['WA0AA'].load()
        self.ebsw01 = program.macros['EB0EB'].symbol_table['EBSW01'].dsp
        self.ebrs01 = program.macros['EB0EB'].symbol_table['EBRS01'].dsp
        self.wa0et4 = program.macros['WA0AA'].symbol_table['WA0ET4'].dsp
        self.wa0et5 = program.macros['WA0AA'].symbol_table['WA0ET5'].dsp
        self.wa0any = program.macros['WA0AA'].symbol_table['#WA0ANY'].dsp
        Pnr.init_db()

    def test_no_name(self) -> None:
        self.state.run('ETA5', aaa=True)
        self.assertEqual("'NEED NAME IN PNR TO COMPLETE TRANSACTION'", self.state.message)

    def test_single_name(self) -> None:
        Pnr.add_names(config.AAAPNR, ['1ZAVERI/NAYAN MR'])
        self.state.run('ETA5', aaa=True)
        self.assertEqual(0xF0F0, self.state.vm.get_unsigned_value(config.ECB + 96, 2))
        self.assertEqual(1, self.state.vm.get_unsigned_value(config.ECB + 23, 1))

    def test_invalid_name(self) -> None:
        # Without number in party at start
        Pnr.add_names(config.AAAPNR, ['ZAVERI/NAYAN MR'])
        self.state.run('ETA5', aaa=True)
        self.assertIn('19000', self.state.dumps)
        self.assertEqual(1, self.state.regs.R1)

    def test_multiple_names(self) -> None:
        Pnr.add_names(config.AAAPNR, ['45ZAVERI', '54SHAH'])
        self.state.run('ETA5', aaa=True)
        self.assertEqual(0xF0F0, self.state.vm.get_unsigned_value(config.ECB + 96, 2))
        self.assertEqual(99, self.state.vm.get_unsigned_value(config.ECB + 23, 1))

    def test_too_many_names(self) -> None:
        Pnr.add_names(config.AAAPNR, ['45ZAVERI', '55SHAH'])
        self.state.run('ETA5', aaa=True)
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'", self.state.message)
        self.assertEqual(100, self.state.regs.R15)
        self.assertEqual(98, self.state.vm.get_unsigned_value(config.ECB + 52, 1))

    def test_WA0NAD(self) -> None:
        Pnr.add_names(config.AAAPNR, ['1ZAVERI/NAYAN MR'])
        wa0nad = program.macros['WA0AA'].symbol_table['#WA0NAD'].dsp
        self.state.setup = {'WA0AA': {'WA0ETG': bytearray([wa0nad])}}
        self.state.run('ETA5', aaa=True)
        self.assertEqual(0xF0F0, self.state.vm.get_unsigned_value(config.ECB + 96, 2))
        self.assertEqual(1, self.state.vm.get_unsigned_value(config.ECB + 23, 1))
        self.assertEqual(7, self.state.regs.R6)

    def test_WA0CDI(self) -> None:
        Pnr.add_names(config.AAAPNR, ['33ZAVERI'])
        wa0cdi = program.macros['WA0AA'].symbol_table['#WA0CDI'].dsp
        self.state.setup = {'WA0AA': {'WA0US4': bytearray([wa0cdi])}}
        self.state.run('ETA5', aaa=True)
        self.assertEqual(0xF0F0, self.state.vm.get_unsigned_value(config.ECB + 96, 2))
        self.assertEqual(33, self.state.vm.get_unsigned_value(config.ECB + 23, 1))
        self.assertEqual(60, self.state.regs.R6)

    def test_group_C(self) -> None:
        Pnr.add_names(config.AAAPNR, ['C/21VEENA WORLD', '2ZAVERI/NAYAN MR/PURVI MRS'])
        self.state.run('ETA5', aaa=True)
        self.assertEqual(0xF1F9, self.state.vm.get_unsigned_value(config.ECB + 96, 2))
        self.assertEqual(21, self.state.vm.get_unsigned_value(config.ECB + 23, 1))
        self.assertTrue(self.state.vm.all_bits_on(config.ECB + self.ebsw01, 0x10))
        self.assertTrue(self.state.vm.all_bits_on(config.ECB + 46, 0x80))
        self.assertEqual('C', DataType('X', bytes=self.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_group_Z(self) -> None:
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', '3SHAH'])
        self.state.run('ETA5', aaa=True)
        self.assertEqual(0xF2F2, self.state.vm.get_unsigned_value(config.ECB + 96, 2))
        self.assertEqual(25, self.state.vm.get_unsigned_value(config.ECB + 23, 1))
        self.assertTrue(self.state.vm.all_bits_on(config.ECB + self.ebsw01, 0x10))
        self.assertTrue(self.state.vm.all_bits_on(config.ECB + 46, 0x80))
        self.assertEqual('Z', DataType('X', bytes=self.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_invalid_type(self):
        Pnr.add_names(config.AAAPNR, ['K/13TOURS', '1ZAVERI'])
        self.state.run('ETA5', aaa=True)
        self.assertEqual(16, self.state.regs.R6)
        self.assertTrue(self.state.vm.all_bits_on(config.ECB + self.ebrs01, 0xC0))
        self.assertEqual('K', DataType('X', bytes=self.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_invalid_name_after_group(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', 'ZAVERI', '1SHAH'])
        self.state.run('ETA5', aaa=True)
        self.assertIn('19000', self.state.dumps)
        self.assertEqual(1, self.state.regs.R1)

    def test_group_overbooking(self):
        Pnr.add_names(config.AAAPNR, ['C/5TOURS', '11ZAVERI'])
        self.state.run('ETA5', aaa=True)
        self.assertTrue(self.state.vm.all_bits_on(self.state.regs.R1 + self.wa0et4, 0x20))
        ui2inc = program.macros['UI2PF'].symbol_table['UI2INC'].dsp
        ui2xui = program.macros['UI2PF'].symbol_table['#UI2XUI'].dsp
        ui2can = program.macros['UI2PF'].symbol_table['#UI2CAN'].dsp
        ui2nxt = program.macros['AASEQ'].symbol_table['#UI2NXT'].dsp
        ui2inc_bytes = bytearray([ui2xui + ui2can, ui2nxt, ui2nxt])
        self.assertEqual(ui2inc_bytes, self.state.vm.get_bytes(config.ECB + 48 + ui2inc, 3))
        self.assertTrue(self.state.vm.all_bits_off(self.state.regs.R1 + self.wa0et5, 0x02))
        self.assertTrue(self.state.vm.all_bits_on(self.state.regs.R1 + self.wa0et5, self.wa0any))
        self.assertTrue(self.state.vm.all_bits_on(config.ECB + self.ebrs01, 0x60))


if __name__ == '__main__':
    unittest.main()
