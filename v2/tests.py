import unittest

from v2.errors import Error
from v2.file_line import Line
from v2.instruction import InstructionType
from v2.macro import SegmentMacro
from v2.segment import Program


class MacroTest(unittest.TestCase):
    NUMBER_OF_FILES = 12

    def setUp(self) -> None:
        self.program = Program()
        self.macro = SegmentMacro(self.program)

    def test_files(self):
        self.assertTrue(self.macro.is_present('WA0AA'))
        self.assertTrue(self.macro.is_present('EB0EB'))
        self.assertFalse(self.macro.is_present('ETA5'))
        self.assertEqual(self.NUMBER_OF_FILES, len(self.macro.global_program.macro.files),
                         'Update number of files in MacroTest')

    def _common_checks(self, macro_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.macro.load(macro_name)
        self.assertListEqual(accepted_errors_list, self.macro.errors, '\n\n\n' + '\n'.join(list(
            set(self.macro.errors) - set(accepted_errors_list))))
        self.assertTrue(self.macro.is_loaded(macro_name))

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
        self.assertEqual(0x2c8, self.macro.data_map['CE1SSQ'].dsp)

    def test_SH0HS(self):
        macro_name = 'SH0HS'
        self._common_checks(macro_name)
        self.assertEqual(20, self.macro.data_map['SH0EQT'].length)
        self.assertEqual(14, self.macro.data_map['SH0CON'].dsp)
        self.assertEqual(0x2a6, self.macro.data_map['SH0SKP'].dsp)
        self.assertEqual(1, self.macro.data_map['SH0SKP'].length)
        self.assertEqual(0x2a8, self.macro.data_map['SH0FLD'].dsp)
        self.assertEqual(0x323, self.macro.data_map['SH0EQT'].dsp)
        self.assertEqual(0x337, self.macro.data_map['SH0SMK'].dsp)
        self.assertEqual(16, self.macro.data_map['SH0SMK'].length)

    def test_PR001W(self):
        macro_name = 'PR001W'
        accepted_errors_list = [
            f"{Error.EXP_INVALID_KEY} #PR001WS:EQU:&SW00WRS {macro_name}",
            f"{Error.EXP_INVALID_KEY_X} #PR001WI:EQU:C'&SW00WID' {macro_name}",
            f"{Error.EXP_INVALID_KEY_X} #PR001WI:EQU:X'&SW00WID' {macro_name}",
        ]
        self._common_checks(macro_name, accepted_errors_list)
        self.assertEqual(0, self.macro.data_map['PR00HDR'].dsp)
        self.assertEqual(0, self.macro.data_map['PR00REC'].dsp)
        self.assertEqual(3, self.macro.data_map['PR00ORG'].dsp)
        self.assertEqual(40, self.macro.data_map['#PR00_00_TYP_040'].dsp)
        self.assertEqual(20, self.macro.data_map['PR00E54'].dsp)
        self.assertEqual(20, self.macro.data_map['#PR00L54'].dsp)
        self.assertEqual(0xd5, self.macro.data_map['#PR00_00_NEWITEM'].dsp)
        self.assertEqual(0x40, self.macro.data_map['#PR00_72_RFIC_NOEMD'].dsp)
        self.assertEqual(0x108 - 0x02d, self.macro.data_map['PR00_D4_HPFPT_GRP'].length)
        self.assertEqual(2, self.macro.data_map['#PR00_X1_TYP1'].length)
        self.assertEqual(4, self.macro.data_map['#PR00_X1_TYP1'].dsp)
        self.assertEqual(6, self.macro.data_map['PR00_X1_PD_EXTDATA'].dsp)

    def test_TR1GAA(self):
        macro_name = 'TR1GAA'
        accepted_errors_list = [
            f"{Error.EXP_INVALID_KEY} #TR1GAAS:EQU:&SW00WRS {macro_name}",
            f"{Error.EXP_INVALID_KEY_X} #TR1GAAI:EQU:C'&SW00WID' {macro_name}",
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
    NUMBER_OF_FILES = 13

    def setUp(self) -> None:
        self.program = Program()
        self.seg = None

    def _common_checks(self, seg_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.program.load(seg_name)
        self.seg = self.program.segments[seg_name]
        self.assertListEqual(accepted_errors_list, self.seg.errors, '\n\n\n' + '\n'.join(list(
            set(self.seg.errors) - set(accepted_errors_list))))
        self.assertTrue(self.seg.assembled)

    def test_files(self):
        self.assertTrue('TS02' in self.program.segments)
        self.assertTrue('TS01' in self.program.segments)
        self.assertFalse('EB0EB' in self.program.segments)
        self.assertEqual(self.NUMBER_OF_FILES, len(self.program.segments), 'Update number of files in SegmentTest')

    def test_field_bits(self):
        seg_name = 'TS01'
        accepted_errors_list = [
            f"{Error.FBD_NO_LEN} TS010010.2:OI:23(2,R9),1 {seg_name}",
            f"{Error.FBD_INVALID_BASE} TS010010.3:OI:EBW000(L'EBW001),1 {seg_name}",
            f"{Error.FBD_INVALID_KEY} TS010010.4:OI:ERROR_FIELD,1 {seg_name}",
            f"{Error.FBD_INVALID_KEY_BASE} TS010010.5:OI:PD0_C_ITM,1 {seg_name}",
            f"{Error.BITS_INVALID_NUMBER} TS010010.7:OI:EBW000,250+250 {seg_name}",
            f"{Error.BITS_INVALID_BIT} TS010010.8:OI:EBW000,#PD0_FLDEMP {seg_name}",
            f"{Error.FBD_INVALID_DSP} TS010010.9:OI:-1(R2),1 {seg_name}",
            f"{Error.FBD_INVALID_DSP} TS010010.10:OI:4096(R2),1 {seg_name}",
        ]
        self.program.macro.load('PD0WRK')
        del self.program.macro.files['PD0WRK']
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
        self.assertEqual(0x008, self.seg.macro.data_map[label].dsp)
        self.assertEqual(2, self.seg.macro.data_map[label].length)
        self.assertEqual('R2', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R14', self.seg.nodes[label].reg2.reg)
        # Check RGA,2 with JNZ TS020010 & it contains a before_goes
        label = 'TS020020'
        self.assertEqual(0x00a, self.seg.macro.data_map[label].dsp)
        self.assertEqual('R2', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R2', self.seg.nodes[label].reg2.reg)
        self.assertEqual('JNZ', self.seg.nodes[label].on)
        self.assertSetEqual({'TS020030', 'TS020040'}, self.seg.nodes[label].next_labels)
        self.assertEqual(5, len(self.seg.nodes[label].conditions))
        # Check 4,R04
        label = 'TS020030'
        self.assertEqual(0x018, self.seg.macro.data_map[label].dsp)
        self.assertEqual('R4', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R4', self.seg.nodes[label].reg2.reg)
        self.assertSetEqual({'TS020040'}, self.seg.nodes[label].next_labels)
        # Check DS    0H
        label = 'TS020040'
        self.assertEqual(0x01a, self.seg.macro.data_map[label].dsp)
        self.assertEqual(label, self.seg.nodes[label].label)
        self.assertEqual('DS', self.seg.nodes[label].command)
        # Check  BCTR  R5,0
        label = 'TS020040.1'
        self.assertEqual('R5', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R0', self.seg.nodes[label].reg2.reg)
        # Check the saved instruction inside TS020020
        label = 'TS020020'
        for condition in self.seg.nodes[label].conditions:
            if not condition.is_check_cc:
                self.assertEqual('R6', condition.reg1.reg)
                self.assertIsNone(condition.fall_down)

    def test_reg_index(self):
        seg_name = 'TS03'
        accepted_errors_list = [
            f"{Error.RFX_INVALID_REG} TS03E010.1:L:R16,EBW000 {seg_name}",
            f"{Error.FBD_INVALID_BASE} TS03E010.2:LA:R1,2(R1,R3,R4) {seg_name}",
            f"{Error.FX_INVALID_INDEX} TS03E010.3:LA:R1,2(ABC,R1) {seg_name}",
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
        self.assertEqual(4095, self.seg.nodes[label].field.dsp)
        self.assertEqual('R0', self.seg.nodes[label].field.index.reg)
        # CH    R15,4(R15)
        label = '$$TS03$$.10'
        self.assertEqual('R15', self.seg.nodes[label].reg.reg)
        self.assertEqual('R15_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R15', self.seg.nodes[label].field.base.reg)
        self.assertEqual(4, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)
        # L     R1,CE1CR1(R3)
        label = '$$TS03$$.11'
        self.assertEqual('R1', self.seg.nodes[label].reg.reg)
        self.assertEqual('CE1CR1', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x170, self.seg.nodes[label].field.dsp)
        self.assertEqual('R3', self.seg.nodes[label].field.index.reg)
        # L     R1,12
        label = '$$TS03$$.12'
        self.assertEqual('R1', self.seg.nodes[label].reg.reg)
        self.assertEqual('R0_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R0', self.seg.nodes[label].field.base.reg)
        self.assertEqual(12, self.seg.nodes[label].field.dsp)
        self.assertIsNone(self.seg.nodes[label].field.index)

    def test_field_variants(self):
        seg_name = 'TS04'
        accepted_errors_list = [
            f"{Error.FL_INVALID_LEN} TS04E100.1:MVC:23(L'CE1WKA+60,R3),26(R4) {seg_name}",
            f"{Error.FL_LEN_REQUIRED} TS04E100.3:OC:EBW000(,R4),EBW000 {seg_name}",
            f"{Error.FL_INVALID_LEN} TS04E200.1:PACK:CE1DCT,10(17,R15) {seg_name}",
            f"{Error.FD_INVALID_DATA} TS04E300.1:MVI:EBW000,256 {seg_name}",
            f"{Error.FD_INVALID_DATA} TS04E300.2:MVI:EBW000,C'AB' {seg_name}",
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
        # Check FieldLenFieldLen
        # PACK  CE1DCT,CE1DET
        label = 'TS040200.1'
        self.assertEqual('CE1DCT', self.seg.nodes[label].field_len1.name)
        self.assertEqual('CE1DET', self.seg.nodes[label].field_len2.name)
        self.assertEqual('R9', self.seg.nodes[label].field_len2.base.reg)
        self.assertEqual(16, self.seg.nodes[label].field_len1.length)
        self.assertEqual(4, self.seg.nodes[label].field_len2.length)
        self.assertEqual(0x374, self.seg.nodes[label].field_len1.dsp)
        self.assertEqual(0x370, self.seg.nodes[label].field_len2.dsp)
        # UNPK  EBW008-EBW000(L'CE1FA1,R3),10(16,R15)
        label = 'TS040200.2'
        self.assertEqual('R3_AREA', self.seg.nodes[label].field_len1.name)
        self.assertEqual('R15_AREA', self.seg.nodes[label].field_len2.name)
        self.assertEqual('R15', self.seg.nodes[label].field_len2.base.reg)
        self.assertEqual(4, self.seg.nodes[label].field_len1.length)
        self.assertEqual(16, self.seg.nodes[label].field_len2.length)
        self.assertEqual(8, self.seg.nodes[label].field_len1.dsp)
        self.assertEqual(10, self.seg.nodes[label].field_len2.dsp)
        # Check FieldData
        # CLI   EBW000,#$BCLASS with BNE   TS040310
        label = 'TS040300.1'
        self.assertEqual('EBW000', self.seg.nodes[label].field.name)
        self.assertEqual(0xC2, self.seg.nodes[label].data)
        self.assertEqual('BNE', self.seg.nodes[label].on)
        self.assertEqual('TS040310', self.seg.nodes[label].goes)
        # MVI   23(R4),L'CE1WKA
        label = 'TS040300.2'
        self.assertEqual('R4_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R4', self.seg.nodes[label].field.base.reg)
        self.assertEqual(23, self.seg.nodes[label].field.dsp)
        self.assertEqual(212, self.seg.nodes[label].data)

    def test_reg_variants(self):
        seg_name = 'TS05'
        accepted_errors_list = [
            f"{Error.REG_INVALID} TS05E100.1:LHI:RAB,1 {seg_name}",
            f"{Error.RD_INVALID_NUMBER} TS05E100.3:LHI:R1,X'10000' {seg_name}",
            f"{Error.RD_INVALID_NUMBER} TS05E100.4:LHI:R1,65536 {seg_name}",
            f"{Error.REG_INVALID} TS05E200.1:STM:R14,R16,EBW000 {seg_name}",
            f"{Error.REG_INVALID} TS05E200.2:LM:RDC,R7,EBW000 {seg_name}",
            f"{Error.FBD_INVALID_KEY} TS05E200.3:LM:R0,R1,PD0_C_ITM {seg_name}",
            f"{Error.FBD_INVALID_DSP} TS05E200.4:STM:R3,R4,4096(R7) {seg_name}",
            f"{Error.REG_INVALID} TS05E300.1:ICM:R16,1,EBW000 {seg_name}",
            f"{Error.RDF_INVALID_DATA} TS05E300.2:STCM:R1,-1,EBW000 {seg_name}",
            f"{Error.RDF_INVALID_DATA} TS05E300.3:ICM:R1,16,EBW000 {seg_name}",
            f"{Error.RDF_INVALID_DATA} TS05E300.4:STCM:R1,0,EBW000 {seg_name}",
            f"{Error.FBD_INVALID_DSP} TS05E300.5:ICM:R1,7,-1(R9) {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        self.assertRaises(ValueError, InstructionType.from_line, Line.from_line(" AHI R1,1,3"), self.seg.macro)
        self.assertRaises(ValueError, InstructionType.from_line, Line.from_line(" LHI R1"), self.seg.macro)
        self.assertRaises(ValueError, InstructionType.from_line, Line.from_line(" STM R1,R2,B,C"), self.seg.macro)
        self.assertRaises(ValueError, InstructionType.from_line, Line.from_line(" LM R1,R2"), self.seg.macro)
        self.assertRaises(ValueError, InstructionType.from_line, Line.from_line(" ICM R1,1"), self.seg.macro)
        self.assertRaises(ValueError, InstructionType.from_line, Line.from_line(" STCM R1"), self.seg.macro)
        # Check RegisterData
        # AHI   R15,SUIFF with BP    TS050110
        label = 'TS050100.1'
        self.assertEqual('R15', self.seg.nodes[label].reg.reg)
        self.assertEqual(0xff, self.seg.nodes[label].data)
        self.assertEqual('BP', self.seg.nodes[label].on)
        self.assertEqual('TS050110', self.seg.nodes[label].goes)
        # AHI   R15,X'00'
        label = 'TS050100.2'
        self.assertEqual('R15', self.seg.nodes[label].reg.reg)
        self.assertEqual(0, self.seg.nodes[label].data)
        self.assertEqual('TS050110', self.seg.nodes[label].fall_down)
        # LHI   R13,-1
        label = 'TS050110.1'
        self.assertEqual('R13', self.seg.nodes[label].reg.reg)
        self.assertEqual(-1, self.seg.nodes[label].data)
        # LHI   R05,X'7FFF'+1
        label = 'TS050110.2'
        self.assertEqual('R5', self.seg.nodes[label].reg.reg)
        self.assertEqual(-32768, self.seg.nodes[label].data)
        # LHI   RG1,32767
        label = 'TS050110.3'
        self.assertEqual('R1', self.seg.nodes[label].reg.reg)
        self.assertEqual(32767, self.seg.nodes[label].data)
        # Check RegisterRegisterField
        # STM   R14,R7,656(R9)
        label = 'TS050200.1'
        self.assertEqual('R14', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R7', self.seg.nodes[label].reg2.reg)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x290, self.seg.nodes[label].field.dsp)
        self.assertEqual('CE1CTRS', self.seg.nodes[label].field.name)
        # LM    RDB,RGF,CE1DSTMP
        label = 'TS050200.2'
        self.assertEqual('R14', self.seg.nodes[label].reg1.reg)
        self.assertEqual('R7', self.seg.nodes[label].reg2.reg)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x290, self.seg.nodes[label].field.dsp)
        self.assertEqual('CE1DSTMP', self.seg.nodes[label].field.name)
        # Check RegisterDataField
        # ICM   R3,B'0001',EBW000
        label = 'TS050300.1'
        self.assertEqual('R3', self.seg.nodes[label].reg.reg)
        self.assertEqual(1, self.seg.nodes[label].data)
        self.assertEqual('EBW000', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(8, self.seg.nodes[label].field.dsp)
        # STCM  R3,B'1111',10(R9)
        label = 'TS050300.2'
        self.assertEqual(15, self.seg.nodes[label].data)
        self.assertEqual('EBW002', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(10, self.seg.nodes[label].field.dsp)
        # ICM   R3,3,EBW000
        label = 'TS050300.3'
        self.assertEqual(3, self.seg.nodes[label].data)
        # STCM  R3,B'1000',EBW000
        label = 'TS050300.4'
        self.assertEqual(8, self.seg.nodes[label].data)

    def test_branch_condition(self):
        seg_name = 'TS06'
        accepted_errors_list = [
            f"{Error.BC_INVALID_MASK} TS06E100.1:JC:-1,TS06E100 {seg_name}",
            f"{Error.BC_INVALID_MASK} TS06E100.2:BC:12,TS06E100 {seg_name}",
            f"{Error.BC_INDEX} TS06E100.3:B:TS06E100(R14) {seg_name}",
            f"{Error.FX_INVALID_INDEX} TS06E100.4:JC:14,TS06E100(-1) {seg_name}",
            f"{Error.BC_INVALID_BRANCH} TS06E100.5:BNZ:0(R8) {seg_name}",
            f"{Error.FBD_INVALID_KEY} TS06E100.6:JE:TS061000 {seg_name}",
        ]
        # self.assertRaises(ValueError, ins.BranchCondition.from_operand, None, 'BC', 'TS060100', self.program.macro)
        # self.assertRaises(ValueError, ins.BranchCondition.from_operand, None, 'JC', 'A,TS060100', self.program.macro)
        self._common_checks(seg_name, accepted_errors_list)
        # Check TS060100
        node = self.seg.nodes['TS060100.1']
        # LTR  R1, R1 with multiple goes
        self.assertEqual('LTR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        self.assertSetEqual({'TS060120', 'TS060100.2', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060100.2', node.fall_down)
        self.assertEqual('JNZ', node.on)
        self.assertEqual('TS060120', node.goes)
        # LR    R2,R3
        self.assertEqual('LR', node.conditions[0].command)
        self.assertEqual('R2', node.conditions[0].reg1.reg)
        self.assertEqual('R3', node.conditions[0].reg2.reg)
        # JNZ   TS060120
        self.assertEqual('JNZ', node.conditions[1].command)
        self.assertEqual('TS060120', node.conditions[1].branch.name)
        self.assertEqual(7, node.conditions[1].mask)
        self.assertIsNone(node.conditions[1].branch.index)
        # LR    R3,R4
        self.assertEqual('R3', node.conditions[2].reg1.reg)
        self.assertEqual('R4', node.conditions[2].reg2.reg)
        # JP    TS060130
        self.assertEqual('JP', node.conditions[3].command)
        self.assertEqual('TS060130', node.conditions[3].branch.name)
        self.assertEqual(2, node.conditions[3].mask)
        node = self.seg.nodes['TS060100.2']
        # LR    R5,R6
        self.assertEqual('R5', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # Check TS060110
        node = self.seg.nodes['TS060110.1']
        # LTR  R2, R2 with a single goes
        self.assertEqual('R2', node.reg2.reg)
        self.assertSetEqual({'TS060110.2', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060110.2', node.fall_down)
        self.assertEqual('BNE', node.on)
        self.assertEqual('TS060130', node.goes)
        # LR    R2,R3
        self.assertEqual('R2', node.conditions[0].reg1.reg)
        self.assertEqual('R3', node.conditions[0].reg2.reg)
        # JC    7,TS060130
        self.assertEqual('BNE', node.conditions[1].command)
        self.assertEqual('TS060130', node.conditions[1].branch.name)
        self.assertEqual(7, node.conditions[1].mask)
        # LR    R3,R4
        node = self.seg.nodes['TS060110.2']
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # J     TS060100
        node = self.seg.nodes['TS060110.3']
        self.assertEqual('J', node.command)
        self.assertEqual('TS060100', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertSetEqual({'TS060100'}, node.next_labels)
        self.assertIsNone(node.fall_down)
        self.assertEqual('J', node.on)
        self.assertEqual('TS060100', node.goes)
        # Check TS060120
        node = self.seg.nodes['TS060120.1']
        # LTR   R3,R3 with a single goes
        self.assertEqual('R3', node.reg2.reg)
        self.assertSetEqual({'TS060120.2', 'TS060110'}, node.next_labels)
        self.assertEqual('TS060120.2', node.fall_down)
        self.assertEqual('BE', node.on)
        self.assertEqual('TS060110', node.goes)
        # BC    8,TS060110
        self.assertEqual('BE', node.conditions[0].command)
        self.assertEqual('TS060110', node.conditions[0].branch.name)
        self.assertEqual(8, node.conditions[0].mask)
        # AR    R5,R2 with a single goes
        node = self.seg.nodes['TS060120.2']
        self.assertEqual('R2', node.reg2.reg)
        self.assertSetEqual({'TS060120', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060130', node.fall_down)
        self.assertEqual('BH', node.on)
        self.assertEqual('TS060120', node.goes)
        # LR    R2,R4
        self.assertEqual('R2', node.conditions[0].reg1.reg)
        self.assertEqual('R4', node.conditions[0].reg2.reg)
        # BC    2,TS060120
        self.assertEqual('BH', node.conditions[1].command)
        self.assertEqual('TS060120', node.conditions[1].branch.name)
        self.assertEqual(2, node.conditions[1].mask)
        # Check TS060130
        node = self.seg.nodes['TS060130.1']
        # LTR   R4,R4 with single goes
        self.assertEqual('R4', node.reg2.reg)
        self.assertSetEqual({'TS060100', 'TS060130.2'}, node.next_labels)
        self.assertEqual('TS060130.2', node.fall_down)
        self.assertEqual('BNO', node.on)
        self.assertEqual('TS060100', node.goes)
        # BNO   TS060100
        self.assertEqual('BNO', node.conditions[0].command)
        self.assertEqual('TS060100', node.conditions[0].branch.name)
        self.assertEqual(14, node.conditions[0].mask)
        # JC    15,TS060120
        node = self.seg.nodes['TS060130.2']
        self.assertEqual('B', node.command)
        self.assertEqual('TS060120', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertSetEqual({'TS060120'}, node.next_labels)
        self.assertIsNone(node.fall_down)
        self.assertEqual('B', node.on)
        self.assertEqual('TS060120', node.goes)
        # BC    15,TS060120
        node = self.seg.nodes['TS060130.4']
        self.assertEqual('B', node.command)
        self.assertEqual('TS060120', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertSetEqual({'TS060120'}, node.next_labels)
        self.assertIsNone(node.fall_down)
        self.assertEqual('B', node.on)
        self.assertEqual('TS060120', node.goes)
        # LR    R3,R5
        node = self.seg.nodes['TS060130.5']
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R5', node.reg2.reg)
        # BACKC
        node = self.seg.nodes['TS060130.6']
        self.assertEqual('BACKC', node.command)
        # B     TS060100
        node = self.seg.nodes['TS060130.7']
        self.assertEqual('B', node.command)
        self.assertEqual('TS060100', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertSetEqual({'TS060100'}, node.next_labels)
        self.assertIsNone(node.fall_down)
        self.assertEqual('B', node.on)
        self.assertEqual('TS060100', node.goes)
        # Check TS060140
        # BC    0,TS060130
        node = self.seg.nodes['TS060140.2']
        self.assertEqual('JNOP', node.command)
        self.assertIsNone(node.branch)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.3'}, node.next_labels)
        self.assertEqual('TS060140.3', node.fall_down)
        self.assertIsNone(node.goes)
        self.assertEqual('JNOP', node.on)
        # NOP   TS060130
        node = self.seg.nodes['TS060140.4']
        self.assertEqual('NOP', node.command)
        self.assertIsNone(node.branch)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.5'}, node.next_labels)
        self.assertEqual('TS060140.5', node.fall_down)
        # JC    0,TS060130
        node = self.seg.nodes['TS060140.6']
        self.assertEqual('JNOP', node.command)
        self.assertIsNone(node.branch)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.7'}, node.next_labels)
        self.assertEqual('TS060140.7', node.fall_down)
        # JNOP  TS060130
        node = self.seg.nodes['TS060140.8']
        self.assertEqual('JNOP', node.command)
        self.assertIsNone(node.branch)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS06E100'}, node.next_labels)
        self.assertEqual('TS06E100', node.fall_down)

    def test_constant(self):
        seg_name = 'TS07'
        accepted_errors_list = [
            f"{Error.EQU_LABEL_REQUIRED} None:EQU:23 {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        label = 'TS070010'
        self.assertEqual(0x008, self.seg.macro.data_map[label].dsp)
        self.assertEqual(1, self.seg.macro.data_map[label].length)
        self.assertEqual('TS07', self.seg.macro.data_map[label].name)
        label = 'TS070020'
        self.assertEqual(0x018, self.seg.macro.data_map[label].dsp)
        self.assertEqual(4, self.seg.macro.data_map[label].length)
        # Constant
        self.assertEqual(0x018, self.seg.constant.start)
        # C'CLASS'
        label = 'NAME'
        self.assertEqual(0x018, self.seg.macro.data_map[label].dsp)
        self.assertEqual(5, self.seg.macro.data_map[label].length)
        class_name = bytearray([0xC3, 0xD3, 0xC1, 0xE2, 0xE2])
        at = 0x018 - self.seg.constant.start
        self.assertEqual(class_name, self.seg.constant.data[at: at+5])
        self.assertEqual(class_name, self.seg.get_constant_bytes(label))
        # 2C'NAM'
        label = 'EXAM'
        self.assertEqual(0x01d, self.seg.macro.data_map[label].dsp)
        self.assertEqual(3, self.seg.macro.data_map[label].length)
        exam_name = bytearray([0xD5, 0xC1, 0xD4, 0xD5, 0xC1, 0xD4])
        self.assertEqual(exam_name, self.seg.get_constant_bytes(label, len(exam_name)))
        # A(NAME)
        label = 'ADR1'
        self.assertEqual(0x024, self.seg.macro.data_map[label].dsp)
        self.assertEqual(4, self.seg.macro.data_map[label].length)
        self.assertEqual(bytearray(int(24).to_bytes(4, 'big')), self.seg.get_constant_bytes(label))
        self.assertEqual(bytearray(int(24).to_bytes(5, 'big')), self.seg.constant.data[0x00B: 0x010])
        # Y(EXAM-NAME)
        label = 'ADR2'
        self.assertEqual(0x028, self.seg.macro.data_map[label].dsp)
        self.assertEqual(2, self.seg.macro.data_map[label].length)
        self.assertEqual(bytearray(int(5).to_bytes(2, 'big')), self.seg.get_constant_bytes(label))
        # CHAR1    DC    C'ASDC'
        self.assertEqual(bytearray([0xC1, 0xE2, 0xC4, 0xC3]), self.seg.get_constant_bytes('CHAR1'))
        # CHAR2    DC    CL6'ASDC'
        self.assertEqual(bytearray([0xC1, 0xE2, 0xC4, 0xC3, 0x40, 0x40]), self.seg.get_constant_bytes('CHAR2'))
        # CHAR3    DC    CL2'ASDC'
        self.assertEqual(bytearray([0xC1, 0xE2]), self.seg.get_constant_bytes('CHAR3'))
        # HEX1     DC    X'E'
        self.assertEqual(bytearray([0x0E]), self.seg.get_constant_bytes('HEX1'))
        # HEX2     DC    XL4'FACE'
        self.assertEqual(bytearray([0x00, 0x00, 0xFA, 0xCE]), self.seg.get_constant_bytes('HEX2'))
        # HEX3     DC    XL1'4243'
        self.assertEqual(bytearray([0x43]), self.seg.get_constant_bytes('HEX3'))
        # BIN1     DC    BL5'0100'
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x00, 0x04]), self.seg.get_constant_bytes('BIN1'))
        # BIN2     DC    BL1'101010'
        self.assertEqual(bytearray([0x2A]), self.seg.get_constant_bytes('BIN2'))
        # ZON1     DC    Z'6940'
        self.assertEqual(bytearray([0xF6, 0xF9, 0xF4, 0xC0]), self.seg.get_constant_bytes('ZON1'))
        # ZON2     DC    ZL1'-555'
        self.assertEqual(bytearray([0xD5]), self.seg.get_constant_bytes('ZON2'))
        # ZON3     DC    ZL5'555'
        self.assertEqual(bytearray([0xF0, 0xF0, 0xF5, 0xF5, 0xC5]), self.seg.get_constant_bytes('ZON3'))
        # PCK1     DC    P'1234'
        self.assertEqual(bytearray([0x01, 0x23, 0x4C]), self.seg.get_constant_bytes('PCK1'))
        # PCK2     DC    PL2'-12345678'
        self.assertEqual(bytearray([0x67, 0x8D]), self.seg.get_constant_bytes('PCK2'))
        # FULL1    DC    F'2000'
        self.assertEqual(bytearray([0x00, 0x00, 0x07, 0xD0]), self.seg.get_constant_bytes('FULL1'))
        self.assertEqual(bytearray([0x8D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07]), self.seg.constant.data[56: 63])
        # FULL2    DC    FL2'100.7'
        self.assertEqual(bytearray([0x00, 0x65]), self.seg.get_constant_bytes('FULL2'))
        # HALF1    DC    H'2000'
        self.assertEqual(bytearray([0x07, 0xD0]), self.seg.get_constant_bytes('HALF1'))
        # HALF2    DC    H'-2'
        self.assertEqual(bytearray([0xFF, 0xFE]), self.seg.get_constant_bytes('HALF2'))
        self.assertEqual(bytearray([0xFF, 0xFE]), self.seg.constant.data[68: 70])
        # FLV      DC    PL2'-29'
        self.assertEqual(bytearray([0x02, 0x9D]), self.seg.get_constant_bytes('FLV'))
        # FLW      DC    Z'246'
        self.assertEqual(bytearray([0xF2, 0xF4, 0xC6]), self.seg.get_constant_bytes('FLW'))
        # FLX      DC    FL5'-1'
        self.assertEqual(bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF]), self.seg.get_constant_bytes('FLX'))
        # FLY      DC    PL2'4096'
        self.assertEqual(bytearray([0x09, 0x6C]), self.seg.get_constant_bytes('FLY'))
        # FLZ      DC    ZL2'-29'
        self.assertEqual(bytearray([0xF2, 0xD9]), self.seg.get_constant_bytes('FLZ'))
        # FLU      DC    C'-29'
        self.assertEqual(bytearray([0x60, 0xF2, 0xF9]), self.seg.get_constant_bytes('FLU'))

    def test_dsect(self):
        seg_name = 'TS08'
        accepted_errors_list = [
        ]
        self._common_checks(seg_name, accepted_errors_list)
        self.assertEqual(48, self.seg.macro.data_map['TS08IND'].dsp)
        self.assertEqual('TS08BLK', self.seg.macro.data_map['TS08IND'].name)
        self.assertEqual(0x80, self.seg.macro.data_map['#ELIGIND'].dsp)
        self.assertEqual(56, self.seg.macro.data_map['TS08FQ'].dsp)
        self.assertEqual(256, self.seg.macro.data_map['TS08REC'].length)
        self.assertEqual(64, self.seg.macro.data_map['TS08REC'].dsp)
        self.assertEqual(64, self.seg.macro.data_map['TS08ITM'].dsp)
        self.assertEqual(64, self.seg.macro.data_map['TS08AAC'].dsp)
        self.assertEqual(0, self.seg.macro.data_map['TS08PGR'].dsp)
        self.assertEqual('TS08AWD', self.seg.macro.data_map['TS08PGR'].name)
        self.assertEqual(30, self.seg.macro.data_map['TS080010'].dsp)
        self.assertEqual('R9', self.seg.nodes['$$TS08$$.1'].field.base.reg)
        self.assertEqual('R1', self.seg.nodes['$$TS08$$.3'].field.base.reg)
        self.assertEqual('WA0ET4', self.seg.nodes['$$TS08$$.3'].field.name)
        self.assertEqual(0x10, self.seg.nodes['$$TS08$$.3'].bits.value)
        self.assertTrue(self.seg.nodes['$$TS08$$.3'].bits.bit_by_name('#WA0TTY').on)
        self.assertEqual('R14', self.seg.nodes['$$TS08$$.4'].field_len.base.reg)
        self.assertEqual(2, self.seg.nodes['$$TS08$$.4'].field_len.length)
        self.assertEqual('R8', self.seg.nodes['$$TS08$$.4'].field.base.reg)
        self.assertEqual(0, self.seg.nodes['$$TS08$$.4'].field.dsp - self.seg.constant.start)
        self.assertEqual(bytearray([0xC1, 0xC1]), self.seg.get_constant_bytes('$C_AA'))
        self.assertEqual('TS08AAC', self.seg.nodes['TS080010.1'].field_len.name)
        self.assertEqual('R14', self.seg.nodes['TS080010.1'].field_len.base.reg)
        self.assertEqual(2, self.seg.nodes['TS080010.1'].field_len.length)
        self.assertEqual('R1', self.seg.nodes['TS080010.1'].field.base.reg)
        self.assertEqual('R14', self.seg.nodes['TS080010.2'].field_len.base.reg)
        self.assertEqual(256, self.seg.nodes['TS080010.2'].field_len.length)
        self.assertEqual('R8', self.seg.nodes['TS080010.2'].field.base.reg)
        self.assertEqual(bytearray([0x00]*256), self.seg.get_constant_bytes('$X_00'))
        self.assertEqual('R2', self.seg.nodes['TS080010.3'].field.base.reg)
        self.assertEqual('R1', self.seg.nodes['TS080010.4'].field.base.reg)
        self.assertEqual('R14', self.seg.nodes['TS080010.5'].field.base.reg)

    def test_subroutine(self):
        seg_name = 'TS09'
        accepted_errors_list = [
            f"{Error.REG_INVALID} TS09E100.1:BAS:R16,TS09S100 {seg_name}",
            f"{Error.REG_INVALID} TS09E100.2:BR:-1 {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # BAS   R4,TS09S100
        node = self.seg.nodes['TS090010.1']
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('TS09S100', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        # JAS   R2,TS09S100
        node = self.seg.nodes['TS090010.2']
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual('TS09S200', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        # LTR   R1,R1 with BZR   R4
        node = self.seg.nodes['TS09S100.1']
        self.assertIsNone(node.goes)
        self.assertEqual({'TS09S100.2'}, node.next_labels)
        self.assertEqual('BZR', node.conditions[0].on)
        self.assertEqual('R4', node.conditions[0].reg.reg)
        self.assertEqual(8, node.conditions[0].mask)
        self.assertIsNone(node.conditions[0].goes)
        # AHI   R2,1
        self.assertEqual('AHI', self.seg.nodes['TS09S100.2'].command)
        # LTR   R1,R1
        self.assertEqual('LTR', self.seg.nodes['TS09S100.3'].command)
        # NOPR  0
        node = self.seg.nodes['TS09S100.4']
        self.assertEqual('NOPR', node.command)
        self.assertIsNone(node.goes)
        self.assertEqual({'TS09S100.5'}, node.next_labels)
        self.assertEqual('NOPR', node.on)
        self.assertEqual('R0', node.reg.reg)
        self.assertEqual(0, node.mask)
        # AHI   R2,1
        self.assertEqual('AHI', self.seg.nodes['TS09S100.5'].command)
        # BR    R4
        node = self.seg.nodes['TS09S100.6']
        self.assertEqual('BR', node.command)
        self.assertIsNone(node.goes)
        self.assertEqual(set(), node.next_labels)
        self.assertEqual('BR', node.on)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual(15, node.mask)
        # BCR   0,R2
        node = self.seg.nodes['TS09S200.1']
        self.assertEqual('NOPR', node.command)
        self.assertIsNone(node.goes)
        self.assertEqual({'TS09S200.2'}, node.next_labels)
        self.assertEqual('NOPR', node.on)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(0, node.mask)
        # BCR   15,R2
        node = self.seg.nodes['TS09S200.2']
        self.assertEqual('BR', node.command)
        self.assertIsNone(node.goes)
        self.assertEqual(set(), node.next_labels)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(15, node.mask)
        # BCR   8,R2
        node = self.seg.nodes['TS09S200.3']
        self.assertIsNone(node.goes)
        self.assertEqual({'TS09S200.4'}, node.next_labels)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual('BER', node.on)
        self.assertEqual(8, node.mask)

    def test_seg_calls(self):
        seg_name = 'TS10'
        accepted_errors_list = [
            f"{Error.SC_INVALID_SEGMENT} TS10E100.1:ENTRC:A000 {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # ENTRC TS01
        node = self.seg.nodes['$$TS10$$.1']
        seg = self.program.segments[node.seg_name]
        self.assertEqual('ENTRC', node.command)
        self.assertEqual('TS01', node.seg_name)
        self.assertEqual('$$TS01$$', node.branch.name)
        self.assertIn('$$TS01$$', seg.macro.data_map)
        self.assertIn('OI', seg.nodes['$$TS01$$.1'].command)
        self.assertEqual('$$TS01$$', node.goes)
        self.assertSetEqual({'$$TS01$$', '$$TS10$$.2'}, node.next_labels)
        # ENTNC TS02
        node = self.seg.nodes['$$TS10$$.2']
        seg = self.program.segments[node.seg_name]
        self.assertEqual('ENTNC', node.command)
        self.assertEqual('TS02', node.seg_name)
        self.assertEqual('$$TS02$$', node.branch.name)
        self.assertIn('$$TS02$$', seg.macro.data_map)
        self.assertIn('SR', seg.nodes['TS020010'].command)
        self.assertEqual('$$TS02$$', node.goes)
        self.assertSetEqual({'$$TS02$$'}, node.next_labels)
        # ENTDC TS03
        node = self.seg.nodes['$$TS10$$.3']
        seg = self.program.segments[node.seg_name]
        self.assertEqual('ENTDC', node.command)
        self.assertEqual('TS03', node.seg_name)
        self.assertEqual('$$TS03$$', node.branch.name)
        self.assertIn('$$TS03$$', seg.macro.data_map)
        self.assertIn('L', seg.nodes['$$TS03$$.1'].command)
        self.assertEqual('$$TS03$$', node.goes)
        self.assertSetEqual({'$$TS03$$'}, node.next_labels)

    def test_key_value(self):
        seg_name = 'TS11'
        accepted_errors_list = [
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # AAGET BASEREG=R1,GET=CORE,INIT=YES,FILE=NO
        node = self.seg.nodes['TS110010.1']
        self.assertEqual('AAGET', node.command)
        self.assertTrue(node.is_key('BASEREG'))
        self.assertEqual('YES', node.get_value('INIT'))
        self.assertEqual('BASEREG', node.get_key_from_value('R1')[0])
        self.assertSetEqual({'BASEREG', 'GET', 'INIT', 'FILE'}, node.keys)
        self.assertDictEqual({'BASEREG': 'R1', 'GET': 'CORE', 'INIT': 'YES', 'FILE': 'NO'}, node.items)
        self.assertSetEqual({'TS110010.2'}, node.next_labels)
        self.assertIsNone(node.goes)
        # GETCC D5,L4,FILL=00
        node = self.seg.nodes['TS110010.2']
        self.assertEqual('GETCC', node.command)
        self.assertTrue(node.is_key('L4'))
        self.assertIsNone(node.get_value('L4'))
        self.assertListEqual(['FILL'], node.get_key_from_value('00'))
        self.assertSetEqual({'D5', 'L4', 'FILL'}, node.keys)
        self.assertDictEqual({'D5': None, 'L4': None, 'FILL': '00'}, node.items)
        self.assertSetEqual({'TS110010.3'}, node.next_labels)
        self.assertIsNone(node.goes)
        # PNRCC ACTION=CRLON,REG=R4
        node = self.seg.nodes['TS110010.3']
        self.assertEqual('PNRCC', node.command)
        self.assertTrue(node.is_key('REG'))
        self.assertEqual('CRLON', node.get_value('ACTION'))
        self.assertEqual('REG', node.get_key_from_value('R4')[0])
        self.assertSetEqual({'ACTION', 'REG'}, node.keys)
        self.assertEqual(2, len(node.items))
        # MODEC REG=R14,MODE=31
        node = self.seg.nodes['TS110020.1']
        self.assertEqual('MODEC', node.command)
        self.assertTrue(node.is_key('REG'))
        self.assertEqual('31', node.get_value('MODE'))
        self.assertEqual('REG', node.get_key_from_value('R14')[0])
        self.assertSetEqual({'TS110020.2'}, node.next_labels)
        # GLOBZ REGR=R15
        node = self.seg.nodes['TS110020.2']
        self.assertEqual('R15', node.get_value('REGR'))
        # DETAC D8,CHECK=NO
        node = self.seg.nodes['TS110020.3']
        self.assertListEqual(['D8'], node.key_only)
        # DBOPN REF=TR1GAA,REG=R4
        node = self.seg.nodes['TS110030.1']
        self.assertTrue(node.is_key('REF'))
        # DBRED REF=TR1GAA,REG=R4,BEGIN,KEY1=(PKY=#TR1GK40), ... several more options
        node = self.seg.nodes['TS110030.2']
        self.assertEqual('DBRED', node.command)
        self.assertTrue(node.is_key('KEY5'))
        self.assertDictEqual({'PKY': '#TR1GK40'}, node.get_value('KEY1'))
        self.assertEqual('ERRORA', node.get_key_from_value('TS110020')[0])
        self.assertSetEqual({'KEY1', 'KEY2', 'KEY3', 'KEY4', 'KEY5'}, node.sub_keys)
        self.assertEqual('TR1G_40_ACSTIERCODE', node.items['KEY3']['R'])
        self.assertEqual('$C_AA', node.items['KEY2']['S'])
        self.assertEqual('LE', node.items['KEY4']['C'])
        self.assertSetEqual({'TS110030.3', 'TS110020'}, node.next_labels)
        self.assertEqual('TS110020', node.goes)
        # PDCLS WORKAREA=(LEV,5)
        node = self.seg.nodes['TS110030.3']
        self.assertSetEqual({'WORKAREA'}, node.sub_keys)
        self.assertIsNone(node.items['WORKAREA']['LEV'])
        self.assertDictEqual({'LEV': None, '5': None}, node.items['WORKAREA'])
        self.assertEqual('WORKAREA', node.get_key_from_value({'LEV': None, '5': None})[0])
        # ATTAC DA
        self.assertTrue(self.seg.nodes['TS110040.1'].is_key('DA'))
        # RELCC D5
        self.assertSetEqual({'D5'}, self.seg.nodes['TS110040.2'].keys)
        # CRUSA S0=5,S1=E
        self.assertSetEqual({'S0', 'S1'}, self.seg.nodes['TS110040.3'].keys)
        self.assertEqual('E', self.seg.nodes['TS110040.3'].items['S1'])
        # PDRED FIELD=NAME,WORKAREA=(LEV,5),NOTFOUND=TS110060,ERROR=TS110070,FORMATOUT=UNPACKED,SEARCH1=ACT
        node = self.seg.nodes['TS110050.1']
        self.assertSetEqual({'FIELD', 'WORKAREA', 'NOTFOUND', 'ERROR', 'FORMATOUT', 'SEARCH1'}, node.keys)
        self.assertSetEqual({'WORKAREA'}, node.sub_keys)
        self.assertTrue(node.is_sub_key('WORKAREA'))
        self.assertFalse(node.is_sub_key('FIELD'))
        self.assertFalse(node.is_sub_key('INVALID_KEY'))
        self.assertIsNone(node.items['WORKAREA']['5'])
        self.assertSetEqual({'TS110050.2', 'TS110060', 'TS110070'}, node.next_labels)
        self.assertEqual('TS110060', node.goes)
        # SYSRA P1=R,P2=021014
        self.assertDictEqual({'P1': 'R', 'P2': '021014'}, self.seg.nodes['TS110050.2'].items)
        # SENDA MSG='MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'",
                         self.seg.nodes['TS110060'].items['MSG'])
        self.assertSetEqual(set(), self.seg.nodes['TS110060'].next_labels)
        # CFCMA ALLOCATE,SREF=TS11PDWK,REG=R4,SIZE=4096,FILL=00,ERROR=TS110050
        node = self.seg.nodes['TS110060.1']
        self.assertEqual('CFCMA', node.command)
        self.assertTrue(node.is_key('ALLOCATE'))
        self.assertEqual('TS11PDWK', node.get_value('SREF'))
        self.assertEqual('SIZE', node.get_key_from_value('4096')[0])
        self.assertSetEqual({'ALLOCATE', 'SREF', 'REG', 'SIZE', 'FILL', 'ERROR'}, node.keys)
        self.assertEqual(6, len(node.items))
        self.assertSetEqual({'TS110050', 'TS110060.2'}, node.next_labels)
        self.assertEqual('TS110050', node.goes)
        # SERRC R,19000
        self.assertListEqual(['R', '19000'], self.seg.nodes['TS110060.2'].key_only)
        self.assertListEqual(list(), self.seg.nodes['TS110060.2'].get_key_from_value('Invalid value'))
        # DBCLS REF=PD0_DF_REFX,FILE=PR001W
        self.assertEqual('PR001W', self.seg.nodes['TS110070.1'].items['FILE'])
        # DBIFB REF=PD0_DF_REF,NEWREF=WPSGPNRF,FILE=PR001W,ERRORA=TS110060
        node = self.seg.nodes['TS110070.2']
        self.assertEqual('DBIFB', node.command)
        self.assertTrue(node.is_key('NEWREF'))
        self.assertEqual('PD0_DF_REF', node.get_value('REF'))
        self.assertEqual(list(), node.key_only)
        self.assertSetEqual({'REF', 'NEWREF', 'FILE', 'ERRORA', }, node.keys)
        self.assertEqual(4, len(node.items))
        self.assertSetEqual({'TS110060'}, node.next_labels)
        self.assertEqual('TS110060', node.goes)

    def test_other_instruction(self):
        seg_name = 'TS12'
        accepted_errors_list = [
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # LH    R1,FNAME(R2)
        node = self.seg.nodes['TS120100.1']
        self.assertEqual('LH', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual('FNAME', node.field.name)
        self.assertEqual('R2', node.field.index.reg)
        self.assertEqual('R3', node.field.base.reg)
        self.assertEqual(0x090, node.field.dsp)
        self.assertEqual(8, self.seg.macro.data_map['FNAME'].length)
        # LPR   R1,R3
        node = self.seg.nodes['TS120100.2']
        self.assertEqual('LPR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # LNR   R2,R2
        node = self.seg.nodes['TS120100.3']
        self.assertEqual('LNR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R2', node.reg2.reg)
        # LCR   R2,R1
        node = self.seg.nodes['TS120100.4']
        self.assertEqual('LCR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        # A     R5,FWDA
        node = self.seg.nodes['TS120200.1']
        self.assertEqual('A', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('FWDA', node.field.name)
        self.assertIsNone(node.field.index)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x008, node.field.dsp)
        self.assertEqual(4, self.seg.macro.data_map['FWDA'].length)
        # AH    R1,HWD
        node = self.seg.nodes['TS120200.2']
        self.assertEqual('AH', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual('HWD', node.field.name)
        self.assertIsNone(node.field.index)
        self.assertEqual('R3', node.field.base.reg)
        self.assertEqual(0x090, node.field.dsp)
        self.assertEqual(2, self.seg.macro.data_map['HWD'].length)
        # S     R5,FWD(R15)
        node = self.seg.nodes['TS120200.3']
        self.assertEqual('S', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R15', node.field.index.reg)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        self.assertEqual(4, self.seg.macro.data_map['FWD'].length)
        # SH    R4,HWDA
        node = self.seg.nodes['TS120200.4']
        self.assertEqual('SH', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('HWDA', node.field.name)
        self.assertIsNone(node.field.index)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x00c, node.field.dsp)
        self.assertEqual(4, self.seg.macro.data_map['HWDA'].length)
        # MH    R5,HWDA
        node = self.seg.nodes['TS120200.5']
        self.assertEqual('MH', node.command)
        self.assertEqual('R5', node.reg.reg)
        # MHI   R5,-2
        node = self.seg.nodes['TS120200.6']
        self.assertEqual('MHI', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual(-2, node.data)
        # M     R4,ONE
        node = self.seg.nodes['TS120200.7']
        self.assertEqual('M', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('ONE', node.field.name)
        self.assertIsNone(node.field.index)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x010, node.field.dsp)
        # MR    R4,R15
        node = self.seg.nodes['TS120200.8']
        self.assertEqual('MR', node.command)
        self.assertEqual('R4', node.reg1.reg)
        self.assertEqual('R15', node.reg2.reg)
        # DR    R4,R7
        node = self.seg.nodes['TS120200.9']
        self.assertEqual('DR', node.command)
        self.assertEqual('R4', node.reg1.reg)
        self.assertEqual('R7', node.reg2.reg)
        # D     R4,NUM
        node = self.seg.nodes['TS120200.10']
        self.assertEqual('D', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x014, node.field.dsp)
        # SLA   R1,1(R2)
        node = self.seg.nodes['TS120200.11']
        self.assertEqual('SLA', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertIsNone(node.field.index)
        self.assertEqual('R2_AREA', node.field.name)
        self.assertEqual('R2', node.field.base.reg)
        self.assertEqual(1, node.field.dsp)
        # SRA   R3,12
        node = self.seg.nodes['TS120200.12']
        self.assertEqual('SRA', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertIsNone(node.field.index)
        self.assertEqual('R0_AREA', node.field.name)
        self.assertEqual('R0', node.field.base.reg)
        self.assertEqual(12, node.field.dsp)
        # SLDA  R2,4
        node = self.seg.nodes['TS120200.13']
        self.assertEqual('SLDA', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(4, node.field.dsp)
        # SRDA  R2,32
        node = self.seg.nodes['TS120200.14']
        self.assertEqual('SRDA', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(32, node.field.dsp)
        # MVCL  R2,R6
        node = self.seg.nodes['TS120300.1']
        self.assertEqual('MVCL', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # MVZ   FLD1,FLD2
        node = self.seg.nodes['TS120300.2']
        self.assertEqual('MVZ', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(5, node.field_len.length)
        self.assertEqual('FLD2', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x505, node.field.dsp)
        # MVN   FLD1,FLD1+3
        node = self.seg.nodes['TS120300.3']
        self.assertEqual('MVN', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(5, node.field_len.length)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x503, node.field.dsp)
        # MVO   FIELDB,FIELDA
        node = self.seg.nodes['TS120300.4']
        self.assertEqual('MVO', node.command)
        self.assertEqual('FIELDB', node.field_len1.name)
        self.assertEqual('R8', node.field_len1.base.reg)
        self.assertEqual(0x01b, node.field_len1.dsp)
        self.assertEqual(4, node.field_len1.length)
        self.assertEqual('FIELDA', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x018, node.field_len2.dsp)
        self.assertEqual(3, node.field_len2.length)
        # BCT   R3,TS120300
        node = self.seg.nodes['TS120300.5']
        self.assertEqual('BCT', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('TS120300', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(70, node.branch.dsp)
        self.assertIsNone(node.branch.index)
        self.assertEqual('TS120300', node.goes)
        self.assertSetEqual({'TS120300', 'TS120300.6'}, node.next_labels)
        # BXH   R1,R4,TS120100
        node = self.seg.nodes['TS120300.6']
        self.assertEqual('BXH', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        self.assertEqual('TS120100', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(8, node.branch.dsp)
        self.assertIsNone(node.branch.index)
        self.assertEqual('TS120100', node.goes)
        self.assertSetEqual({'TS120100', 'TS120300.7'}, node.next_labels)
        # BXLE  R2,R6,TS120200
        node = self.seg.nodes['TS120300.7']
        self.assertEqual('BXLE', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        self.assertEqual('TS120200', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(18, node.branch.dsp)
        self.assertIsNone(node.branch.index)
        self.assertEqual('TS120200', node.goes)
        self.assertSetEqual({'TS120200', 'TS120300.8'}, node.next_labels)
        # BASR  R8,R0
        node = self.seg.nodes['TS120300.8']
        self.assertEqual('BASR', node.command)
        self.assertEqual('R8', node.reg1.reg)
        self.assertEqual('R0', node.reg2.reg)
        # CR    R3,R5
        node = self.seg.nodes['TS120400.1']
        self.assertEqual('CR', node.command)
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R5', node.reg2.reg)
        # C     R3,FWDA
        node = self.seg.nodes['TS120400.2']
        self.assertEqual('C', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('FWDA', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x008, node.field.dsp)
        # CHI   R3,-1
        node = self.seg.nodes['TS120400.3']
        self.assertEqual('CHI', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual(-1, node.data)
        # CL    R3,NUM
        node = self.seg.nodes['TS120400.4']
        self.assertEqual('CL', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x014, node.field.dsp)
        # CLR   R3,R4
        node = self.seg.nodes['TS120400.5']
        self.assertEqual('CLR', node.command)
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # CLM   R3,9,FLD1
        node = self.seg.nodes['TS120400.6']
        self.assertEqual('CLM', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual(9, node.data)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x500, node.field.dsp)
        # CLCL  R2,R6
        node = self.seg.nodes['TS120400.7']
        self.assertEqual('CLCL', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # SLL   R1,7
        node = self.seg.nodes['TS120400.8']
        self.assertEqual('SLL', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual(7, node.field.dsp)
        # SRL   R4,10(R5)
        node = self.seg.nodes['TS120400.9']
        self.assertEqual('SRL', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual(10, node.field.dsp)
        self.assertEqual('R5', node.field.base.reg)
        # SLDL  R2,4
        node = self.seg.nodes['TS120400.10']
        self.assertEqual('SLDL', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(4, node.field.dsp)
        # SRDL  R2,32
        node = self.seg.nodes['TS120400.11']
        self.assertEqual('SRDL', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(32, node.field.dsp)
        # ALR   R5,R15
        # BC    3,TS120400
        node = self.seg.nodes['TS120400.12']
        self.assertEqual('ALR', node.command)
        self.assertEqual('R5', node.reg1.reg)
        self.assertEqual('R15', node.reg2.reg)
        self.assertEqual('TS120400', node.goes)
        self.assertEqual('BCRY', node.on)
        # AL    R5,ONE
        node = self.seg.nodes['TS120400.13']
        self.assertEqual('AL', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('ONE', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x010, node.field.dsp)
        # SLR   R1,R3
        # BC    4,TS120400
        node = self.seg.nodes['TS120400.14']
        self.assertEqual('SLR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        self.assertEqual('TS120400', node.goes)
        self.assertEqual('BL', node.on)
        # SL    R5,ZERO
        node = self.seg.nodes['TS120400.15']
        self.assertEqual('SL', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('ZERO', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x020, node.field.dsp)
        # NC    FLD1,FLD1
        node = self.seg.nodes['TS120500.1']
        self.assertEqual('NC', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(5, node.field_len.length)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x500, node.field.dsp)
        # NR    R2,R3
        node = self.seg.nodes['TS120500.2']
        self.assertEqual('NR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # OR    R0,R3
        node = self.seg.nodes['TS120500.3']
        self.assertEqual('OR', node.command)
        self.assertEqual('R0', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # XR    R1,R1
        node = self.seg.nodes['TS120500.4']
        self.assertEqual('XR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        # O     R2,FWD
        node = self.seg.nodes['TS120500.5']
        self.assertEqual('O', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        # X     R0,FWD
        node = self.seg.nodes['TS120500.6']
        self.assertEqual('X', node.command)
        self.assertEqual('R0', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        # XI    TEST,X'CA'
        node = self.seg.nodes['TS120500.7']
        self.assertEqual('TEST', node.field.name)
        self.assertEqual('R6', node.field.base.reg)
        self.assertEqual(0x3cc, node.field.dsp)
        self.assertEqual(0xCA, node.bits.value)
        self.assertEqual('#BIT0+#BIT1+#BIT4+#BIT6', node.bits.text)
        # ZAP   FLD1,FLD1+1(2)
        node = self.seg.nodes['TS120600.1']
        self.assertEqual('ZAP', node.command)
        self.assertEqual('FLD1', node.field_len1.name)
        self.assertEqual('R6', node.field_len1.base.reg)
        self.assertEqual(0x500, node.field_len1.dsp)
        self.assertEqual(5, node.field_len1.length)
        self.assertEqual('FLD1', node.field_len2.name)
        self.assertEqual('R6', node.field_len2.base.reg)
        self.assertEqual(0x501, node.field_len2.dsp)
        self.assertEqual(2, node.field_len2.length)
        # AP    WORK,PACKED
        node = self.seg.nodes['TS120600.2']
        self.assertEqual('AP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('R6', node.field_len1.base.reg)
        self.assertEqual(0x3d0, node.field_len1.dsp)
        self.assertEqual(4, node.field_len1.length)
        self.assertEqual('PACKED', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x027, node.field_len2.dsp)
        self.assertEqual(2, node.field_len2.length)
        # SP    WORK,PACKED
        node = self.seg.nodes['TS120600.3']
        self.assertEqual('SP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('PACKED', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x027, node.field_len2.dsp)
        self.assertEqual(2, node.field_len2.length)
        # MP    WORK,P2
        node = self.seg.nodes['TS120600.4']
        self.assertEqual('MP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('P2', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x029, node.field_len2.dsp)
        self.assertEqual(2, node.field_len2.length)
        # DP    WORK,P2
        node = self.seg.nodes['TS120600.5']
        self.assertEqual('DP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('P2', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x029, node.field_len2.dsp)
        self.assertEqual(2, node.field_len2.length)
        # CP    FLD1,FLD2
        node = self.seg.nodes['TS120600.6']
        self.assertEqual('CP', node.command)
        self.assertEqual('FLD1', node.field_len1.name)
        self.assertEqual('R6', node.field_len1.base.reg)
        self.assertEqual(0x500, node.field_len1.dsp)
        self.assertEqual(5, node.field_len1.length)
        self.assertEqual('FLD2', node.field_len2.name)
        self.assertEqual('R6', node.field_len2.base.reg)
        self.assertEqual(0x505, node.field_len2.dsp)
        self.assertEqual(5, node.field_len2.length)
        # TP    NUM
        node = self.seg.nodes['TS120600.7']
        self.assertEqual('TP', node.command)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x014, node.field.dsp)
        self.assertEqual(4, node.field.length)
        # SRP   FLD1,4,0
        node = self.seg.nodes['TS120600.8']
        self.assertEqual('SRP', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R6', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(5, node.field_len.length)
        self.assertEqual(4, node.field.dsp)
        self.assertEqual('R0', node.field.base.reg)
        self.assertEqual(0, node.data)
        # TR    INPT,TABLE
        node = self.seg.nodes['TS120600.9']
        self.assertEqual('TR', node.command)
        self.assertEqual('INPT', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x02b, node.field_len.dsp)
        self.assertEqual(3, node.field_len.length)
        self.assertEqual('TABLE', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x02e, node.field.dsp)
        # TRT   SENT,FULLTBL
        node = self.seg.nodes['TS120600.10']
        self.assertEqual('TRT', node.command)
        self.assertEqual('SENT', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x38, node.field_len.dsp)
        self.assertEqual(11, node.field_len.length)
        self.assertEqual('FULLTBL', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x043, node.field.dsp)
        # ED    PATTERN,PCK1
        node = self.seg.nodes['TS120600.11']
        self.assertEqual('ED', node.command)
        self.assertEqual('PATTERN', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x143, node.field_len.dsp)
        self.assertEqual(10, node.field_len.length)
        self.assertEqual('PCK1', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x024, node.field.dsp)
        # EDMK  PATTERN,PCK1
        node = self.seg.nodes['TS120600.12']
        self.assertEqual('PATTERN', node.field_len.name)
        self.assertEqual('PCK1', node.field.name)
        # FULLTBL  DC    193X'FF',9X'00',7X'FF',9X'00',8X'FF',8X'00',22X'FF'
        self.assertEqual(bytearray([0xFF]*193), self.seg.get_constant_bytes('FULLTBL', 193))
        self.assertEqual(bytearray([0x00]*9), self.seg.get_constant_bytes("FULLTBL+C'A'", 9))
        self.assertEqual(bytearray([0xFF]*7), self.seg.get_constant_bytes("FULLTBL+C'I'+1", 7))
        self.assertEqual(bytearray([0x00]*9), self.seg.get_constant_bytes("FULLTBL+C'J'", 9))
        self.assertEqual(bytearray([0xFF]*8), self.seg.get_constant_bytes("FULLTBL+C'R'+1", 8))
        self.assertEqual(bytearray([0x00]*8), self.seg.get_constant_bytes("FULLTBL+C'S'", 8))
        self.assertEqual(bytearray([0xFF]*22), self.seg.get_constant_bytes("FULLTBL+C'Z'+1", 22))

    def test_execute(self):
        seg_name = 'TS13'
        accepted_errors_list = [
            f"{Error.REG_INVALID} TS13E000.1:EX:R16,TS130010 {seg_name}",
            f"{Error.RL_INVALID_LEN} TS13E000.2:EX:R15,*-1 {seg_name}",
            f"{Error.RL_INVALID_LABEL} TS13E000.3:EX:R15,TS13INVALID {seg_name}"
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # TM    EBW000,0
        node = self.seg.nodes['TS130010.1']
        self.assertEqual('TM', node.command)
        self.assertSetEqual({'TS130010.2'}, node.next_labels)
        # EX    R15,*-4 with BNO   TS130010 on TM    EBW000,0
        node = self.seg.nodes['TS130010.2']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130010.1', node.label)
        self.assertEqual('TS130010', node.goes)
        self.assertSetEqual({'TS130020', 'TS130010'}, node.next_labels)
        ex_node = self.seg.nodes[node.label]
        self.assertEqual('TM', ex_node.command)
        self.assertEqual(0, ex_node.bits.value)
        # EX    R15,*-6 on MVC   EBW000,EBT000
        node = self.seg.nodes['TS130020.2']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130020.1', node.label)
        self.assertSetEqual({'TS130020.3'}, node.next_labels)
        ex_node = self.seg.nodes[node.label]
        self.assertEqual('MVC', ex_node.command)
        self.assertEqual(1, ex_node.field_len.length)
        self.assertEqual('EBW000', ex_node.field_len.name)
        self.assertEqual('EBT000', ex_node.field.name)
        # EX    R15,TS130030 on PACK  EBW088(8),4(1,R2)
        node = self.seg.nodes['TS130020.3']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130030', node.label)
        self.assertSetEqual({'TS130030'}, node.next_labels)
        ex_node = self.seg.nodes[node.label]
        self.assertEqual('PACK', ex_node.command)
        self.assertEqual(8, ex_node.field_len1.length)
        self.assertEqual(1, ex_node.field_len2.length)
        self.assertEqual('EBW088', ex_node.field_len1.name)
        self.assertEqual('R2', ex_node.field_len2.base.reg)
        self.assertEqual(4, ex_node.field_len2.dsp)
        # EX    R15,TS130040 with MVC   EBW000,EBT000
        node = self.seg.nodes['TS130030.1']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130040.1', node.label)
        self.assertSetEqual({'TS130040'}, node.next_labels)
        ex_node = self.seg.nodes[node.label]
        self.assertEqual('MVC', ex_node.command)
        self.assertEqual(1, ex_node.field_len.length)
        self.assertEqual('EBW000', ex_node.field_len.name)
        self.assertEqual('EBT000', ex_node.field.name)
