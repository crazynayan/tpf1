import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS
from test.test_eta5_execution import hfax_2812_gld, fqtv_gld, itin_2811_2812
from utils.data_type import DataType


class PdredHfax(unittest.TestCase):
    def setUp(self) -> None:
        self.test_data = TestDataUTS()
        self.tpf_server = Execute()
        self.output = self.test_data.output
        self.ecb = self.test_data.add_core_with_len([('EBW000', 5)], 'EB0EB')
        self.output.add_regs(['R1', 'R2', 'R3', 'R12'])

    def test_pdred_ts19(self):
        # This also test PDCLS
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin')
        self.tpf_server.run('TS19', self.test_data)
        self.assertEqual(0xF2F8F1F2, self.output.get_unsigned_value('R1'))
        self.assertEqual(0xF9F0F8F7, self.output.get_unsigned_value('R2'))
        self.assertEqual(0x00D6D9C4, self.output.get_unsigned_value('R3'))
        self.assertEqual('24OCT', DataType('X', input=self.ecb['EBW000'].hex).decode)
        self.assertEqual(12, self.output.regs['R12'])


if __name__ == '__main__':
    unittest.main()
