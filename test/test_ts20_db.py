import unittest

from config import config
from db.pnr import Pnr
from db.tpfdf import Tpfdf
from utils.data_type import DataType
from utils.test_data import T


class DbTest(unittest.TestCase):
    def setUp(self) -> None:
        T.state.init_run()
        Pnr.init_db()

    def test_pdred_ts18(self):
        names = ['C/21TOURS', '2ZAVERI',  'I/2ZAVERI/S']
        Pnr.add_names(config.AAAPNR, names)
        T.state.run('TS18', aaa=True)
        self.assertIsNone(T.state.message)
        self.assertEqual(25, T.state.regs.R1)
        # Check for another corporate
        Pnr.add_names(config.AAAPNR, ['C/21VEENA TOURS'])
        T.state.restart('TS18', aaa=True)
        self.assertEqual("'MORE THAN 1 C/'", T.state.message)
        self.assertEqual(0, T.state.regs.R1)
        # Check for > 99 names
        names = ['55ZAVERI', '45SHAH']
        Pnr.init_db()
        Pnr.add_names(config.AAAPNR, names)
        T.state.restart('TS18', aaa=True)
        self.assertEqual("'MORE THAN 99 NAMES'", T.state.message)
        self.assertEqual(100, T.state.regs.R1)

    def test_pdred_ts19(self):
        # This also test PDCLS
        Pnr.add_hfax(config.AAAPNR, T.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', T.fqtv_gld)
        Pnr.add_itin(config.AAAPNR, T.itin_2811_2812)
        T.state.run('TS19', aaa=True)
        self.assertEqual(0xF2F8F1F2, T.state.regs.get_unsigned_value('R1'))
        self.assertEqual(0xF9F0F8F7, T.state.regs.get_unsigned_value('R2'))
        self.assertEqual(0x00D6D9C4, T.state.regs.get_unsigned_value('R3'))
        date_bytes = T.state.vm.get_bytes(config.ECB + 8, 5)
        self.assertEqual('24OCT', DataType('X', bytes=date_bytes).decode)
        self.assertEqual(12, T.state.regs.R12)

    def test_tpfdf_ts20(self):
        Tpfdf.add(T.tr1gaa, 'TR1GAA', '40')
        T.state.run('TS20', aaa=True)
        self.assertEqual(21, T.state.regs.R0)
        self.assertEqual(0x80, T.state.vm.get_byte(T.state.regs.R5 + 5))


if __name__ == '__main__':
    unittest.main()
