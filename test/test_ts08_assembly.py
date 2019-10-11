import unittest

from assembly.file_line import Line
from assembly.instruction import Instruction
from assembly.program import program
from utils.errors import Error


class AssemblyTest(unittest.TestCase):
    NUMBER_OF_FILES = 37

    def setUp(self) -> None:
        self.seg = None

    def _common_checks(self, seg_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        program.load(seg_name)
        self.seg = program.segments[seg_name]
        self.assertListEqual(accepted_errors_list, self.seg.errors, '\n\n\n' + '\n'.join(list(
            set(self.seg.errors) - set(accepted_errors_list))))
        self.assertTrue(self.seg.assembled)


class SegmentTest(AssemblyTest):
    def test_files(self):
        self.assertTrue('TS02' in program.segments)
        self.assertTrue('TS01' in program.segments)
        self.assertFalse('EB0EB' in program.segments)
        self.assertEqual(self.NUMBER_OF_FILES, len(program.segments), 'Update number of files in SegmentTest')

    def test_field_bits(self):
        seg_name = 'TS01'
        accepted_errors_list = [
            f"{Error.FBD_NO_LEN} TS01E000.1:OI:23(2,R9),1 {seg_name}",
            f"{Error.FBD_INVALID_BASE} TS01E000.2:OI:EBW000(L'EBW001),1 {seg_name}",
            f"{Error.FBD_INVALID_KEY} TS01E000.3:OI:ERROR_FIELD,1 {seg_name}",
            f"{Error.FBD_INVALID_KEY_BASE} TS01E000.4:OI:PD0_C_ITM,1 {seg_name}",
            f"{Error.BITS_INVALID_NUMBER} TS01E000.6:OI:EBW000,250+250 {seg_name}",
            f"{Error.FBD_INVALID_DSP} TS01E000.8:OI:-1(R2),1 {seg_name}",
            f"{Error.FBD_INVALID_DSP} TS01E000.9:OI:4096(R2),1 {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # Check EBW008-EBW000(9),1
        label = '$$TS01$$.1'
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(8, self.seg.nodes[label].field.dsp)
        self.assertEqual('EBW000', self.seg.nodes[label].field.name)
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
        self.assertEqual(0x000, self.seg.macro.data_map[label].dsp)
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
        # CH    R15,=H'99'
        label = '$$TS03$$.13'
        self.assertEqual('R15', self.seg.nodes[label].reg.reg)
        self.assertEqual('R8', self.seg.nodes[label].field.base.reg)
        literal = self.seg.nodes[label].field.name
        self.assertTrue(self.seg.macro.data_map[literal].is_literal)
        self.assertEqual(bytearray([0x00, 0x63]), self.seg.get_constant_bytes(literal))
        # N     R0,=A(X'1F')
        label = '$$TS03$$.14'
        self.assertEqual('R0', self.seg.nodes[label].reg.reg)
        self.assertEqual('R8', self.seg.nodes[label].field.base.reg)
        literal = self.seg.nodes[label].field.name
        self.assertTrue(self.seg.macro.data_map[literal].is_literal)
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x1F]), self.seg.get_constant_bytes(literal))
        # L     R6,PD0_RT_ADR
        label = '$$TS03$$.15'
        self.assertEqual('R4', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x078, self.seg.nodes[label].field.dsp)
        field_name = self.seg.nodes[label].field.name
        self.assertEqual(4, self.seg.macro.data_map[field_name].length)
        self.assertEqual('PD0WRK', self.seg.macro.data_map[field_name].name)
        # L     R6,PD0_RT_ADRX
        label = '$$TS03$$.16'
        self.assertEqual('R5', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x078, self.seg.nodes[label].field.dsp)
        field_name = self.seg.nodes[label].field.name
        self.assertEqual(4, self.seg.macro.data_map[field_name].length)
        self.assertEqual('PD0WRKX', self.seg.macro.data_map[field_name].name)

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
        self.assertEqual(211, self.seg.nodes[label].field_len.length)
        # CLC   L'CE1WKA+EBW000+4(CE1FA1-CE1FA0,R9),CE1FA1(R9) with BNE   TS040110
        label = 'TS040100.2'
        self.assertEqual('EBCFW0', self.seg.nodes[label].field_len.name)
        self.assertEqual('R9', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(0xe0, self.seg.nodes[label].field_len.dsp)
        self.assertEqual(7, self.seg.nodes[label].field_len.length)
        self.assertEqual('EBCFW1', self.seg.nodes[label].field.name)
        self.assertEqual(0xe8, self.seg.nodes[label].field.dsp)
        self.assertEqual('BNE', self.seg.nodes[label].on)
        self.assertEqual('TS040110', self.seg.nodes[label].goes)
        # MVC   EBW000(L'CE1WKA-1),EBW001
        label = 'TS040100.3'
        self.assertEqual('EBW000', self.seg.nodes[label].field_len.name)
        self.assertEqual('R9', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(0x8, self.seg.nodes[label].field_len.dsp)
        self.assertEqual(210, self.seg.nodes[label].field_len.length)
        self.assertEqual('EBW001', self.seg.nodes[label].field.name)
        self.assertEqual(0x9, self.seg.nodes[label].field.dsp)
        self.assertEqual('TS040100.4', self.seg.nodes[label].fall_down)
        # CLC   2(2,R2),=C'I/' with BE    TS040110
        label = 'TS040100.4'
        self.assertEqual('R2_AREA', self.seg.nodes[label].field_len.name)
        self.assertEqual('R2', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(2, self.seg.nodes[label].field_len.dsp)
        self.assertEqual(1, self.seg.nodes[label].field_len.length)
        self.assertEqual('R8', self.seg.nodes[label].field.base.reg)
        literal = self.seg.nodes[label].field.name
        self.assertTrue(self.seg.macro.data_map[literal].is_literal)
        self.assertEqual('I/', self.seg.get_constant_bytes(literal).decode(encoding='cp037'))
        self.assertEqual('TS040110', self.seg.nodes[label].goes)
        self.assertEqual('BE', self.seg.nodes[label].on)
        # CLC   =C'C/',2(R2) with BL    TS040110
        label = 'TS040100.5'
        self.assertEqual('R2_AREA', self.seg.nodes[label].field.name)
        self.assertEqual('R2', self.seg.nodes[label].field.base.reg)
        self.assertEqual(2, self.seg.nodes[label].field.dsp)
        self.assertEqual('R8', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(1, self.seg.nodes[label].field_len.length)
        literal = self.seg.nodes[label].field_len.name
        self.assertTrue(self.seg.macro.data_map[literal].is_literal)
        self.assertEqual('C/', self.seg.get_constant_bytes(literal).decode(encoding='cp037'))
        self.assertEqual('TS040110', self.seg.nodes[label].goes)
        self.assertEqual('BL', self.seg.nodes[label].on)
        # MVC   23(L'CE1WKA,R3),26(R4)
        label = 'TS040110.1'
        self.assertEqual('R3_AREA', self.seg.nodes[label].field_len.name)
        self.assertEqual('R3', self.seg.nodes[label].field_len.base.reg)
        self.assertEqual(23, self.seg.nodes[label].field_len.dsp)
        self.assertEqual(211, self.seg.nodes[label].field_len.length)
        self.assertEqual('R4_AREA', self.seg.nodes[label].field.name)
        self.assertEqual(26, self.seg.nodes[label].field.dsp)
        # Check FieldLenFieldLen
        # PACK  CE1DCT,CE1DET
        label = 'TS040200.1'
        self.assertEqual('CE1DCT', self.seg.nodes[label].field_len1.name)
        self.assertEqual('CE1DET', self.seg.nodes[label].field_len2.name)
        self.assertEqual('R9', self.seg.nodes[label].field_len2.base.reg)
        self.assertEqual(15, self.seg.nodes[label].field_len1.length)
        self.assertEqual(3, self.seg.nodes[label].field_len2.length)
        self.assertEqual(0x374, self.seg.nodes[label].field_len1.dsp)
        self.assertEqual(0x370, self.seg.nodes[label].field_len2.dsp)
        # UNPK  EBW008-EBW000(L'CE1FA1,R3),10(16,R15)
        label = 'TS040200.2'
        self.assertEqual('R3_AREA', self.seg.nodes[label].field_len1.name)
        self.assertEqual('R15_AREA', self.seg.nodes[label].field_len2.name)
        self.assertEqual('R15', self.seg.nodes[label].field_len2.base.reg)
        self.assertEqual(3, self.seg.nodes[label].field_len1.length)
        self.assertEqual(15, self.seg.nodes[label].field_len2.length)
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
        self.assertRaises(ValueError, Instruction.from_line, Line.from_line(" AHI R1,1,3"), self.seg.macro)
        self.assertRaises(ValueError, Instruction.from_line, Line.from_line(" LHI R1"), self.seg.macro)
        self.assertRaises(ValueError, Instruction.from_line, Line.from_line(" STM R1,R2,B,C"), self.seg.macro)
        self.assertRaises(ValueError, Instruction.from_line, Line.from_line(" LM R1,R2"), self.seg.macro)
        self.assertRaises(ValueError, Instruction.from_line, Line.from_line(" ICM R1,1"), self.seg.macro)
        self.assertRaises(ValueError, Instruction.from_line, Line.from_line(" STCM R1"), self.seg.macro)
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
        # ICM   R3,B'1001',EBW000
        label = 'TS050300.1'
        self.assertEqual('R3', self.seg.nodes[label].reg.reg)
        self.assertEqual(9, self.seg.nodes[label].data)
        self.assertEqual('EBW000', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(8, self.seg.nodes[label].field.dsp)
        # STCM  R3,B'1111',10(R9)
        label = 'TS050300.2'
        self.assertEqual(15, self.seg.nodes[label].data)
        self.assertEqual('EBW002', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(10, self.seg.nodes[label].field.dsp)
        # ICM   R3,3,=H'-3'
        label = 'TS050300.3'
        self.assertEqual(3, self.seg.nodes[label].data)
        self.assertEqual('R8', self.seg.nodes[label].field.base.reg)
        literal = self.seg.nodes[label].field.name
        self.assertTrue(self.seg.macro.data_map[literal].is_literal)
        self.assertEqual(bytearray([0xFF, 0xFD]), self.seg.get_constant_bytes(literal))
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
            f"{Error.BC_INVALID_BRANCH} TS06E100.5:BNZ:1000(R8) {seg_name}",
            f"{Error.FBD_INVALID_KEY} TS06E100.6:JE:TS061000 {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        self.assertRaises(ValueError, Instruction.from_line, Line.from_line(" BC TS060100"), self.seg.macro)
        self.assertRaises(ValueError, Instruction.from_line, Line.from_line(" JC A,TS060100"), self.seg.macro)
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
        node = self.seg.nodes['TS060110']
        # LTR  R2, R2 with a single goes
        self.assertEqual('R2', node.reg2.reg)
        self.assertSetEqual({'TS060110.1', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060110.1', node.fall_down)
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
        node = self.seg.nodes['TS060110.1']
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # J     TS060100
        node = self.seg.nodes['TS060110.2']
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
        # JC    15,TS060120 & BC    15,TS060120
        for node in {self.seg.nodes['TS060130.2'], self.seg.nodes['TS060130.4']}:
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
        self.assertEqual(0x000, self.seg.macro.data_map[label].dsp)
        self.assertEqual(4, self.seg.macro.data_map[label].length)
        # C'CLASS'
        label = 'NAME'
        self.assertEqual(0x000, self.seg.macro.data_map[label].dsp)
        self.assertEqual(5, self.seg.macro.data_map[label].length)
        class_name = bytearray([0xC3, 0xD3, 0xC1, 0xE2, 0xE2])
        at = 0x000
        self.assertEqual(class_name, self.seg.data.get_constant(at, at + 5))
        self.assertEqual(class_name, self.seg.get_constant_bytes(label))
        # 2C'NAM'
        label = 'EXAM'
        self.assertEqual(0x005, self.seg.macro.data_map[label].dsp)
        self.assertEqual(3, self.seg.macro.data_map[label].length)
        exam_name = bytearray([0xD5, 0xC1, 0xD4, 0xD5, 0xC1, 0xD4])
        self.assertEqual(exam_name, self.seg.get_constant_bytes(label, len(exam_name)))
        # A(EXAM)
        label = 'ADR1'
        self.assertEqual(0x00c, self.seg.macro.data_map[label].dsp)
        self.assertEqual(4, self.seg.macro.data_map[label].length)
        self.assertEqual(bytearray(int(5).to_bytes(4, 'big')), self.seg.get_constant_bytes(label))
        self.assertEqual(bytearray(int(5).to_bytes(5, 'big')), self.seg.data.get_constant(0x00B, 0x010))
        # Y(ADR1-EXAM)
        label = 'ADR2'
        self.assertEqual(0x010, self.seg.macro.data_map[label].dsp)
        self.assertEqual(2, self.seg.macro.data_map[label].length)
        self.assertEqual(bytearray(int(7).to_bytes(2, 'big')), self.seg.get_constant_bytes(label))
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
        self.assertEqual(bytearray([0x8D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07]), self.seg.data.get_constant(56, 63))
        # FULL2    DC    FL2'100.7'
        self.assertEqual(bytearray([0x00, 0x65]), self.seg.get_constant_bytes('FULL2'))
        # HALF1    DC    H'2000'
        self.assertEqual(bytearray([0x07, 0xD0]), self.seg.get_constant_bytes('HALF1'))
        # HALF2    DC    H'-2'
        self.assertEqual(bytearray([0xFF, 0xFE]), self.seg.get_constant_bytes('HALF2'))
        self.assertEqual(bytearray([0xFF, 0xFE]), self.seg.data.get_constant(68, 70))
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
        # BIG      DC    Y(ADR1-EXAM,L'ADR1-L'EXAM),X'23',YL1(EXAM+ADR1,L'ZON3+L'HALF1-EXAM+#UI2NXT)
        self.assertEqual(bytearray([0x00, 0x07]), self.seg.get_constant_bytes('BIG'))
        self.assertEqual(bytearray([0x00, 0x07, 0x00, 0x01, 0x23, 0x11, 0xF4]), self.seg.get_constant_bytes('BIG', 7))

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
        self.assertEqual(0, self.seg.macro.data_map['TS080010'].dsp)
        self.assertEqual('R9', self.seg.nodes['$$TS08$$.1'].field.base.reg)
        self.assertEqual('R1', self.seg.nodes['$$TS08$$.3'].field.base.reg)
        self.assertEqual('WA0ET4', self.seg.nodes['$$TS08$$.3'].field.name)
        self.assertEqual(0x10, self.seg.nodes['$$TS08$$.3'].bits.value)
        self.assertTrue(self.seg.nodes['$$TS08$$.3'].bits.bit_by_name('#WA0TTY').on)
        self.assertEqual('R14', self.seg.nodes['$$TS08$$.4'].field_len.base.reg)
        self.assertEqual(1, self.seg.nodes['$$TS08$$.4'].field_len.length)
        self.assertEqual('R8', self.seg.nodes['$$TS08$$.4'].field.base.reg)
        self.assertEqual(0, self.seg.nodes['$$TS08$$.4'].field.dsp)
        self.assertEqual(bytearray([0xC1, 0xC1]), self.seg.get_constant_bytes('$C_AA'))
        self.assertEqual('TS08AAC', self.seg.nodes['TS080010.1'].field_len.name)
        self.assertEqual('R14', self.seg.nodes['TS080010.1'].field_len.base.reg)
        self.assertEqual(1, self.seg.nodes['TS080010.1'].field_len.length)
        self.assertEqual('R1', self.seg.nodes['TS080010.1'].field.base.reg)
        self.assertEqual('R14', self.seg.nodes['TS080010.2'].field_len.base.reg)
        self.assertEqual(255, self.seg.nodes['TS080010.2'].field_len.length)
        self.assertEqual('R8', self.seg.nodes['TS080010.2'].field.base.reg)
        self.assertEqual(bytearray([0x00] * 256), self.seg.get_constant_bytes('$X_00'))
        self.assertEqual('R2', self.seg.nodes['TS080010.3'].field.base.reg)
        self.assertEqual('R1', self.seg.nodes['TS080010.4'].field.base.reg)
        self.assertEqual('R14', self.seg.nodes['TS080010.5'].field.base.reg)


if __name__ == '__main__':
    unittest.main()
