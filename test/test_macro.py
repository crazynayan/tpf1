import unittest

from v2.errors import Error
from v2.segment import Program


class MacroTest(unittest.TestCase):
    NUMBER_OF_FILES = 16

    def setUp(self) -> None:
        self.program = Program()
        self.macro = None

    def test_files(self):
        self.assertTrue(self.program.is_macro_present('WA0AA'))
        self.assertTrue(self.program.is_macro_present('EB0EB'))
        self.assertFalse(self.program.is_macro_present('ETA5'))
        self.assertEqual(self.NUMBER_OF_FILES, len(self.program.macros),
                         'Update number of files in MacroTest')

    def _common_checks(self, macro_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.macro = self.program.macros[macro_name]
        self.macro.load()
        self.assertListEqual(accepted_errors_list, self.macro.errors, '\n\n\n' + '\n'.join(list(
            set(self.macro.errors) - set(accepted_errors_list))))
        self.assertTrue(self.program.macros[macro_name].loaded)

    def test_WA0AA(self):
        macro_name = 'WA0AA'
        self._common_checks(macro_name)
        self.assertEqual(100, self.macro.symbol_table['WA0OUT'].length)
        self.assertEqual(0x60, self.macro.symbol_table['WA0OUT'].dsp)
        self.assertEqual(0x2c, self.macro.symbol_table['WA0TTO'].dsp)
        self.assertEqual(0x180, self.macro.symbol_table['WA0ORG'].dsp)
        self.assertEqual(0x182, self.macro.symbol_table['WA0ITC'].dsp)
        self.assertEqual(148, self.macro.symbol_table['WA0ITS'].length)
        self.assertEqual(11, self.macro.symbol_table['WA2TSD'].length)
        self.assertEqual(0x218, self.macro.symbol_table['WA2TSD'].dsp)
        self.assertEqual(0x218, self.macro.symbol_table['WA2TAG'].dsp)
        self.assertEqual(0x10, self.macro.symbol_table['#WA0TTY'].dsp)
        self.assertEqual(0x3c6, self.macro.symbol_table['WA2LS3'].dsp)
        self.assertEqual(0x314, self.macro.symbol_table['WA2VFD'].dsp)
        self.assertEqual(178, self.macro.symbol_table['WA2VFD'].length)
        self.assertEqual(0x41e, self.macro.symbol_table['WA0AAZ'].dsp)
        self.assertEqual(48, self.macro.symbol_table['WA2AOF'].length)

    def test_EB0EB(self):
        macro_name = 'EB0EB'
        self._common_checks(macro_name)
        self.assertEqual(8, self.macro.symbol_table['EBW000'].dsp)
        self.assertEqual(0x70, self.macro.symbol_table['EBT000'].dsp)
        self.assertEqual(0xD4, self.macro.symbol_table['EBSW01'].dsp)
        self.assertEqual(8, self.macro.symbol_table['CE1ERS15'].length)
        self.assertEqual(0x2c8, self.macro.symbol_table['CE1SSQ'].dsp)

    def test_SH0HS(self):
        macro_name = 'SH0HS'
        self._common_checks(macro_name)
        self.assertEqual(20, self.macro.symbol_table['SH0EQT'].length)
        self.assertEqual(14, self.macro.symbol_table['SH0CON'].dsp)
        self.assertEqual(0x2a6, self.macro.symbol_table['SH0SKP'].dsp)
        self.assertEqual(1, self.macro.symbol_table['SH0SKP'].length)
        self.assertEqual(0x2a8, self.macro.symbol_table['SH0FLD'].dsp)
        self.assertEqual(0x323, self.macro.symbol_table['SH0EQT'].dsp)
        self.assertEqual(0x337, self.macro.symbol_table['SH0SMK'].dsp)
        self.assertEqual(16, self.macro.symbol_table['SH0SMK'].length)

    def test_PR001W(self):
        macro_name = 'PR001W'
        accepted_errors_list = [
            f"{Error.EXP_INVALID_KEY} #PR001WS:EQU:&SW00WRS {macro_name}",
            f"{Error.EQU_INVALID_VALUE} #PR001WI:EQU:C'&SW00WID' {macro_name}",
            f"{Error.EQU_INVALID_VALUE} #PR001WI:EQU:X'&SW00WID' {macro_name}",
        ]
        self._common_checks(macro_name, accepted_errors_list)
        self.assertEqual(0, self.macro.symbol_table['PR00HDR'].dsp)
        self.assertEqual(0, self.macro.symbol_table['PR00REC'].dsp)
        self.assertEqual(3, self.macro.symbol_table['PR00ORG'].dsp)
        self.assertEqual(40, self.macro.symbol_table['#PR00_00_TYP_040'].dsp)
        self.assertEqual(20, self.macro.symbol_table['PR00E54'].dsp)
        self.assertEqual(20, self.macro.symbol_table['#PR00L54'].dsp)
        self.assertEqual(0xd5, self.macro.symbol_table['#PR00_00_NEWITEM'].dsp)
        self.assertEqual(0x40, self.macro.symbol_table['#PR00_72_RFIC_NOEMD'].dsp)
        self.assertEqual(0x108 - 0x02d, self.macro.symbol_table['PR00_D4_HPFPT_GRP'].length)
        self.assertEqual(2, self.macro.symbol_table['#PR00_X1_TYP1'].length)
        self.assertEqual(4, self.macro.symbol_table['#PR00_X1_TYP1'].dsp)
        self.assertEqual(6, self.macro.symbol_table['PR00_X1_PD_EXTDATA'].dsp)

    def test_TR1GAA(self):
        macro_name = 'TR1GAA'
        accepted_errors_list = [
            f"{Error.EXP_INVALID_KEY} #TR1GAAS:EQU:&SW00WRS {macro_name}",
            f"{Error.EQU_INVALID_VALUE} #TR1GAAI:EQU:C'&SW00WID' {macro_name}",
            f"{Error.EQU_INVALID_VALUE} #TR1GAAI:EQU:X'&SW00WID' {macro_name}",
        ]
        self._common_checks(macro_name, accepted_errors_list)

    def test_PD0WRK(self):
        macro_name = 'PD0WRK'
        self._common_checks(macro_name)
        self.assertEqual(256, self.macro.symbol_table['#PD0_TYP07'].dsp)
        self.assertEqual(0x8000, self.macro.symbol_table['#PD0_TYP00'].dsp)
        self.assertEqual(0xf000, self.macro.symbol_table['#PD0_AIR'].dsp)
        self.assertEqual(0xf040, self.macro.symbol_table['#PD0_AIRO'].dsp)
        self.assertEqual(0x130, self.macro.symbol_table['#PD0_HOTEL'].dsp)
        self.assertEqual(0x706, self.macro.symbol_table['PD0_IN_KEY'].dsp)
        self.assertEqual(0x030, self.macro.symbol_table['PD9_PAR_VD'].dsp)
        self.assertEqual(0xf9a, self.macro.symbol_table['PD0_U_W00'].dsp)
        self.assertEqual(0xe9c, self.macro.symbol_table['PD0_ADR_PHDR'].dsp)
        self.assertEqual(0x0b0, self.macro.symbol_table['PD0_C_ITM'].dsp)

    def test_WI0BS(self):
        macro_name = 'WI0BS'
        self._common_checks(macro_name)
        self.assertEqual(15, self.macro.symbol_table['#WI0BSG'].dsp)

    def test_PNRCM(self):
        macro_name = 'PNRCM'
        self._common_checks(macro_name)
        self.assertEqual(52, self.macro.symbol_table['PM1WRK'].length)
        self.assertEqual(0xc, self.macro.symbol_table['PM1LOC'].dsp)
        self.assertEqual(18, self.macro.symbol_table['PM1ERR'].dsp)

    def test_UI2PF(self):
        macro_name = 'UI2PF'
        self._common_checks(macro_name)
        self.assertEqual(98, self.macro.symbol_table['#UI2098'].dsp)
        self.assertEqual(0x10, self.macro.symbol_table['#UI2XUI'].dsp)
        self.assertEqual(0x08, self.macro.symbol_table['#UI2CAN'].dsp)

    def test_AASEQ(self):
        macro_name = 'AASEQ'
        self._common_checks(macro_name)
        self.assertEqual(0xF2, self.macro.symbol_table['#UI2NXT'].dsp)

    def test_SW00SR(self):
        macro_name = 'SW00SR'
        accepted_errors_list = [
            f"{Error.EQU_INVALID_VALUE} #SW00SRI:EQU:C'&SW00WID' {macro_name}",
            f"{Error.EXP_INVALID_KEY} NODUMP_OPT:EQU:#BIT7 {macro_name}",
            f"{Error.EXP_INVALID_KEY} DFDUMP_OFF:EQU:#BIT7 {macro_name}",
            f"{Error.EXP_INVALID_KEY} DFDUMP_ON:EQU:#BITA-DFDUMP_OFF {macro_name}",
        ]
        self._common_checks(macro_name, accepted_errors_list)


if __name__ == '__main__':
    unittest.main()