import unittest

from p1_utils.data_type import DataType
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS
from p8_test.test_local.test_eta5_execution import hfax_2812_gld, fqtv_gld, itin_2811_2812


class PdredHfax(unittest.TestCase):
    def setUp(self) -> None:
        self.test_data = TestDataUTS()
        self.tpf_server = TpfServer()
        self.test_data.add_fields([('EBW000', 5)], 'EB0EB')
        self.test_data.add_all_regs()

    def test_pdred_ts19(self):
        # This also test PDCLS
        self.test_data.add_pnr_element(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_field_data(fqtv_gld, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_field_data(itin_2811_2812, 'itin')
        test_data = self.tpf_server.run('TS19', self.test_data)
        self.assertEqual(0xF2F8F1F2, test_data.get_unsigned_value('R1'))
        self.assertEqual(0xF9F0F8F7, test_data.get_unsigned_value('R2'))
        self.assertEqual(0x00D6D9C4, test_data.get_unsigned_value('R3'))
        self.assertEqual('24OCT', DataType('X', input=test_data.get_field('EBW000')).decode)
        self.assertEqual(12, test_data.output.regs['R12'])


if __name__ == '__main__':
    unittest.main()
