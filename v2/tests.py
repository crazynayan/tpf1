import unittest

from v2.errors import Error
from v2.macro import Macro
from v2.segment import Segment


class MacroTest(unittest.TestCase):
    NUMBER_OF_FILES = 9

    def setUp(self) -> None:
        self.macro = Macro()

    def test_files(self):
        self.assertTrue('WA0AA' in self.macro.files)
        self.assertTrue('EB0EB' in self.macro.files)
        self.assertFalse('eta5' in self.macro.files)
        self.assertEqual(self.NUMBER_OF_FILES, len(self.macro.files), 'Update number of files in MacroTest')

    def _common_checks(self, macro_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.macro.load(macro_name)
        self.assertListEqual(accepted_errors_list, self.macro.errors, '\n\n\n' + '\n'.join(self.macro.errors))
        self.assertTrue(self.macro.files[macro_name].data_mapped)

    def test_WA0AA(self):
        macro_name = 'WA0AA'
        self._common_checks(macro_name)
        self.assertEqual(100, self.macro.data_map['WA0OUT'].length)
        self.assertEqual(0x60, self.macro.data_map['WA0OUT'].dsp)
        self.assertEqual(0x2c, self.macro.data_map['WA0TTO'].dsp)
        self.assertEqual(0x180, self.macro.data_map['WA0ORG'].dsp)
        self.assertEqual(0x182, self.macro.data_map['WA0ITC'].dsp)
        self.assertEqual(148, self.macro.data_map['WA0ITS'].length)
        self.assertEqual(11, self.macro.data_map['WA2TSD'].length)
        self.assertEqual(0x218, self.macro.data_map['WA2TSD'].dsp)
        self.assertEqual(0x218, self.macro.data_map['WA2TAG'].dsp)
        self.assertEqual(0x10, self.macro.data_map['#WA0TTY'].dsp)
        self.assertEqual(0x3c6, self.macro.data_map['WA2LS3'].dsp)
        self.assertEqual(0x314, self.macro.data_map['WA2VFD'].dsp)
        self.assertEqual(178, self.macro.data_map['WA2VFD'].length)
        self.assertEqual(0x41e, self.macro.data_map['WA0AAZ'].dsp)
        self.assertEqual(48, self.macro.data_map['WA2AOF'].length)

    def test_EB0EB(self):
        macro_name = 'EB0EB'
        self._common_checks(macro_name)
        self.assertEqual(8, self.macro.data_map['EBW000'].dsp)
        self.assertEqual(0x70, self.macro.data_map['EBT000'].dsp)
        self.assertEqual(0xD4, self.macro.data_map['EBSW01'].dsp)
        self.assertEqual(8, self.macro.data_map['CE1ERS15'].length)

    def test_SH0HS(self):
        macro_name = 'SH0HS'
        self._common_checks(macro_name)
        self.assertEqual(20, self.macro.data_map['SH0EQT'].length)
        self.assertEqual(14, self.macro.data_map['SH0CON'].dsp)

    def test_PR001W(self):
        macro_name = 'PR001W'
        accepted_errors_list = [
            f"{Error.DS_DATA_TYPE} #PR00_X1_TYP1:DS:X'0001' {macro_name}",
            f"{Error.EXP_INVALID_KEY} #PR001WS:EQU:&SW00WRS {macro_name}",
            f"{Error.EXP_INVALID_KEY_X} #PR001WI:EQU:X'&SW00WID' {macro_name}",
        ]
        self._common_checks(macro_name, accepted_errors_list)
        self.assertEqual(0, self.macro.data_map['PR00HDR'].dsp)
        self.assertEqual(0, self.macro.data_map['PR00REC'].dsp)
        self.assertEqual(3, self.macro.data_map['PR00ORG'].dsp)
        self.assertEqual(40, self.macro.data_map['#PR00_00_TYP_040'].dsp)
        self.assertEqual(20, self.macro.data_map['PR00E54'].dsp)
        self.assertEqual(20, self.macro.data_map['#PR00L54'].dsp)
        self.assertEqual('N', self.macro.data_map['#PR00_00_NEWITEM'].dsp)
        self.assertEqual(' ', self.macro.data_map['#PR00_72_RFIC_NOEMD'].dsp)
        # self.assertEqual(219, self.macro.data_map['PR00_D4_HPFPT_GRP'].length)

    def test_TR1GAA(self):
        macro_name = 'TR1GAA'
        accepted_errors_list = [
            f"{Error.EXP_INVALID_KEY} #TR1GAAS:EQU:&SW00WRS {macro_name}",
            f"{Error.EXP_INVALID_KEY_X} #TR1GAAI:EQU:X'&SW00WID' {macro_name}",
        ]
        self._common_checks(macro_name, accepted_errors_list)

    def test_PD0WRK(self):
        macro_name = 'PD0WRK'
        self._common_checks(macro_name)
        self.assertEqual(256, self.macro.data_map['#PD0_TYP07'].dsp)
        self.assertEqual(0x8000, self.macro.data_map['#PD0_TYP00'].dsp)
        self.assertEqual(0xf000, self.macro.data_map['#PD0_AIR'].dsp)
        self.assertEqual(0xf040, self.macro.data_map['#PD0_AIRO'].dsp)
        self.assertEqual(0x130, self.macro.data_map['#PD0_HOTEL'].dsp)
        self.assertEqual(0x706, self.macro.data_map['PD0_IN_KEY'].dsp)
        self.assertEqual(0x030, self.macro.data_map['PD9_PAR_VD'].dsp)
        self.assertEqual(0xf9a, self.macro.data_map['PD0_U_W00'].dsp)
        self.assertEqual(0xe9c, self.macro.data_map['PD0_ADR_PHDR'].dsp)
        self.assertEqual(0x0b0, self.macro.data_map['PD0_C_ITM'].dsp)

    def test_WI0BS(self):
        macro_name = 'WI0BS'
        self._common_checks(macro_name)
        self.assertEqual(15, self.macro.data_map['#WI0BSG'].dsp)

    def test_PNRCM(self):
        macro_name = 'PNRCM'
        self._common_checks(macro_name)
        self.assertEqual(52, self.macro.data_map['PM1WRK'].length)
        self.assertEqual(0xc, self.macro.data_map['PM1LOC'].dsp)
        self.assertEqual(18, self.macro.data_map['PM1ERR'].dsp)

    def test_UI2PF(self):
        macro_name = 'UI2PF'
        self._common_checks(macro_name)
        self.assertEqual(98, self.macro.data_map['#UI2098'].dsp)
        # self.assertEqual(0xF2, self.macro.data_map['#UI2NXT'].dsp)  # TODO Need SYSEQ macro


class SegmentTest(unittest.TestCase):
    NUMBER_OF_FILES = 2

    def setUp(self) -> None:
        self.seg = Segment()

    def _common_checks(self, seg_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.seg.load(seg_name)
        self.assertListEqual(accepted_errors_list, self.seg.errors, '\n\n\n' + '\n'.join(self.seg.errors))
        self.assertTrue(self.seg.files[seg_name].loaded)

    def test_files(self):
        self.assertTrue('ETA5' in self.seg.files)
        self.assertTrue('TS01' in self.seg.files)
        self.assertFalse('EB0EB' in self.seg.files)
        self.assertEqual(self.NUMBER_OF_FILES, len(self.seg.files), 'Update number of files in SegmentTest')

    def test_field_bits(self):
        seg_name = 'TS01'
        accepted_errors_list = [
            f"{Error.FBD_NO_LEN} None:OI:23(2,R9),1 {seg_name}",
            f"{Error.FBD_INVALID_BASE} None:OI:EBW000(L'EBW001),1 {seg_name}",
            f"{Error.FBD_INVALID_KEY} None:OI:ERROR_FIELD,1 {seg_name}",
            f"{Error.FBD_INVALID_KEY_BASE} None:OI:PD0_C_ITM,1 {seg_name}",
            f"{Error.FBD_INVALID_DSP} None:OI:C'A'(R2),1 {seg_name}",
            f"{Error.BITS_INVALID_NUMBER} None:OI:EBW000,250+250 {seg_name}",
            f"{Error.BITS_INVALID_BIT} None:OI:EBW000,#PD0_FLDEMP {seg_name}",
            f"{Error.INSTRUCTION_INVALID} None:ERR:EBW000,1 {seg_name}",
        ]
        self.seg.macro.load('PD0WRK')
        del self.seg.macro.files['PD0WRK']
        self._common_checks(seg_name, accepted_errors_list)
        # Check EBW008-EBW000(2),1
        label = '$$TS01$$.1'
        self.assertEqual('R2', self.seg.nodes[label].field.base.reg)
        self.assertEqual(8, self.seg.nodes[label].field.dsp)
        self.assertEqual('R2_AREA', self.seg.nodes[label].field.name)
        self.assertTrue(self.seg.nodes[label].bits.bit7.on)
        self.assertEqual("#BIT7", self.seg.nodes[label].bits.bit7.name)
        # Check EBW000,X'80'
        label = '$$TS01$$.2'
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(8, self.seg.nodes[label].field.dsp)
        self.assertEqual('EBW000', self.seg.nodes[label].field.name)
        self.assertTrue(self.seg.nodes[label].bits.bit0.on)
        self.assertEqual("#BIT0", self.seg.nodes[label].bits.bit0.name)
        self.assertEqual(0x80, self.seg.nodes[label].bits.value)
        # Check 23(R9),23
        label = '$$TS01$$.3'
        self.assertEqual('EBW015', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(23, self.seg.nodes[label].field.dsp)
        self.assertTrue(self.seg.nodes[label].bits.bit7.on)
        self.assertEqual("#BIT3+#BIT5+#BIT6+#BIT7", self.seg.nodes[label].bits.text)
        self.assertEqual(0b00010111, self.seg.nodes[label].bits.value)
        # Check EBT000+L'CE1DSTMP(R9),CE1SEW+CE1CPS+CE1DTX+CE1SNP
        label = '$$TS01$$.4'
        self.assertEqual('EBT008', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x78, self.seg.nodes[label].field.dsp)
        self.assertEqual("CE1SEW+CE1CPS+CE1DTX+CE1SNP", self.seg.nodes[label].bits.text)
        self.assertEqual(0xf0, self.seg.nodes[label].bits.value)
        self.assertTrue(self.seg.nodes[label].bits.bit_by_name('CE1DTX').on)
        self.assertFalse(self.seg.nodes[label].bits.bit6.on)
        # Check L'EBW000+3+EBW008-EBW000(9),X'FF'-CE1SEW-CE1CPS
        label = '$$TS01$$.5'
        self.assertEqual('EBW004', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x0c, self.seg.nodes[label].field.dsp)
        self.assertEqual("#BITA-CE1SEW-CE1CPS", self.seg.nodes[label].bits.text)
        self.assertEqual(0x3f, self.seg.nodes[label].bits.value)
        self.assertFalse(self.seg.nodes[label].bits.bit_by_name('CE1CPS').on)
        self.assertTrue(self.seg.nodes[label].bits.bit6.on)
        # Check TM with BZ TS010010
        label = '$$TS01$$.6'
        self.assertEqual('TS010010', self.seg.nodes[label].goes)
        self.assertEqual('BZ', self.seg.nodes[label].on)
        self.assertSetEqual({'$$TS01$$.7', 'TS010010'}, self.seg.nodes[label].next_labels)
        # Check fall down to label
        label = '$$TS01$$.7'
        self.assertEqual('TS010010', self.seg.nodes[label].fall_down)
        # Check EQU *
        label = 'TS010010'
        self.assertEqual(label, self.seg.nodes[label].label)
        self.assertEqual('EQU', self.seg.nodes[label].command)
