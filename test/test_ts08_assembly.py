import unittest

from assembly.instruction import Instruction
from assembly.program import program
from utils.errors import Error
from utils.file_line import Line


class AssemblyTest(unittest.TestCase):
    NUMBER_OF_FILES = 40

    def old_common_checks(self, seg_name, accepted_errors_list=None):
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

    def test_field_variants(self):
        seg_name = 'TS04'
        accepted_errors_list = [
            f"{Error.FL_INVALID_LEN} TS04E100.1:MVC:23(L'CE1WKA+60,R3),26(R4) {seg_name}",
            f"{Error.FL_LEN_REQUIRED} TS04E100.3:OC:EBW000(,R4),EBW000 {seg_name}",
            f"{Error.FL_INVALID_LEN} TS04E200.1:PACK:CE1DCT,10(17,R15) {seg_name}",
            f"{Error.FD_INVALID_DATA} TS04E300.1:MVI:EBW000,256 {seg_name}",
            f"{Error.FD_INVALID_DATA} TS04E300.2:MVI:EBW000,C'AB' {seg_name}",
        ]
        self.old_common_checks(seg_name, accepted_errors_list)
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
        self.old_common_checks(seg_name, accepted_errors_list)
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

    def test_constant(self):
        seg_name = 'TS07'
        accepted_errors_list = [
            f"{Error.EQU_LABEL_REQUIRED} None:EQU:23 {seg_name}",
        ]
        self.old_common_checks(seg_name, accepted_errors_list)
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
        self.old_common_checks(seg_name, accepted_errors_list)
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