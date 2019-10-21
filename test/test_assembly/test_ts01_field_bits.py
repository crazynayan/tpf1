import unittest

from assembly2.seg5_segment import Segment, segments
from utils.errors import FieldLengthInvalidError, RegisterInvalidError, NotFoundInSymbolTableError, BitsInvalidError, \
    FieldDspInvalidError
from utils.file_line import Line


class FieldBits(unittest.TestCase):
    def test_field_bits(self):
        seg_name = 'TS01'
        seg: Segment = segments[seg_name]
        self.assertRaises(FieldLengthInvalidError, seg.field_bits, Line.from_line(" OI 23(2,R9),1"))
        self.assertRaises(RegisterInvalidError, seg.field_bits, Line.from_line(" OI 23(L'EBW001),1"))
        self.assertRaises(NotFoundInSymbolTableError, seg.field_bits, Line.from_line(" OI ERROR_FIELD,1"))
        self.assertRaises(BitsInvalidError, seg.field_bits, Line.from_line(" OI 8(R9),250+250"))
        self.assertRaises(FieldDspInvalidError, seg.field_bits, Line.from_line(" OI -1(R2),1"))
        self.assertRaises(FieldDspInvalidError, seg.field_bits, Line.from_line(" OI 4096(R2),1"))
        seg.assemble()
        # Check EBW008-EBW000(9),1
        node = seg.nodes['$$TS01$$.1']
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(8, node.field.dsp)
        self.assertEqual('EBW000', node.field.name)
        self.assertTrue(node.bits.bit7.on)
        self.assertEqual("#BIT7", node.bits.bit7.name)
        # Check EBW000,X'80'
        node = seg.nodes['$$TS01$$.2']
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(8, node.field.dsp)
        self.assertEqual('EBW000', node.field.name)
        self.assertTrue(node.bits.bit0.on)
        self.assertEqual("#BIT0", node.bits.bit0.name)
        self.assertEqual(0x80, node.bits.value)
        # Check 23(R9),23
        node = seg.nodes['$$TS01$$.3']
        self.assertEqual('EBW015', node.field.name)
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(23, node.field.dsp)
        self.assertTrue(node.bits.bit7.on)
        self.assertEqual("#BIT3=0x10 + #BIT5=0x04 + #BIT6=0x02 + #BIT7=0x01", str(node.bits))
        self.assertEqual(0b00010111, node.bits.value)
        # Check EBT000+L'CE1DSTMP(R9),CE1SEW+CE1CPS+CE1DTX+CE1SNP
        node = seg.nodes['$$TS01$$.4']
        self.assertEqual('EBT008', node.field.name)
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(0x78, node.field.dsp)
        self.assertEqual("CE1SEW=0x80 + CE1CPS=0x40 + CE1DTX=0x20 + CE1SNP=0x10", str(node.bits))
        self.assertEqual(0xf0, node.bits.value)
        self.assertFalse(node.bits.bit6.on)
        # Check L'EBW000+3+EBW008-EBW000(9),X'FF'-CE1SEW-CE1CPS
        node = seg.nodes['$$TS01$$.5']
        self.assertEqual('EBW004', node.field.name)
        self.assertEqual('R9', node.field.base.reg)
        self.assertEqual(0x0c, node.field.dsp)
        self.assertEqual("#BITA - CE1SEW=0x80 - CE1CPS=0x40", str(node.bits))
        self.assertEqual(0x3f, node.bits.value)
        self.assertTrue(node.bits.bit6.on)
        # Check TM with BZ TS010010
        node = seg.nodes['$$TS01$$.6']
        self.assertEqual('TS010010', node.goes)
        self.assertEqual('BZ', node.on)
        self.assertSetEqual({'$$TS01$$.7', 'TS010010'}, node.next_labels)
        # Check fall down to label
        node = seg.nodes['$$TS01$$.7']
        self.assertEqual('TS010010', node.fall_down)
        # Check TS010010 EQU *
        node = seg.nodes['TS010010']
        self.assertEqual('TS010010', node.label)
        self.assertEqual('EQU', node.command)
        # Check OI    EBT000,1
        self.assertEqual('EBT000', seg.nodes['TS010010.1'].field.name)
        # Check OI    PD0_C_ITM,1
        self.assertEqual(0xC1, seg.nodes['TS010010.3'].field.dsp)
        # Check OI    PD0_C_ITM,1
        self.assertEqual('PD0_C_ITM', seg.nodes['TS010010.4'].field.name)
        self.assertIsNone(seg.nodes['TS010010.4'].field.base)
        # Check OI    EBW000,#PD0_FLDEMP
        self.assertEqual(0x03, seg.nodes['TS010010.5'].bits.value)


if __name__ == '__main__':
    unittest.main()
