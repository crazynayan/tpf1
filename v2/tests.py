import unittest

from v2.errors import Error
from v2.macro import Macro
from v2.segment import Segment, Label


class MacroTest(unittest.TestCase):
    NUMBER_OF_FILES = 12

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
        self.assertListEqual(accepted_errors_list, self.macro.errors, '\n\n\n' + '\n'.join(list(
            set(self.macro.errors) - set(accepted_errors_list))))
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
        self.assertEqual(0x323, self.macro.data_map['SH0EQT'].dsp)
        self.assertEqual(0x337, self.macro.data_map['SH0SMK'].dsp)
        self.assertEqual(16, self.macro.data_map['SH0SMK'].length)

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
    NUMBER_OF_FILES = 5

    def setUp(self) -> None:
        self.seg = Segment()

    def _common_checks(self, seg_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.seg.load(seg_name)
        self.assertListEqual(accepted_errors_list, self.seg.errors, '\n\n\n' + '\n'.join(list(
            set(self.seg.errors) - set(accepted_errors_list))))
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

    def test_reg_reg(self):
        seg_name = 'TS02'
        accepted_errors_list = [
            f"{Error.REG_INVALID} TS02E010:LR:R16,R15 {seg_name}",
            f"{Error.REG_INVALID} TS02E020:LR:R1,RBD {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # Check R02,RDA
        label = 'TS020010'
        self.assertEqual('R2', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R14', self.seg.nodes[label].reg2.reg)
        # Check RGA,2 with JNZ TS020010 & it contains a before_goes
        label = 'TS020020'
        self.assertEqual('R2', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R2', self.seg.nodes[label].reg2.reg)
        self.assertEqual('JNZ', self.seg.nodes[label].on)
        self.assertSetEqual({'TS020030', 'TS020040'}, self.seg.nodes[label].next_labels)
        self.assertEqual(4, self.seg.nodes[label].before_goes)
        # Check 4,R04
        label = 'TS020030'
        self.assertEqual('R4', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R4', self.seg.nodes[label].reg2.reg)
        self.assertSetEqual({'TS020040'}, self.seg.nodes[label].next_labels)
        # Check DS    0H
        label = 'TS020040'
        self.assertEqual(label, self.seg.nodes[label].label)
        self.assertEqual('DS', self.seg.nodes[label].command)
        # Check  BCTR  R5,0
        label = 'TS020040.1'
        self.assertEqual('R5', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R0', self.seg.nodes[label].reg2.reg)
        # Check the saved instruction inside $$TS02$$.2
        label = 'TS020020'
        goes_label = Label(label, Label.BEFORE_GOES_SEPARATOR)
        for _ in range(self.seg.nodes[label].before_goes):
            goes_label.index += 1
            self.assertEqual('R6', self.seg.nodes[str(goes_label)].reg1.reg)
            self.assertIsNone(self.seg.nodes[str(goes_label)].fall_down)
        self.assertEqual('R7', self.seg.nodes[str(goes_label)].reg2.reg)

    def test_reg_index(self):
        seg_name = 'TS03'
        accepted_errors_list = [
            f"{Error.RFX_INVALID_REG} None:L:R16,EBW000 {seg_name}",
            f"{Error.FBD_INVALID_BASE} None:LA:R1,2(R1,R3,R4) {seg_name}",
            f"{Error.FX_INVALID_INDEX} None:LA:R1,2(ABC,R1) {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # L     R1,CE1CR1
        label = '$$TS03$$.1'
        self.assertEqual('R1', self.seg.nodes[label].reg.reg)
        self.assertEqual('CE1CR1', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x170, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)
        # LA    R2,2
        label = '$$TS03$$.2'
        self.assertEqual('R2', self.seg.nodes[label].reg.reg)
        self.assertEqual('R0_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R0', self.seg.nodes[label].field.base.reg)
        self.assertEqual(2, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)
        # IC    R1,3(R3,R4)
        label = '$$TS03$$.3'
        self.assertEqual('R1', self.seg.nodes[label].reg.reg)
        self.assertEqual('R4_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R4', self.seg.nodes[label].field.base.reg)
        self.assertEqual(3, self.seg.nodes[label].field.dsp)
        self.assertEqual('R3', self.seg.nodes[label].field.index.reg)
        # STH   R3,L'CE1CR1
        label = '$$TS03$$.4'
        self.assertEqual('R3', self.seg.nodes[label].reg.reg)
        self.assertEqual('R0_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R0', self.seg.nodes[label].field.base.reg)
        self.assertEqual(4, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)
        # N     R5,EBW008-EB0EB(R6)
        label = '$$TS03$$.5'
        self.assertEqual('R5', self.seg.nodes[label].reg.reg)
        self.assertEqual('R6_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R6', self.seg.nodes[label].field.base.reg)
        self.assertEqual(16, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)
        # ST    R2,L'EBW000+2(R6,)
        label = '$$TS03$$.6'
        self.assertEqual('R2', self.seg.nodes[label].reg.reg)
        self.assertEqual('R6_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R6', self.seg.nodes[label].field.base.reg)
        self.assertEqual(3, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)
        # STC   5,EBT000(0,9)
        label = '$$TS03$$.7'
        self.assertEqual('R5', self.seg.nodes[label].reg.reg)
        self.assertEqual('EBT000', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x070, self.seg.nodes[label].field.dsp)
        self.assertEqual('R0', self.seg.nodes[label].field.index.reg)
        # STC   CVB   RGC,L'CE1CR1+EBW000(,REB)
        label = '$$TS03$$.8'
        self.assertEqual('R4', self.seg.nodes[label].reg.reg)
        self.assertEqual('EBW004', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(12, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)
        # CVD   R06,6000(R00,R00)
        label = '$$TS03$$.9'
        self.assertEqual('R6', self.seg.nodes[label].reg.reg)
        self.assertEqual('R0_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R0', self.seg.nodes[label].field.base.reg)
        self.assertEqual(6000, self.seg.nodes[label].field.dsp)
        self.assertEqual('R0', self.seg.nodes[label].field.index.reg)
        # CH    R15,4(R15)
        label = '$$TS03$$.10'
        self.assertEqual('R15', self.seg.nodes[label].reg.reg)
        self.assertEqual('R15_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R15', self.seg.nodes[label].field.base.reg)
        self.assertEqual(4, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)

    def test_field_variants(self):
        seg_name = 'TS04'
        accepted_errors_list = [
            f"{Error.FL_INVALID_LEN} None:MVC:23(L'CE1WKA+60,R3),26(R4) {seg_name}",
            f"{Error.FL_INVALID_LEN} None:XC:CE1WKA(#$BCLASS),CE1WKA {seg_name}",
            f"{Error.FL_LEN_REQUIRED} None:OC:EBW000(,R4),EBW000 {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # Check FieldLenField
        # XC    CE1WKA,CE1WKA
        label = 'TS040100.1'
        self.assertEqual('CE1WKA', self.seg.nodes[label].field_len.name)
        self.assertEqual('R9', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(0x8, self.seg.nodes[label].field_len.dsp)
        self.assertEqual(212, self.seg.nodes[label].field_len.length)
        # CLC   L'CE1WKA+EBW000+4(CE1FA1-CE1FA0,R9),CE1FA1(R9) with BNE   TS040110
        label = 'TS040100.2'
        self.assertEqual('EBCFW0', self.seg.nodes[label].field_len.name)
        self.assertEqual('R9', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(0xe0, self.seg.nodes[label].field_len.dsp)
        self.assertEqual(8, self.seg.nodes[label].field_len.length)
        self.assertEqual('EBCFW1', self.seg.nodes[label].field.name)
        self.assertEqual(0xe8, self.seg.nodes[label].field.dsp)
        self.assertEqual('BNE', self.seg.nodes[label].on)
        self.assertEqual('TS040110', self.seg.nodes[label].goes)
        # MVC   EBW000(L'CE1WKA-1),EBW001
        label = 'TS040100.3'
        self.assertEqual('EBW000', self.seg.nodes[label].field_len.name)
        self.assertEqual('R9', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(0x8, self.seg.nodes[label].field_len.dsp)
        self.assertEqual(211, self.seg.nodes[label].field_len.length)
        self.assertEqual('EBW001', self.seg.nodes[label].field.name)
        self.assertEqual(0x9, self.seg.nodes[label].field.dsp)
        self.assertEqual('TS040110', self.seg.nodes[label].fall_down)
        # MVC   23(L'CE1WKA,R3),26(R4)
        label = 'TS040110.1'
        self.assertEqual('R3_AREA', self.seg.nodes[label].field_len.name)
        self.assertEqual('R3', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(23, self.seg.nodes[label].field_len.dsp)
        self.assertEqual(212, self.seg.nodes[label].field_len.length)
        self.assertEqual('R4_AREA', self.seg.nodes[label].field.name)
        self.assertEqual(26, self.seg.nodes[label].field.dsp)
