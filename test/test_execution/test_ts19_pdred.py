import unittest

from config import config
from db.pnr import Pnr
from utils.data_type import DataType
from utils.test_data import T


class PdredHfax(unittest.TestCase):
    def setUp(self) -> None:
        T.state.init_run()
        Pnr.init_db()

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


if __name__ == '__main__':
    unittest.main()
