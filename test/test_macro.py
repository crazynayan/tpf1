import unittest

from assembly.program import program
from utils.errors import Error


class MacroTest(unittest.TestCase):
    NUMBER_OF_FILES = 21

    def setUp(self) -> None:
        self.program = program
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
        self.assertEqual(0, self.macro.symbol_table['TR1GHDR'].dsp)
        self.assertEqual(0, self.macro.symbol_table['TR1GREC'].dsp)
        self.assertEqual(0, self.macro.symbol_table['TR1GSIZ'].dsp)
        self.assertEqual(3, self.macro.symbol_table['TR1GORG'].dsp)
        self.assertEqual(3, self.macro.symbol_table['TR1GFAD'].dsp)
        self.assertEqual(3, self.macro.symbol_table['TR1G_40_SCC'].dsp)
        self.assertEqual(6, self.macro.symbol_table['TR1G_40_OCC'].dsp)
        self.assertEqual(9, self.macro.symbol_table['TR1G_40_IHC'].dsp)
        self.assertEqual(0xC, self.macro.symbol_table['TR1G_40_PRD_TYP'].dsp)
        self.assertEqual(0xC1C9D9, self.macro.symbol_table['#TR1G_40_AIR'].dsp)
        self.assertEqual(0xF, self.macro.symbol_table['TR1G_40_PRD_EXP'].dsp)
        self.assertEqual(0xC6C6, self.macro.symbol_table['#TR1G_40_FREQ'].dsp)
        self.assertEqual(0xC3D2, self.macro.symbol_table['#TR1G_40_CONCIERGE'].dsp)
        self.assertEqual(0xC2C3, self.macro.symbol_table['#TR1G_40_BRNDC'].dsp)
        self.assertEqual(0x13, self.macro.symbol_table['TR1G_40_TIER_EFFD'].dsp)
        self.assertEqual(0x17, self.macro.symbol_table['TR1G_40_TIER_DISD'].dsp)
        self.assertEqual(1, self.macro.symbol_table['#TR1G_40_ALLIANCE'].length)
        self.assertEqual(0x1C, self.macro.symbol_table['TR1G_40_TIERS'].dsp)
        self.assertEqual(1, self.macro.symbol_table['#TR1G_40_CI'].length)
        self.assertEqual(0xC3, self.macro.symbol_table['#TR1G_40_CI'].dsp)
        self.assertEqual(0x1D, self.macro.symbol_table['TR1G_40_IN1'].dsp)
        self.assertEqual(0x1E, self.macro.symbol_table['TR1G_40_TPG_TI'].dsp)
        self.assertEqual(2, self.macro.symbol_table['TR1G_40_TPG_TI'].length)
        self.assertEqual(0x1E, self.macro.symbol_table['TR1G_40_TI_EXP'].dsp)
        self.assertEqual(1, self.macro.symbol_table['TR1G_40_TI_EXP'].length)
        self.assertEqual(0x1F, self.macro.symbol_table['TR1G_40_TI'].dsp)
        self.assertEqual(1, self.macro.symbol_table['TR1G_40_TI'].length)
        self.assertEqual(0x20, self.macro.symbol_table['TR1G_40_FTX'].dsp)
        self.assertEqual(36, self.macro.symbol_table['TR1G_40_FTX'].length)
        self.assertEqual(0x20, self.macro.symbol_table['TR1G_40_FTX_LEN'].dsp)
        self.assertEqual(1, self.macro.symbol_table['TR1G_40_FTX_LEN'].length)
        self.assertEqual(0x21, self.macro.symbol_table['TR1G_40_FTX_DATA'].dsp)
        self.assertEqual(35, self.macro.symbol_table['TR1G_40_FTX_DATA'].length)
        self.assertEqual(0x44, self.macro.symbol_table['TR1G_40_TPG_PTI'].dsp)
        self.assertEqual(2, self.macro.symbol_table['TR1G_40_TPG_PTI'].length)
        self.assertEqual(0x44, self.macro.symbol_table['TR1G_40_PTI_EXP'].dsp)
        self.assertEqual(1, self.macro.symbol_table['TR1G_40_PTI_EXP'].length)
        self.assertEqual(0x46, self.macro.symbol_table['TR1G_40_ATPCOTI_EXP'].dsp)
        self.assertEqual(1, self.macro.symbol_table['TR1G_40_ATPCOTI_EXP'].length)
        self.assertEqual(0x6D, self.macro.symbol_table['TR1G_40_TAG'].dsp)
        self.assertEqual(0x40, self.macro.symbol_table['#TR1G_40_CI_DSP'].dsp)
        self.assertEqual(16, self.macro.symbol_table['TR1G_40_TRLVLIND'].length)
        self.assertEqual(0x77, self.macro.symbol_table['TR1G_40_TRLLVLIND1'].dsp)
        self.assertEqual(0x78, self.macro.symbol_table['TR1G_40_TRLLVLIND2'].dsp)
        self.assertEqual(1, self.macro.symbol_table['TR1G_40_TRLLVLIND2'].length)
        self.assertEqual(0x88, self.macro.symbol_table['TR1G_40_BOR_BAN'].dsp)
        self.assertEqual(35, self.macro.symbol_table['TR1G_40_BOR_BAN'].length)
        self.assertEqual(0x10, self.macro.symbol_table['#TR1G_40_ACS_ENTLMNT@CG1'].dsp)
        # self.assertEqual(0x08, self.macro.symbol_table['#TR1G_40_ACS_SKY_PRTY_TIER@CG1'].dsp)
        self.assertEqual(0xB5, self.macro.symbol_table['TR1G_40_TKT_HTAG'].dsp)
        self.assertEqual(0xB5, self.macro.symbol_table['TR1G_40_TKTH'].dsp)
        self.assertEqual(3, self.macro.symbol_table['TR1G_40_TKTH'].length)
        self.assertEqual(0xBA, self.macro.symbol_table['TR1G_40_TKT_ATAG'].dsp)
        self.assertEqual(5, self.macro.symbol_table['TR1G_40_TKT_ATAG'].length)
        self.assertEqual(0xBA, self.macro.symbol_table['TR1G_40_TKTA'].dsp)
        self.assertEqual(0XD3, self.macro.symbol_table['TR1GE40'].dsp)
        self.assertEqual(3, self.macro.symbol_table['TR1G_40_TKTA'].length)
        self.assertEqual(0xBD, self.macro.symbol_table['TR1G_40_TKTA_EXP'].dsp)
        self.assertEqual(2, self.macro.symbol_table['TR1G_40_TKTA_EXP'].length)
        self.assertEqual(0xCC, self.macro.symbol_table['TR1G_40_ELTELP'].dsp)
        self.assertEqual(1, self.macro.symbol_table['TR1G_40_ELTELP'].length)
        self.assertEqual(0xCE, self.macro.symbol_table['TR1G_40_SPR'].dsp)
        self.assertEqual(3, self.macro.symbol_table['TR1G_80_OWNCC'].dsp)
        self.assertEqual(6, self.macro.symbol_table['TR1G_80_ALG_EFFD'].dsp)
        # self.assertEqual(0xFF, self.macro.symbol_table['TR1G_80_ATYP_255'].dsp)
        self.assertEqual(0x3B, self.macro.symbol_table['TR1GE80'].dsp)

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
        self.assertEqual(0xFF, self.macro.symbol_table['#WI0MAX'].dsp)
        self.assertEqual(1, self.macro.symbol_table['WI0TYP'].length)
        self.assertEqual(2, self.macro.symbol_table['#WI0CCS'].dsp)
        self.assertEqual(0xE, self.macro.symbol_table['WI0BI3'].dsp)
        self.assertEqual(0x1A, self.macro.symbol_table['WI0FNB'].dsp)
        self.assertEqual(0x1C, self.macro.symbol_table['WI0VAR'].dsp)
        self.assertEqual(0x1C, self.macro.symbol_table['#WI0FXL'].dsp)
        self.assertEqual(1, self.macro.symbol_table['WI0VAR'].length)
        self.assertEqual(0, self.macro.symbol_table['WI0EXF'].dsp)
        self.assertEqual(0, self.macro.symbol_table['WI0EXL'].dsp)
        self.assertEqual(0xF, self.macro.symbol_table['#WI0BSG'].dsp)
        self.assertEqual(2, self.macro.symbol_table['WI0EXD'].dsp)
        self.assertEqual(2, self.macro.symbol_table['WI0BFA'].dsp)
        self.assertEqual(2, self.macro.symbol_table['WI0TTL'].dsp)
        self.assertEqual(8, self.macro.symbol_table['WI0RCL'].dsp)
        self.assertEqual(0x1C, self.macro.symbol_table['WI0ZRL'].dsp)

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

    def test_MI0MI(self):
        macro_name = 'MI0MI'
        accepted_errors_list = [
        ]
        self._common_checks(macro_name, accepted_errors_list)
        self.assertEqual(0x15, self.macro.symbol_table['MI0ACC'].dsp)

    def test_PDEQU(self):
        macro_name = 'PDEQU'
        accepted_errors_list = [
        ]
        self._common_checks(macro_name, accepted_errors_list)
        self.assertEqual(0x50, self.macro.symbol_table['#PD_NAME_K'].dsp)


if __name__ == '__main__':
    unittest.main()
