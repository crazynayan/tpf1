import unittest

from assembly.program import program
from config import config
from db.pnr import Pnr
from execution.execute import Execute
from utils.data_type import DataType

program.macros['EB0EB'].load()
program.macros['WA0AA'].load()
program.macros['UI2PF'].load()


class T:
    state: Execute = Execute()
    ebsw01 = program.macros['EB0EB'].symbol_table['EBSW01'].dsp
    ebrs01 = program.macros['EB0EB'].symbol_table['EBRS01'].dsp
    wa0et4 = program.macros['WA0AA'].symbol_table['WA0ET4'].dsp
    wa0et5 = program.macros['WA0AA'].symbol_table['WA0ET5'].dsp
    wa0pty = program.macros['WA0AA'].symbol_table['WA0PTY'].dsp
    wa0ext = program.macros['WA0AA'].symbol_table['WA0EXT'].dsp
    wa0pn2 = program.macros['WA0AA'].symbol_table['#WA0PN2'].dsp
    wa0any = program.macros['WA0AA'].symbol_table['#WA0ANY'].dsp
    wa0tty = program.macros['WA0AA'].symbol_table['#WA0TTY'].dsp
    ui2cnn = program.macros['UI2PF'].symbol_table['UI2CNN'].dsp
    ui2097 = program.macros['UI2PF'].symbol_table['#UI2097'].dsp
    ui2098 = program.macros['UI2PF'].symbol_table['#UI2098'].dsp
    ui2214 = program.macros['UI2PF'].symbol_table['#UI2214'].dsp


