import unittest

from p1_utils.errors import RegisterInvalidError, DataInvalidError, NotFoundInSymbolTableError, FieldDspInvalidError
from p1_utils.file_line import Line
from p2_assembly.seg6_segment import segments, Segment


class RegisterVariants(unittest.TestCase):
    def test_reg_variants(self):
        seg: Segment = segments['TS05']
        self.assertRaises(RegisterInvalidError, seg.reg_data, Line.from_line(" LHI RAB,1"))
        self.assertRaises(DataInvalidError, seg.reg_data, Line.from_line(" LHI R1,X'100000000'"))
        self.assertRaises(RegisterInvalidError, seg.reg_reg_field, Line.from_line(" STM R14,R16,EBW000"))
        self.assertRaises(RegisterInvalidError, seg.reg_reg_field, Line.from_line(" LM RDC,R7,EBW000"))
        self.assertRaises(NotFoundInSymbolTableError, seg.reg_reg_field, Line.from_line(" LM R0,R1,PD0_C_ITM"))
        self.assertRaises(FieldDspInvalidError, seg.reg_reg_field, Line.from_line(" STM R3,R4,4096(R7)"))
        self.assertRaises(RegisterInvalidError, seg.reg_data_field, Line.from_line(" ICM R16,1,EBW000"))
        self.assertRaises(DataInvalidError, seg.reg_data_field, Line.from_line(" STCM  R1,-1,EBW000"))
        self.assertRaises(DataInvalidError, seg.reg_data_field, Line.from_line(" ICM R1,16,EBW000"))
        self.assertRaises(FieldDspInvalidError, seg.reg_data_field, Line.from_line(" ICM R1,7,-1(R9)"))
        self.assertRaises(ValueError, seg.reg_data, Line.from_line(" AHI R1,1,3"))
        self.assertRaises(ValueError, seg.reg_data, Line.from_line(" LHI R1"))
        self.assertRaises(ValueError, seg.reg_reg_field, Line.from_line(" STM R1,R2,B,C"))
        self.assertRaises(ValueError, seg.reg_reg_field, Line.from_line(" LM R1,R2"))
        self.assertRaises(ValueError, seg.reg_data_field, Line.from_line(" ICM R1,1"))
        self.assertRaises(ValueError, seg.reg_data_field, Line.from_line(" STCM R1"))
        seg.assemble()
        # Check RegisterData
        # AHI   R15,SUIFF with BP    TS050110
        node = seg.nodes['TS050100.1']
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual(0xff, node.data)
        node = seg.nodes['TS050100.2']
        self.assertEqual('BP', node.on)
        self.assertEqual('TS050110', node.goes)
        # AHI   R15,X'00'
        node = seg.nodes['TS050100.3']
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual(0, node.data)
        self.assertEqual('TS050110', node.fall_down)
        # LHI   R13,-1
        node = seg.nodes['TS050110.1']
        self.assertEqual('R13', node.reg.reg)
        self.assertEqual(-1, node.data)
        # LHI   R05,X'7FFF'+1
        node = seg.nodes['TS050110.2']
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual(32768, node.data)  # RegisterData is now 32 bit so this will be positive value
        # LHI   RG1,32767
        node = seg.nodes['TS050110.3']
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual(32767, node.data)
        # Check RegisterRegisterField
        # STM   R14,R7,656(R9)
        node = seg.nodes['TS050200.1']
        self.assertEqual('R14', node.reg1.reg)
        self.assertEqual('R7', node.reg2.reg)
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(0x290, node.field.dsp)
        self.assertEqual('R9_AREA', node.field.name)
        # LM    RDB,RGF,CE1DSTMP
        node = seg.nodes['TS050200.2']
        self.assertEqual('R14', node.reg1.reg)
        self.assertEqual('R7', node.reg2.reg)
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(0x290, node.field.dsp)
        self.assertEqual('CE1DSTMP', node.field.name)
        # Check RegisterDataField
        # ICM   R3,B'1001',EBW000
        node = seg.nodes['TS050300.1']
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual(9, node.data)
        self.assertEqual('EBW000', node.field.name)
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(8, node.field.dsp)
        # STCM  R3,B'1111',10(R9)
        node = seg.nodes['TS050300.2']
        self.assertEqual(15, node.data)
        self.assertEqual('R9_AREA', node.field.name)
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(10, node.field.dsp)
        # ICM   R3,3,=H'-3'
        node = seg.nodes['TS050300.3']
        self.assertEqual(3, node.data)
        self.assertEqual('R8', node.field.base.reg)
        literal = node.field.name
        self.assertTrue(seg.lookup(literal).is_literal)
        self.assertEqual(bytearray([0xFF, 0xFD]), seg.get_constant_bytes(literal))
        # STCM  R3,B'1000',EBW000
        node = seg.nodes['TS050300.4']
        self.assertEqual(8, node.data)


if __name__ == '__main__':
    unittest.main()
