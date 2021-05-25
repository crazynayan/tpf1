import unittest

from p2_assembly.mac2_data_macro import DataMacro, macros


class MacroTest(unittest.TestCase):
    NUMBER_OF_FILES = 59

    def test_files(self):
        self.assertIn('EB0EB', macros)
        self.assertIn('WA0AA', macros)
        self.assertNotIn('ETA5', macros)
        self.assertEqual(self.NUMBER_OF_FILES, len(macros), 'Update number of files in MacroTest')

    def _common_checks(self, macro_name, accepted_errors_list=None):
        self.macro: DataMacro = macros[macro_name]
        self.macro.load()
        self.assertTrue(macros[macro_name].loaded)
        if accepted_errors_list is not None:
            for label in accepted_errors_list:
                self.assertFalse(self.macro.check(label))
        return

    def test_WA0AA(self):
        macro_name = 'WA0AA'
        self._common_checks(macro_name)
        self.assertEqual(100, self.macro.lookup('WA0OUT').length)
        self.assertEqual(0x60, self.macro.lookup('WA0OUT').dsp)
        self.assertEqual(0x2c, self.macro.lookup('WA0TTO').dsp)
        self.assertEqual(0x180, self.macro.lookup('WA0ORG').dsp)
        self.assertEqual(0x182, self.macro.lookup('WA0ITC').dsp)
        self.assertEqual(148, self.macro.lookup('WA0ITS').length)
        self.assertEqual(11, self.macro.lookup('WA2TSD').length)
        self.assertEqual(0x218, self.macro.lookup('WA2TSD').dsp)
        self.assertEqual(0x218, self.macro.lookup('WA2TAG').dsp)
        self.assertEqual(0x10, self.macro.lookup('#WA0TTY').dsp)
        self.assertEqual(0x3c6, self.macro.lookup('WA2LS3').dsp)
        self.assertEqual(0x314, self.macro.lookup('WA2VFD').dsp)
        self.assertEqual(178, self.macro.lookup('WA2VFD').length)
        self.assertEqual(0x41e, self.macro.lookup('WA0AAZ').dsp)
        self.assertEqual(48, self.macro.lookup('WA2AOF').length)

    def test_EB0EB(self):
        macro_name = 'EB0EB'
        self._common_checks(macro_name)
        self.assertEqual(8, self.macro.lookup('EBW000').dsp)
        self.assertEqual(0x70, self.macro.lookup('EBT000').dsp)
        self.assertEqual(0xD4, self.macro.lookup('EBSW01').dsp)
        self.assertEqual(8, self.macro.lookup('CE1ERS15').length)
        self.assertEqual(0x2c8, self.macro.lookup('CE1SSQ').dsp)

    def test_SH0HS(self):
        macro_name = 'SH0HS'
        self._common_checks(macro_name)
        self.assertEqual(20, self.macro.lookup('SH0EQT').length)
        self.assertEqual(14, self.macro.lookup('SH0CON').dsp)
        self.assertEqual(0x2a6, self.macro.lookup('SH0SKP').dsp)
        self.assertEqual(1, self.macro.lookup('SH0SKP').length)
        self.assertEqual(0x2a8, self.macro.lookup('SH0FLD').dsp)
        self.assertEqual(0x323, self.macro.lookup('SH0EQT').dsp)
        self.assertEqual(0x337, self.macro.lookup('SH0SMK').dsp)
        self.assertEqual(16, self.macro.lookup('SH0SMK').length)

    def test_PR001W(self):
        macro_name = 'PR001W'
        accepted_errors_list = ['#PR001WS', '#PR001WI', ]
        self._common_checks(macro_name, accepted_errors_list)
        self.assertEqual(0, self.macro.lookup('PR00HDR').dsp)
        self.assertEqual(0, self.macro.lookup('PR00REC').dsp)
        self.assertEqual(3, self.macro.lookup('PR00ORG').dsp)
        self.assertEqual(40, self.macro.lookup('#PR00_00_TYP_040').dsp)
        self.assertEqual(20, self.macro.lookup('PR00E54').dsp)
        self.assertEqual(20, self.macro.lookup('#PR00L54').dsp)
        self.assertEqual(0xd5, self.macro.lookup('#PR00_00_NEWITEM').dsp)
        self.assertEqual(0x40, self.macro.lookup('#PR00_72_RFIC_NOEMD').dsp)
        self.assertEqual(0x108 - 0x02d, self.macro.lookup('PR00_D4_HPFPT_GRP').length)
        self.assertEqual(2, self.macro.lookup('#PR00_X1_TYP1').length)
        self.assertEqual(4, self.macro.lookup('#PR00_X1_TYP1').dsp)
        self.assertEqual(6, self.macro.lookup('PR00_X1_PD_EXTDATA').dsp)

    def test_TR1GAA(self):
        macro_name = 'TR1GAA'
        accepted_errors_list = ['#TR1GAAS', '#TR1GAAI', ]
        self._common_checks(macro_name, accepted_errors_list)
        self.assertEqual(0, self.macro.lookup('TR1GHDR').dsp)
        self.assertEqual(0, self.macro.lookup('TR1GREC').dsp)
        self.assertEqual(0, self.macro.lookup('TR1GSIZ').dsp)
        self.assertEqual(3, self.macro.lookup('TR1GORG').dsp)
        self.assertEqual(3, self.macro.lookup('TR1GFAD').dsp)
        self.assertEqual(3, self.macro.lookup('TR1G_40_SCC').dsp)
        self.assertEqual(6, self.macro.lookup('TR1G_40_OCC').dsp)
        self.assertEqual(9, self.macro.lookup('TR1G_40_IHC').dsp)
        self.assertEqual(0xC, self.macro.lookup('TR1G_40_PRD_TYP').dsp)
        self.assertEqual(0xC1C9D9, self.macro.lookup('#TR1G_40_AIR').dsp)
        self.assertEqual(0xF, self.macro.lookup('TR1G_40_PRD_EXP').dsp)
        self.assertEqual(0xC6C6, self.macro.lookup('#TR1G_40_FREQ').dsp)
        self.assertEqual(0xC3D2, self.macro.lookup('#TR1G_40_CONCIERGE').dsp)
        self.assertEqual(0xC2C3, self.macro.lookup('#TR1G_40_BRNDC').dsp)
        self.assertEqual(0x13, self.macro.lookup('TR1G_40_TIER_EFFD').dsp)
        self.assertEqual(0x17, self.macro.lookup('TR1G_40_TIER_DISD').dsp)
        self.assertEqual(1, self.macro.lookup('#TR1G_40_ALLIANCE').length)
        self.assertEqual(0x1C, self.macro.lookup('TR1G_40_TIERS').dsp)
        self.assertEqual(1, self.macro.lookup('#TR1G_40_CI').length)
        self.assertEqual(0xC3, self.macro.lookup('#TR1G_40_CI').dsp)
        self.assertEqual(0x1D, self.macro.lookup('TR1G_40_IN1').dsp)
        self.assertEqual(0x1E, self.macro.lookup('TR1G_40_TPG_TI').dsp)
        self.assertEqual(2, self.macro.lookup('TR1G_40_TPG_TI').length)
        self.assertEqual(0x1E, self.macro.lookup('TR1G_40_TI_EXP').dsp)
        self.assertEqual(1, self.macro.lookup('TR1G_40_TI_EXP').length)
        self.assertEqual(0x1F, self.macro.lookup('TR1G_40_TI').dsp)
        self.assertEqual(1, self.macro.lookup('TR1G_40_TI').length)
        self.assertEqual(0x20, self.macro.lookup('TR1G_40_FTX').dsp)
        self.assertEqual(36, self.macro.lookup('TR1G_40_FTX').length)
        self.assertEqual(0x20, self.macro.lookup('TR1G_40_FTX_LEN').dsp)
        self.assertEqual(1, self.macro.lookup('TR1G_40_FTX_LEN').length)
        self.assertEqual(0x21, self.macro.lookup('TR1G_40_FTX_DATA').dsp)
        self.assertEqual(35, self.macro.lookup('TR1G_40_FTX_DATA').length)
        self.assertEqual(0x44, self.macro.lookup('TR1G_40_TPG_PTI').dsp)
        self.assertEqual(2, self.macro.lookup('TR1G_40_TPG_PTI').length)
        self.assertEqual(0x44, self.macro.lookup('TR1G_40_PTI_EXP').dsp)
        self.assertEqual(1, self.macro.lookup('TR1G_40_PTI_EXP').length)
        self.assertEqual(0x46, self.macro.lookup('TR1G_40_ATPCOTI_EXP').dsp)
        self.assertEqual(1, self.macro.lookup('TR1G_40_ATPCOTI_EXP').length)
        self.assertEqual(0x6D, self.macro.lookup('TR1G_40_TAG').dsp)
        self.assertEqual(0x40, self.macro.lookup('#TR1G_40_CI_DSP').dsp)
        self.assertEqual(16, self.macro.lookup('TR1G_40_TRLVLIND').length)
        self.assertEqual(0x77, self.macro.lookup('TR1G_40_TRLLVLIND1').dsp)
        self.assertEqual(0x78, self.macro.lookup('TR1G_40_TRLLVLIND2').dsp)
        self.assertEqual(1, self.macro.lookup('TR1G_40_TRLLVLIND2').length)
        self.assertEqual(0x88, self.macro.lookup('TR1G_40_BOR_BAN').dsp)
        self.assertEqual(35, self.macro.lookup('TR1G_40_BOR_BAN').length)
        self.assertEqual(0x10, self.macro.lookup('#TR1G_40_ACS_ENTLMNT@CG1').dsp)
        self.assertEqual(0xB5, self.macro.lookup('TR1G_40_TKT_HTAG').dsp)
        self.assertEqual(0xB5, self.macro.lookup('TR1G_40_TKTH').dsp)
        self.assertEqual(3, self.macro.lookup('TR1G_40_TKTH').length)
        self.assertEqual(0xBA, self.macro.lookup('TR1G_40_TKT_ATAG').dsp)
        self.assertEqual(5, self.macro.lookup('TR1G_40_TKT_ATAG').length)
        self.assertEqual(0xBA, self.macro.lookup('TR1G_40_TKTA').dsp)
        self.assertEqual(0XD3, self.macro.lookup('TR1GE40').dsp)
        self.assertEqual(3, self.macro.lookup('TR1G_40_TKTA').length)
        self.assertEqual(0xBD, self.macro.lookup('TR1G_40_TKTA_EXP').dsp)
        self.assertEqual(2, self.macro.lookup('TR1G_40_TKTA_EXP').length)
        self.assertEqual(0xCC, self.macro.lookup('TR1G_40_ELTELP').dsp)
        self.assertEqual(1, self.macro.lookup('TR1G_40_ELTELP').length)
        self.assertEqual(0xCE, self.macro.lookup('TR1G_40_SPR').dsp)
        self.assertEqual(3, self.macro.lookup('TR1G_80_OWNCC').dsp)
        self.assertEqual(6, self.macro.lookup('TR1G_80_ALG_EFFD').dsp)
        self.assertEqual(0x3B, self.macro.lookup('TR1GE80').dsp)

    def test_PD0WRK(self):
        macro_name = 'PD0WRK'
        self._common_checks(macro_name)
        self.assertEqual(256, self.macro.lookup('#PD0_TYP07').dsp)
        self.assertEqual(0x8000, self.macro.lookup('#PD0_TYP00').dsp)
        self.assertEqual(0xf000, self.macro.lookup('#PD0_AIR').dsp)
        self.assertEqual(0xf040, self.macro.lookup('#PD0_AIRO').dsp)
        self.assertEqual(0x130, self.macro.lookup('#PD0_HOTEL').dsp)
        self.assertEqual(0x706, self.macro.lookup('PD0_IN_KEY').dsp)
        self.assertEqual(0x030, self.macro.lookup('PD9_PAR_VD').dsp)
        self.assertEqual(0xf9a, self.macro.lookup('PD0_U_W00').dsp)
        self.assertEqual(0xe9c, self.macro.lookup('PD0_ADR_PHDR').dsp)
        self.assertEqual(0x0b0, self.macro.lookup('PD0_C_ITM').dsp)

    def test_WI0BS(self):
        macro_name = 'WI0BS'
        self._common_checks(macro_name)
        self.assertEqual(15, self.macro.lookup('#WI0BSG').dsp)
        self.assertEqual(0xFF, self.macro.lookup('#WI0MAX').dsp)
        self.assertEqual(1, self.macro.lookup('WI0TYP').length)
        self.assertEqual(2, self.macro.lookup('#WI0CCS').dsp)
        self.assertEqual(0xE, self.macro.lookup('WI0BI3').dsp)
        self.assertEqual(0x1A, self.macro.lookup('WI0FNB').dsp)
        self.assertEqual(0x1C, self.macro.lookup('WI0VAR').dsp)
        self.assertEqual(0x1C, self.macro.lookup('#WI0FXL').dsp)
        self.assertEqual(1, self.macro.lookup('WI0VAR').length)
        self.assertEqual(0, self.macro.lookup('WI0EXF').dsp)
        self.assertEqual(0, self.macro.lookup('WI0EXL').dsp)
        self.assertEqual(0xF, self.macro.lookup('#WI0BSG').dsp)
        self.assertEqual(2, self.macro.lookup('WI0EXD').dsp)
        self.assertEqual(2, self.macro.lookup('WI0BFA').dsp)
        self.assertEqual(2, self.macro.lookup('WI0TTL').dsp)
        self.assertEqual(8, self.macro.lookup('WI0RCL').dsp)
        self.assertEqual(0x1C, self.macro.lookup('WI0ZRL').dsp)

    def test_PNRCM(self):
        macro_name = 'PNRCM'
        self._common_checks(macro_name)
        self.assertEqual(52, self.macro.lookup('PM1WRK').length)
        self.assertEqual(0xc, self.macro.lookup('PM1LOC').dsp)
        self.assertEqual(18, self.macro.lookup('PM1ERR').dsp)

    def test_UI2PF(self):
        macro_name = 'UI2PF'
        self._common_checks(macro_name)
        self.assertEqual(98, self.macro.lookup('#UI2098').dsp)
        self.assertEqual(0x10, self.macro.lookup('#UI2XUI').dsp)
        self.assertEqual(0x08, self.macro.lookup('#UI2CAN').dsp)

    def test_AASEQ(self):
        macro_name = 'AASEQ'
        self._common_checks(macro_name)
        self.assertEqual(0xF2, self.macro.lookup('#UI2NXT').dsp)

    def test_SW00SR(self):
        macro_name = 'SW00SR'
        accepted_errors_list = ['#SW00SRI', ]
        self._common_checks(macro_name, accepted_errors_list)

    def test_MI0MI(self):
        macro_name = 'MI0MI'
        self._common_checks(macro_name)
        self.assertEqual(0x15, self.macro.lookup('MI0ACC').dsp)

    def test_PDEQU(self):
        macro_name = 'PDEQU'
        self._common_checks(macro_name)
        self.assertEqual(0x50, self.macro.lookup('#PD_NAME_K').dsp)

    def test_FT3FT(self):
        self._common_checks('FT3FT')
        self.assertEqual(0x000, self.macro.lookup('FT3REG').dsp)
        self.assertEqual(4, self.macro.lookup('FT3REG').length)
        self.assertEqual(0x020, self.macro.lookup('FT3SAV').dsp)
        self.assertEqual(0x020, self.macro.lookup('FT3R13').dsp)
        self.assertEqual(0x092, self.macro.lookup('FT3END').dsp)

    def test_MH0HM(self):
        self._common_checks('MH0HM')

    def test_NNM1WK(self):
        self._common_checks('NNM1WK')

    def test_NM0WK(self):
        self._common_checks('NM0WK')

    def test_SV0SV(self):
        self._common_checks('SV0SV')

    def test_FT0FT(self):
        self._common_checks('FT0FT')

    def test_S40S4(self):
        self._common_checks('S40S4')

    def test_TJ0TJ(self):
        self._common_checks('TJ0TJ')

    def test_ADVWK(self):
        self._common_checks('ADVWK')

    def test_PRBWRK(self):
        self._common_checks('PRBWRK')

    def test_TI011W(self):
        self._common_checks('TI011W')

    def test_WY0WY(self):
        self._common_checks('WY0WY')

    def test_PDHWK(self):
        self._common_checks('PDHWK')

    def test_TR1GWK(self):
        self._common_checks('TR1GWK')

    def test_RR731S(self):
        self._common_checks('RR731S')

    def test_ETA1_additions(self):
        macro_list = ["ET1WKA", "PD4TP", "PM0WK", "TF2WK", "TP5TI", "WI2BS", "WX1AA"]
        for macro_name in macro_list:
            self._common_checks(macro_name)

    def test_ETAX_ETAF_ETAZ_additions(self):
        macro_list = ["WA1AA", "MAGIC", "IDECB", "RR1WAA"]
        for macro_name in macro_list:
            self._common_checks(macro_name)

    def test_ETK1_additions(self):
        macro_list = ["ET0WK", "ETKWK", "ETEWK"]
        for macro_name in macro_list:
            self._common_checks(macro_name)

    def test_ETA4_ETA6_additions(self):
        macro_list = ["TKFWK", "TKTEQ", "PX0WK", "TJ5WK", "QR041W", "ETGLDSP"]
        for macro_name in macro_list:
            self._common_checks(macro_name)


if __name__ == '__main__':
    unittest.main()
