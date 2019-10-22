import unittest

from assembly2.mac2_data_macro import macros
from config import config
from db.pnr import Pnr
from db.tpfdf import Tpfdf
from utils.data_type import DataType
from utils.errors import PackExecutionError
from utils.test_data import T


class NameSuccessETAW(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_single_name_wa0pty_no_match_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['1ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(1, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(T.ui2214, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))

    def test_multiple_names_wa0pty_match_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['45ZAVERI', '54SHAH'])
        T.state.setup.aaa['WA0PTY'] = bytearray([99])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(T.ui2214, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))

    def test_WA0NAD_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['1ZAVERI', '3SHAH'])
        T.wa0nad = macros['WA0AA'].evaluate('#WA0NAD')
        T.state.setup.aaa['WA0ETG'] = bytearray([T.wa0nad])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(4, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(4, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertTrue(T.state.vm.all_bits_off(T.state.regs.R1 + T.wa0etg, T.wa0nad))
        self.assertEqual(7, T.state.regs.R6)           # Call to ETK2 with R6=7 will ensure Name association is deleted

    def test_WA0CDI_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['33ZAVERI'])
        T.wa0cdi = macros['WA0AA'].evaluate('#WA0CDI')
        T.state.setup.aaa['WA0US4'] = bytearray([T.wa0cdi])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        T.state.run('ETA5', aaa=True)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(33, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(33, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(60, T.state.regs.R6)

    def test_group_C_ETAW(self) -> None:
        Pnr.add_names(config.AAAPNR, ['C/21TOURS', '2ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(0xF1F9, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(21, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(21, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertTrue(T.state.vm.all_bits_on(T.ebsw01, 0x10))
        self.assertTrue(T.state.vm.all_bits_on(T.ebw000 + 38, 0x80))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_group_Z_ETAW_wa0pyt_no_match(self) -> None:
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', '3SHAH'])
        T.state.setup.aaa['WA0PTY'] = bytearray([3])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(0xF2F2, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(25, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(25, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertTrue(T.state.vm.all_bits_on(T.ebsw01, 0x10))
        self.assertTrue(T.state.vm.all_bits_on(T.ebw000 + 38, 0x80))
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_group_C_not_at_start_wa0pty_history_no_match_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['10ZAVERI', 'C/21TOURS', '1SHAH'])
        T.state.setup.aaa['WA0PTY'] = bytearray([0xE3])  # 99 = 0x63 with bit0 on is 0xE3
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(0xF1F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)
        self.assertEqual(21, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(0x95, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))  # 21 = 0x15 with bit0 on is 0x95

    def test_pn2_on_group_9_C_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['C/99W/TOURS', '3SHAH'])
        T.state.setup.aaa['WA0UB1'] = bytearray([T.wa0pn2])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(9, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(9, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_pn2_on_group_99_C_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['C/999W/TOURS', '3SHAH'])
        T.state.setup.aaa['WA0UB1'] = bytearray([T.wa0pn2])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF9F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_pn2_on_group_Z_wa0pty_history_match_ETAW(self):
        # T.wa0PN2 OFF behaves the same way
        Pnr.add_names(config.AAAPNR, ['Z/99W/SABRE', '3SHAH'])
        T.state.setup.aaa['WA0UB1'] = bytearray([T.wa0pn2])
        T.state.setup.aaa['WA0PTY'] = bytearray([0xE3])  # 99 = 0x63 with bit0 on is 0xE3
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF9F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(0xE3, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_pn2_off_group_wa0pti_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['C/99W/TOURS', '3SHAH'])
        T.state.setup.aaa['WA0UB1'] = bytearray([0x00])
        T.state.setup.aaa['WA0PTI'] = bytearray([3])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertIn('021014', T.state.dumps)
        self.assertEqual(0xF9F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(0, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))

    def test_infant_with_adults_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['2ZAVERI', 'I/1ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertIn('021014', T.state.dumps)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(3, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(3, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(1, T.state.vm.get_byte(T.ebw000 + 10))
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))

    def test_infant_only_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['I/3ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(0xF0F3, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(3, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(3, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(3, T.state.vm.get_byte(T.ebw000 + 10))
        self.assertEqual(3, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))

    def test_infant_at_start_with_less_adults_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['I/33ZAVERI', '44ZAVERI', 'I/22SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertIn('021014', T.state.dumps)
        self.assertEqual(0xF0F0, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(99, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(99, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(55, T.state.vm.get_byte(T.ebw000 + 10))
        self.assertEqual(55, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))

    def test_infant_with_group_wa0pti_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['Z/21SABRE', '3ZAVERI', 'I/1ZAVERI', '4SHAH', 'I/2SHAH'])
        T.state.setup.aaa['WA0PTI'] = bytearray([3])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(0xF1F4, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(24, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(24, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(3, T.state.vm.get_byte(T.ebw000 + 10))
        self.assertEqual(3, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))

    def test_infant_at_start_with_group_ETAW(self):
        Pnr.add_names(config.AAAPNR, ['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertIn('021014', T.state.dumps)
        self.assertEqual(0xF1F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))
        self.assertEqual(32, T.state.vm.get_byte(T.ebw000 + 15))
        self.assertEqual(0, T.state.vm.get_byte(T.ebw000 + 16))
        self.assertEqual(32, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))
        self.assertEqual(7, T.state.vm.get_byte(T.ebw000 + 10))
        self.assertEqual(7, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))


class NameSuccessVarious(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_infant_group_call_from_TOQ1(self) -> None:
        Pnr.add_names(config.AAAPNR, ['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'])
        label = T.state.run('TOQ1', aaa=True)
        self.assertEqual('$$TOQ1$$.4', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(0xF1F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))  # Group - Adults
        self.assertEqual(32, T.state.vm.get_byte(T.ebw000 + 15))                                # Group + Infants
        self.assertEqual(9, T.state.vm.get_byte(T.ebw000 + 16))                                 # Adults
        self.assertEqual(7, T.state.vm.get_byte(T.ebw000 + 10))                                 # Infants
        self.assertEqual(0, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))                    # Group + Infants
        self.assertEqual(0, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))                    # Infants

    def test_infant_group_with_error_from_itinerary_police_not_file_rec_mode_ETA2(self) -> None:
        Pnr.add_names(config.AAAPNR, ['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'])
        T.state.setup.aaa['WA0PTI'] = bytearray([7])  # Infants
        T.state.setup.aaa['WA0PTY'] = bytearray([32])  # Group + Infants
        T.state.setup.errors.add('ETC1ERR')  # Error from Basic Itinerary Police
        T.state.setup.aaa['WA0ET3'] = bytearray([0x00])  # File Rec mode indicator is OFF
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA2$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(0xF1F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))  # Group - Adults
        self.assertEqual(32, T.state.vm.get_byte(T.ebw000 + 15))                                # Group + Infants
        self.assertEqual(0, T.state.vm.get_byte(T.ebw000 + 16))                                 # Adults
        self.assertEqual(7, T.state.vm.get_byte(T.ebw000 + 10))                                 # Infants
        self.assertEqual(32, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))                   # Group + Infants
        self.assertEqual(7, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))                    # Infants

    def test_infant_group_with_error_from_itinerary_police_file_rec_mode_FRD(self) -> None:
        Pnr.add_names(config.AAAPNR, ['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'])
        T.state.setup.aaa['WA0PTI'] = bytearray([0])  # Infants
        T.state.setup.aaa['WA0PTY'] = bytearray([0])  # Group + Infants
        T.state.setup.errors.add('ETC1ERR')  # Error from Basic Itinerary Police
        T.state.setup.aaa['WA0ET3'] = bytearray([0x10])  # File Rec mode indicator is ON
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$FRD1$$.1', label)
        self.assertIn('021014', T.state.dumps)
        self.assertEqual(0xF1F6, T.state.vm.get_unsigned_value(T.state.regs.R1 + T.wa0ext, 2))  # Group - Adults
        self.assertEqual(32, T.state.vm.get_byte(T.ebw000 + 15))                                # Group + Infants
        self.assertEqual(0, T.state.vm.get_byte(T.ebw000 + 16))                                 # Adults
        self.assertEqual(7, T.state.vm.get_byte(T.ebw000 + 10))                                 # Infants
        self.assertEqual(32, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))                   # Group + Infants
        self.assertEqual(7, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pti))                    # Infants


class NameFailETK1(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_no_name_tty_ETK1_33(self) -> None:
        T.state.setup.aaa['WA0ET4'] = bytearray([T.wa0tty])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(0, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0x60))
        self.assertEqual(33, T.state.regs.R6)

    def test_too_many_names_tty_ETK1_33(self) -> None:
        Pnr.add_names(config.AAAPNR, ['45ZAVERI', '55SHAH'])
        T.state.setup.aaa['WA0ET4'] = bytearray([T.wa0tty])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(100, T.state.regs.R15)
        self.assertEqual(T.ui2098, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual(33, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0x60))

    def test_group_overbooking_tty_ETK1_33(self):
        Pnr.add_names(config.AAAPNR, ['Z/15SABRE', '11ZAVERI', '5SHAH'])
        T.state.setup.aaa['WA0ET4'] = bytearray([T.wa0tty])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(33, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0x60))

    def test_multiple_groups_CC_tty_ETK1_33(self):
        Pnr.add_names(config.AAAPNR, ['C/25TOURS', 'C/21TOURS', '1SHAH'])
        T.state.setup.aaa['WA0ET4'] = bytearray([T.wa0tty])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(T.ui2097, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual(33, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0x60))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_multiple_groups_ZC_tty_ETK1_33(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', 'C/21TOURS', '1SHAH'])
        T.state.setup.aaa['WA0ET4'] = bytearray([T.wa0tty])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(T.ui2097, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual(33, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0x60))
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_multiple_groups_CZ_tty_ETK1_16(self):
        Pnr.add_names(config.AAAPNR, ['C/25TOURS', 'Z/21SABRE', '1SHAH'])
        T.state.setup.aaa['WA0ET4'] = bytearray([T.wa0tty])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(T.ui2098, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0xC0))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_multiple_groups_ZZ_tty_ETK1_16(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', 'Z/21SABRE', '1SHAH'])
        T.state.setup.aaa['WA0ET4'] = bytearray([T.wa0tty])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertListEqual(list(), T.state.dumps)
        self.assertEqual(T.ui2098, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0xC0))
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_invalid_type_ETK1_16(self):
        Pnr.add_names(config.AAAPNR, ['K/13TOURS', '1ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0xC0))
        self.assertEqual('K', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_group_Z_not_at_start_ETK1_16(self):
        # It will give the same error if number of party is mentioned in Z/
        Pnr.add_names(config.AAAPNR, ['3ZAVERI', 'Z/SABRE', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0xC0))
        self.assertEqual(0x00, T.state.vm.get_byte(T.ebw000 + 14))

    def test_multiple_groups_ZZ_ETK1_16(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', 'Z/21TOURS', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0xC0))
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_multiple_groups_CZ_ETK1_16(self):
        Pnr.add_names(config.AAAPNR, ['C/25SABRE', 'Z/21TOURS', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETK1$$.1', label)
        self.assertEqual(16, T.state.regs.R6)
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0xC0))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)


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
        ui2inc = macros['UI2PF'].evaluate('UI2INC')
        ui2xui = macros['UI2PF'].evaluate('#UI2XUI')
        ui2can = macros['UI2PF'].evaluate('#UI2CAN')
        ui2nxt = macros['AASEQ'].evaluate('#UI2NXT')
        ui2inc_bytes = bytearray([ui2xui + ui2can, ui2nxt, ui2nxt])
        self.assertEqual(ui2inc_bytes, T.state.vm.get_bytes(T.state.regs.R7 + ui2inc, 3))
        self.assertTrue(T.state.vm.all_bits_off(T.state.regs.R1 + T.wa0et5, 0x02))
        self.assertTrue(T.state.vm.all_bits_on(T.state.regs.R1 + T.wa0et5, T.wa0any))
        self.assertEqual(T.ui2214, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertTrue(T.state.vm.all_bits_on(T.ebrs01, 0x60))

    def test_multiple_groups_CC_UIO1(self):
        Pnr.add_names(config.AAAPNR, ['C/25SABRE', 'C/21TOURS', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$UIO1$$.1', label)
        self.assertTrue(T.state.vm.all_bits_on(T.state.regs.R1 + T.wa0et5, T.wa0any))
        self.assertEqual(T.ui2097, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_multiple_groups_ZC_UIO1(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', 'C/21TOURS', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$UIO1$$.1', label)
        self.assertTrue(T.state.vm.all_bits_on(T.state.regs.R1 + T.wa0et5, T.wa0any))
        self.assertEqual(T.ui2097, T.state.vm.get_byte(T.state.regs.R7 + T.ui2cnn))
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)


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

    def test_invalid_name_high_after_group_ETA2(self):
        Pnr.add_names(config.AAAPNR, ['Z/25SABRE', chr(0xDB) + 'ZAVERI', '1SHAH'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA2$$.1', label)
        self.assertIn('19000', T.state.dumps)
        self.assertEqual(1, T.state.regs.R1)

    def test_invalid_infant_less_ETA2(self) -> None:
        Pnr.add_names(config.AAAPNR, ['I/ZAVERI'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA2$$.1', label)
        self.assertIn('19000', T.state.dumps)
        self.assertEqual(1, T.state.regs.R1)

    def test_invalid_infant_high_ETA2(self) -> None:
        # Without number in party at start
        Pnr.add_names(config.AAAPNR, ['I/' + chr(0xDB) + 'TOURS'])
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

    def test_name_error_ERROR(self) -> None:
        Pnr.add_names(config.AAAPNR, ['1ZAVERI'])
        T.state.setup.errors.add('ETA5090.1')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETA3$$.1', label)


class NameException(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        T.state.init_run()

    def test_invalid_group_at_start_Exception(self):
        # Both C/ and Z/ will give an exception.
        # I/ will NOT give an exception.
        Pnr.add_names(config.AAAPNR, ['Z/SABRE', '1ZAVERI'])
        self.assertRaises(PackExecutionError, T.state.run, 'ETA5', True)
        self.assertEqual('Z', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)

    def test_invalid_group_C_not_at_start_Exception(self):
        # Preceding adult for invalid C/  will give an exception.
        # Preceding adult for invalid Z/ will NOT give an exception.
        Pnr.add_names(config.AAAPNR, ['1ZAVERI', 'C/TOURS'])
        self.assertRaises(PackExecutionError, T.state.run, 'ETA5', True)
        self.assertEqual('C', DataType('X', bytes=T.state.vm.get_bytes(T.ebw000 + 14)).decode)


class Companion(unittest.TestCase):

    def setUp(self) -> None:
        # Award is for Flight 2812 and not for other flight -> Check WP89
        Pnr.init_db()
        Pnr.add_names(config.AAAPNR, ['1ZAVERI'])
        Tpfdf.init_db()
        Tpfdf.add(data=T.tr1gaa, ref_name='TR1GAA', key='40')
        T.state.init_run()
        T.state.setup.aaa['WA0ET6'] = bytearray([T.wa0hfx])

    def test_fqtv_itin_match_award_not_exp_key_ETK2(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        label = T.state.run('TOQ1', aaa=True)
        self.assertEqual('ETK20100.1', label)
        self.assertEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(0x60, T.state.vm.get_byte(T.ebrs01))
        self.assertEqual(116, T.state.regs.R6)

    def test_fqtv_no_match_award_not_exp_key_ETK2(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_exp_key)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('ETK20100.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(0x60, T.state.vm.get_byte(T.ebrs01))
        self.assertEqual(116, T.state.regs.R6)

    def test_itin_no_match_award_not_exp_key_ETK2(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('ETK20100.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(0x60, T.state.vm.get_byte(T.ebrs01))
        self.assertEqual(116, T.state.regs.R6)

    def test_date_error_ETK2(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld_date_error)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('ETK20100.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(0x60, T.state.vm.get_byte(T.ebrs01))
        self.assertEqual(116, T.state.regs.R6)

    def test_fqtv_itin_match_no_award_exp_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2811_exp)
        Pnr.add_fqtv('DGHWCL', T.fqtv_exp_key)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_fqtv_itin_match_award_exp_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_exp)
        Pnr.add_fqtv('DGHWCL', T.fqtv_exp_key)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_fqtv_itin_match_award_key_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_key)
        Pnr.add_fqtv('DGHWCL', T.fqtv_exp_key)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_no_tr1gaa_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        Tpfdf.init_db('TR1GAA')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_tr1gaa_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        T.state.setup.errors.add('ETA92100.1')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_dbifb_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        T.state.setup.errors.add('ETA92300.1')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_pnrcc_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        T.state.setup.errors.add('ETA92300.10')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_prp1_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        T.state.setup.errors.add('PRP1ERR')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_eta9pdwk_allocate_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        T.state.setup.errors.add('ETA92300.25')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_fqtv_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        T.state.setup.errors.add('ETA92400.1')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_itin_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        T.state.setup.errors.add('ETA92500.1')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_chkaward_allocate_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        T.state.setup.errors.add('ETA92500.7')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_chkaward_loadadd_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        T.state.setup.errors.add('ETA92500.19')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))

    def test_fqtv_itin_match_award_error_ETAW(self) -> None:
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        Pnr.add_itin('DGHWCL', T.itin_2811_2812)
        T.state.setup.errors.add('WP89ERR')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual('WP89', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000, 4)).decode)
        self.assertEqual(1, T.state.vm.get_byte(T.state.regs.R1 + T.wa0pty))


class BeforeNameETAW(unittest.TestCase):

    def setUp(self) -> None:
        Pnr.init_db()
        Pnr.add_names(config.AAAPNR, ['1ZAVERI'])
        T.state.init_run()

    def test_HFX_BA_SRT5(self):
        T.state.setup.aaa['WA0ET6'] = bytearray([T.wa0hfx])
        T.state.set_partition('BA')
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('SRT5', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000 + 4, 4)).decode)

    def test_HFX_AA_TKV_SRT5(self):
        T.state.setup.aaa['WA0ET6'] = bytearray([T.wa0hfx])
        T.state.setup.aaa['WA0US3'] = bytearray([T.wa0tkv])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual('SRT5', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000 + 4, 4)).decode)

    def test_ASC_ITN_fqtv_ETAS(self):
        T.state.setup.aaa['WA0ASC'] = bytearray([0x01])
        T.state.setup.aaa['WA0ET2'] = bytearray([T.wa0itn])
        Pnr.add_fqtv(config.AAAPNR, T.fqtv_gld)
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual('ETAS', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000 + 8, 4)).decode)

    def test_ASC_FTN_ETAS(self):
        T.state.setup.aaa['WA0ASC'] = bytearray([0x01])
        T.state.setup.aaa['WA0XX3'] = bytearray([T.wa0ftn])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('ETAS', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000 + 8, 4)).decode)

    def test_ASC_fqtv_ETAS(self):
        T.state.setup.aaa['WA0ASC'] = bytearray([0x01])
        Pnr.add_fqtv(config.AAAPNR, T.fqtv_gld)
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('ETAS', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000 + 8, 4)).decode)

    def test_FTD_ETK2(self):
        T.state.setup.aaa['WA0XX3'] = bytearray([T.wa0ftd])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual(13, T.state.regs.R6)

    def test_AFU_subs_ETGN(self):
        T.state.setup.aaa['WA0USE'] = bytearray([T.wa0afu])
        Pnr.add_subs_card_seg(config.AAAPNR, ['TEST'])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertEqual('ETGN', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000 + 12, 4)).decode)

    def test_AFU_ETGN(self):
        T.state.setup.aaa['WA0USE'] = bytearray([T.wa0afu])
        label = T.state.run('ETA5', aaa=True)
        self.assertEqual('$$ETAW$$.1', label)
        self.assertNotEqual('ETGN', DataType('X', bytes=T.state.vm.get_bytes(T.ebx000 + 12, 4)).decode)


# noinspection PyPep8Naming
def tearDownModule():
    with open('trace_log.txt', 'w') as trace_log:
        trace_log.write('\n'.join([str(trace) for trace in T.state.DEBUG.get_no_hit()]))


if __name__ == '__main__':
    unittest.main()