class NameSuccessETAW(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_single_name_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['1ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(1, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(T.ui2214, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))

    def test_multiple_names_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['45ZAVERI', '54SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_WA0NAD_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['1ZAVERI', '3SHAH'])
        T.wa0nad = program.macros['WA0AA'].symbol_table['#WA0NAD'].dsp
        T.state.setup = {'WA0AA': {'WA0ETG': bytearray([T.wa0nad])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(4, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(4, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(7, T.state.regs.R6)

    def test_WA0CDI_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['33ZAVERI'])
        T.wa0cdi = program.macros['WA0AA'].symbol_table['#WA0CDI'].dsp
        T.state.setup = {'WA0AA': {'WA0US4': bytearray([T.wa0cdi])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        T.state.run('ETA5', aaa=True)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(33, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(33, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(60, T.state.regs.R6)

    def test_group_C_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['C/21TOURS', '2ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF1F9, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(21, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(21, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebsw01, 0x10))
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + 46, 0x80))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_group_Z_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', '3SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF2F2, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(25, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(25, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebsw01, 0x10))
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + 46, 0x80))
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_group_C_not_at_start_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['10ZAVERI', 'C/21TOURS', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF1F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)
        self.assertEqual(21, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(21, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_pn2_on_group_C_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['C/99W/TOURS', '3SHAH'])
        T.state.setup = {'WA0AA': {'WA0UB1': bytearray([T.wa0pn2])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(9, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(9, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_pn2_on_group_Z_ETAW(self):
        # T.wa0PN2 OFF behaves the same way
        Pnr.add_names(config.AAAPNR, ['Z/99W/SABRE', '3SHAH'])
        T.state.setup = {'WA0AA': {'WA0UB1': bytearray([T.wa0pn2])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF9F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_pn2_off_group_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['C/99W/TOURS', '3SHAH'])
        T.state.setup = {'WA0AA': {'WA0UB1': bytearray([0x00])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF9F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_infant_with_adults_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['2ZAVERI', 'I/1ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(3, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(3, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(1, T.state.vm.get_byte(config.ECB + 18))

    def test_multiple_infants_with_less_adults_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['44ZAVERI', 'I/33ZAVERI', 'I/22SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(55, T.state.vm.get_byte(config.ECB + 18))

    def test_infant_only_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['I/3ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F3, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(3, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(3, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(3, T.state.vm.get_byte(config.ECB + 18))

    def test_infant_at_start_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['I/33ZAVERI', '44ZAVERI', 'I/22SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(55, T.state.vm.get_byte(config.ECB + 18))

    def test_infant_with_group_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['Z/21SABRE', '3ZAVERI', 'I/1ZAVERI', '4SHAH', 'I/2SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF1F4, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(24, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(24, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(3, T.state.vm.get_byte(config.ECB + 18))

    def test_infant_at_start_with_group_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '4SHAH', 'I/2SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF1F8, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(32, T.state.vm.get_byte(config.ECB + 23))
        self.assertEqual(32, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(7, T.state.vm.get_byte(config.ECB + 18))


class NameFailETK1(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_no_name_tty_ETK1(self) -> None:
        T.state.setup = {'WA0AA': {'WA0ET4': bytearray([T.wa0tty])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(0, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0x60))
        self.assertEqual(33, T.state.regs.R6)

    def test_too_many_names_tty_ETK1(self) -> None:
        Pnr.add_names(config.AAAPNR, ['45ZAVERI', '55SHAH'])
        T.state.setup = {'WA0AA': {'WA0ET4': bytearray([T.wa0tty])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(100, T.state.regs.R15)
        self.assertEqual(T.ui2098, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual(33, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0x60))

    def test_group_overbooking_tty_ETK1(self):
        Pnr.add_names(config.AAAPNR, ['Z/15TOURS', '11ZAVERI', '5SHAH'])
        T.state.setup = {'WA0AA': {'WA0ET4': bytearray([T.wa0tty])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(33, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0x60))

    def test_multiple_groups_tty_C_ETK1(self):
        Pnr.add_names(config.AAAPNR, ['C/25SABRE', 'C/21TOURS', '1SHAH'])
        T.state.setup = {'WA0AA': {'WA0ET4': bytearray([T.wa0tty])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(T.ui2097, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual(33, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0x60))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_multiple_groups_tty_Z_ETK1(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', 'Z/21TOURS', '1SHAH'])
        T.state.setup = {'WA0AA': {'WA0ET4': bytearray([T.wa0tty])}}
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(T.ui2098, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0xC0))
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_invalid_type_ETK1(self):
        Pnr.add_names(config.AAAPNR, ['K/13TOURS', '1ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0xC0))
        self.assertEqual('K', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_group_Z_not_at_start_ETK1(self):
        # It will give the same error if number of party is mentioned in Z/
        Pnr.add_names(config.AAAPNR, ['3ZAVERI', 'Z/SABRE', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0xC0))
        self.assertEqual(0x00, T.state.vm.get_byte(config.ECB + 22))

    def test_multiple_groups_Z_ETK1(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', 'Z/21TOURS', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0xC0))
        # This is the first 'Z'
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)


class NameFailETA5(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_no_name_ETA5420(self) -> None:
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('ETA5420.7', label)
        self.assertEqual("'NEED NAME IN PNR TO COMPLETE TRANSACTION'", T.state.message)

    def test_too_many_names_ETA5430(self) -> None:
        Pnr.add_names(config.AAAPNR, ['45ZAVERI', '55SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('ETA5430', label)
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'", T.state.message)
        self.assertEqual(100, T.state.regs.R15)
        self.assertEqual(T.ui2098, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))

    def test_too_many_infants_ETA5430(self) -> None:
        Pnr.add_names(config.AAAPNR, ['45ZAVERI', 'I/55ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('ETA5430', label)
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'", T.state.message)
        self.assertEqual(100, T.state.regs.R15)
        self.assertEqual(T.ui2098, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))


class NameFailUIO1(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_group_overbooking_UIO1(self):
        Pnr.add_names(config.AAAPNR, ['C/5TOURS', '11ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$UIO1$$.1', label)
        self.assertTrue(T.state.vm.all_bits_on(T.state.regs.R1 + T.wa0et4, 0x20))
        ui2inc = program.macros['UI2PF'].symbol_table['UI2INC'].dsp
        ui2xui = program.macros['UI2PF'].symbol_table['#UI2XUI'].dsp
        ui2can = program.macros['UI2PF'].symbol_table['#UI2CAN'].dsp
        ui2nxt = program.macros['AASEQ'].symbol_table['#UI2NXT'].dsp
        ui2inc_bytes = bytearray([ui2xui + ui2can, ui2nxt, ui2nxt])
        self.assertEqual(ui2inc_bytes, T.state.vm.get_bytes(config.ECB + 48 + ui2inc, 3))
        self.assertTrue(T.state.vm.all_bits_off(T.state.regs.R1 + T.wa0et5, 0x02))
        self.assertTrue(T.state.vm.all_bits_on(T.state.regs.R1 + T.wa0et5, T.wa0any))
        self.assertEqual(T.ui2214, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertTrue(T.state.vm.all_bits_on(config.ECB + T.ebrs01, 0x60))

    def test_multiple_groups_C_UIO1(self):
        Pnr.add_names(config.AAAPNR, ['C/25SABRE', 'C/21TOURS', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$UIO1$$.1', label)
        self.assertTrue(T.state.vm.all_bits_on(T.state.regs.R1 + T.wa0et5, T.wa0any))
        self.assertEqual(T.ui2097, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)


class NameFailETA2(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_invalid_name_ETA2(self) -> None:
        # Without number in party at start
        Pnr.add_names(config.AAAPNR, ['ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA2$$.1', label)
        self.assertIn('19000', T.state.dumps)
        self.assertEqual(1, T.state.regs.R1)

    def test_invalid_name_after_group_ETA2(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', 'ZAVERI', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA2$$.1', label)
        self.assertIn('19000', T.state.dumps)
        self.assertEqual(1, T.state.regs.R1)

    def test_invalid_infant_ETA2(self) -> None:
        Pnr.add_names(config.AAAPNR, ['I/ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA2$$.1', label)
        self.assertIn('19000', T.state.dumps)
        self.assertEqual(1, T.state.regs.R1)

    def test_invalid_infant_after_adult_ETA2(self) -> None:
        Pnr.add_names(config.AAAPNR, ['1ZAVERI', 'I/ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA2$$.1', label)
        self.assertIn('19000', T.state.dumps)
        self.assertEqual(1, T.state.regs.R1)

    def test_invalid_infant_after_group_ETA2(self) -> None:
        Pnr.add_names(config.AAAPNR, ['C/21TOURS', 'I/ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA2$$.1', label)
        self.assertIn('19000', T.state.dumps)
        self.assertEqual(1, T.state.regs.R1)


class NameException(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_invalid_group_at_start_Exception(self):
        # Both C/ and Z/ will give an exception.
        # I/ will NOT give an exception.
        Pnr.add_names(config.AAAPNR, ['Z/SABRE', '1ZAVERI'])
        self.assertRaises(ValueError, T.state.run, 'ETA5', True)
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)

    def test_invalid_group_C_not_at_start_Exception(self):
        # Preceding adult for C/  will give an exception.
        # Preceding adult for Z/ will NOT give an exception.
        Pnr.add_names(config.AAAPNR, ['1ZAVERI', 'C/TOURS'])
        self.assertRaises(ValueError, T.state.run, 'ETA5', True)
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(config.ECB + 22)).decode)


if __name__ == '__main__':
    unittest.main()
