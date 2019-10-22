import unittest

from config import config
from db.pnr import Pnr
from test.input_td import TD
from utils.data_type import DataType


class PdredHfax(unittest.TestCase):
    def setUp(self) -> None:
        TD.state.init_run()
        Pnr.init_db()

    def test_pdred_ts19(self):
        # This also test PDCLS
        Pnr.add_hfax(config.AAAPNR, TD.hfax_2812_gld)
        Pnr.add_fqtv('DGHWCL', TD.fqtv_gld)
        Pnr.add_itin(config.AAAPNR, TD.itin_2811_2812)
        TD.state.run('TS19', aaa=True)
        self.assertEqual(0xF2F8F1F2, TD.state.regs.get_unsigned_value('R1'))
        self.assertEqual(0xF9F0F8F7, TD.state.regs.get_unsigned_value('R2'))
        self.assertEqual(0x00D6D9C4, TD.state.regs.get_unsigned_value('R3'))
        date_bytes = TD.state.vm.get_bytes(config.ECB + 8, 5)
        self.assertEqual('24OCT', DataType('X', bytes=date_bytes).decode)
        self.assertEqual(12, TD.state.regs.R12)


if __name__ == '__main__':
    unittest.main()
