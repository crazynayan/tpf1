import unittest

from config import config
from db.pnr import Pnr
from db.tpfdf import Tpfdf
from execution.execute import Execute
from utils.data_type import DataType


class DbTest(unittest.TestCase):
    def setUp(self) -> None:
        self.state = Execute()

    def test_pdred_ts18(self):
        names = [
            'C/21VEENA WORLD',
            '1ZAVERI/NAYAN MR',
            '1ZAVERI/PURVI MRS',
            'I/ZAVERI/S',
        ]
        Pnr.add_names(config.AAAPNR, names)
        self.state.run('TS18', aaa=True)
        self.assertListEqual(list(), self.state.seg.errors)
        self.assertIsNone(self.state.message)
        self.assertEqual(24, self.state.regs.R1)
        # Check for another corporate
        Pnr.add_names(config.AAAPNR, ['C/21VEENA TOURS'])
        self.state.restart('TS18', aaa=True)
        self.assertEqual("'MORE THAN 1 C/'", self.state.message)
        self.assertEqual(0, self.state.regs.R1)
        # Check for > 99 names
        names = ['55ZAVERI', '45SHAH']
        Pnr.init_db()
        Pnr.add_names(config.AAAPNR, names)
        self.state.restart('TS18', aaa=True)
        self.assertEqual("'MORE THAN 99 NAMES'", self.state.message)
        self.assertEqual(100, self.state.regs.R1)

    def test_pdred_ts19(self):
        # This also test PDCLS
        hfax = [
            'SSRFQTUBA2811Y20OCTDFW  ORD  0510EXP/DGHWCL RR    ',
            'SSRWCHRAA2812Y20OCT/NN1',
            'SSRFQTUAA2812Y20OCTDFW  ORD  0510EXP/DGHWCL RR    ',
            'SSRFQTUAA2813Y20OCTDFW  ORD  0510EXP*DGHWCL DR    ',
            'SSRWCHRAA2812Y20OCT/NN1',
            'SSRWCHRAA2812Y20OCT/NN1',
            'SSRFQTUAA2814Y20OCTDFW  ORD  0510EXP*DGHWCL RR    ',
        ]
        fqtv = [
            {
                'PR00_60_FQT_CXR': DataType('C', input='BA').to_bytes(),
                'PR00_60_FQT_FTN': DataType('C', input='NKE9086').to_bytes(),
                'PR00_60_FQT_TYP': DataType('X', input='60').to_bytes(),
            },
            {
                'PR00_60_FQT_CXR': DataType('C', input='AA').to_bytes(),
                'PR00_60_FQT_FTN': DataType('C', input='NKE9087').to_bytes(),
                'PR00_60_FQT_TYP': DataType('X', input='80').to_bytes(),
            },
            {
                'PR00_60_FQT_CXR': DataType('C', input='AA').to_bytes(),
                'PR00_60_FQT_FTN': DataType('C', input='NKE9088').to_bytes(),
                'PR00_60_FQT_TYP': DataType('X', input='60').to_bytes(),
            },
        ]
        itin = [
            {
                'WI0ARC': DataType('C', input='BA').to_bytes(),
                'WI0FNB': DataType('H', input='2812').to_bytes(),
                'WI0DTE': DataType('X', input='4CC1').to_bytes(),
                'WI0BRD': DataType('C', input='DFW').to_bytes(),
                'WI0OFF': DataType('C', input='ORZ').to_bytes(),
            },
            {
                'WI0ARC': DataType('C', input='AA').to_bytes(),
                'WI0FNB': DataType('H', input='2811').to_bytes(),
                'WI0DTE': DataType('X', input='4CC1').to_bytes(),
                'WI0BRD': DataType('C', input='DFW').to_bytes(),
                'WI0OFF': DataType('C', input='ORA').to_bytes(),
            },
            {
                'WI0ARC': DataType('C', input='AA').to_bytes(),
                'WI0FNB': DataType('H', input='2812').to_bytes(),
                'WI0DTE': DataType('X', input='4CC0').to_bytes(),
                'WI0BRD': DataType('C', input='DFW').to_bytes(),
                'WI0OFF': DataType('C', input='ORB').to_bytes(),
            },
            {
                'WI0ARC': DataType('C', input='AA').to_bytes(),
                'WI0FNB': DataType('H', input='2812').to_bytes(),
                'WI0DTE': DataType('X', input='4CC1').to_bytes(),
                'WI0BRD': DataType('C', input='DFX').to_bytes(),
                'WI0OFF': DataType('C', input='ORC').to_bytes(),
            },
            {
                'WI0ARC': DataType('C', input='AA').to_bytes(),
                'WI0FNB': DataType('H', input='2812').to_bytes(),
                'WI0DTE': DataType('X', input='4CC1').to_bytes(),
                'WI0BRD': DataType('C', input='DFW').to_bytes(),
                'WI0OFF': DataType('C', input='ORD').to_bytes(),
            },
        ]
        Pnr.add_hfax(config.AAAPNR, hfax)
        Pnr.add_fqtv('DGHWCL', fqtv)
        Pnr.add_itin(config.AAAPNR, itin)
        self.state.run('TS19', aaa=True)
        self.assertListEqual(list(), self.state.seg.errors)
        self.assertEqual(0xF2F8F1F4, self.state.regs.get_unsigned_value('R1'))
        self.assertEqual(0xF9F0F8F8, self.state.regs.get_unsigned_value('R2'))
        self.assertEqual(0x00D6D9C4, self.state.regs.get_unsigned_value('R3'))

    def test_tpfdf_ts20(self):
        tr1gaa = [
            {
                'TR1G_40_OCC': DataType('C', input='AA').to_bytes(),
                'TR1G_40_ACSTIERCODE': DataType('C', input='EXP').to_bytes(),
                'TR1G_40_TIER_EFFD': DataType('X', input='47D3').to_bytes(),
                'TR1G_40_TIER_DISD': DataType('X', input='7FFF').to_bytes(),
                'TR1G_40_PTI': DataType('X', input='60').to_bytes(),
            },
        ]
        Tpfdf.add(tr1gaa, 'TR1GAA', '40')
        self.state.run('TS20', aaa=True)
        self.assertEqual(21, self.state.regs.R0)
        self.assertEqual(0x60, self.state.vm.get_byte(self.state.regs.R5 + 5))


if __name__ == '__main__':
    unittest.main()
