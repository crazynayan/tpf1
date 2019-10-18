import unittest

from assembly.file_line import Line
from assembly2.seg5_segment import Segment, segments
from utils.errors import FieldLengthInvalidError, RegisterInvalidError, NotFoundInSymbolTableError, BitsInvalidError, \
    FieldDspInvalidError


class TestFieldBits(unittest.TestCase):
    def test_field_bits(self):
        seg_name = 'TS01'
        self.seg: Segment = segments[seg_name]
        self.assertRaises(FieldLengthInvalidError, self.seg.field_bits, Line.from_line(" OI 23(2,R9),1"))
        self.assertRaises(RegisterInvalidError, self.seg.field_bits, Line.from_line(" OI 23(L'EBW001),1"))
        self.assertRaises(NotFoundInSymbolTableError, self.seg.field_bits, Line.from_line(" OI ERROR_FIELD,1"))
        self.assertRaises(BitsInvalidError, self.seg.field_bits, Line.from_line(" OI 8(R9),250+250"))
        self.assertRaises(FieldDspInvalidError, self.seg.field_bits, Line.from_line(" OI -1(R2),1"))
        self.assertRaises(FieldDspInvalidError, self.seg.field_bits, Line.from_line(" OI 4096(R2),1"))
        self.seg.assemble()
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
        self.assertEqual("#BIT3=0x10 + #BIT5=0x04 + #BIT6=0x02 + #BIT7=0x01", str(self.seg.nodes[label].bits))
        self.assertEqual(0b00010111, self.seg.nodes[label].bits.value)
        # Check EBT000+L'CE1DSTMP(R9),CE1SEW+CE1CPS+CE1DTX+CE1SNP
        label = '$$TS01$$.4'
        self.assertEqual('EBT008', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x78, self.seg.nodes[label].field.dsp)
        self.assertEqual("CE1SEW=0x80 + CE1CPS=0x40 + CE1DTX=0x20 + CE1SNP=0x10", str(self.seg.nodes[label].bits))
        self.assertEqual(0xf0, self.seg.nodes[label].bits.value)
        self.assertFalse(self.seg.nodes[label].bits.bit6.on)
        # Check L'EBW000+3+EBW008-EBW000(9),X'FF'-CE1SEW-CE1CPS
        label = '$$TS01$$.5'
        self.assertEqual('EBW004', self.seg.nodes[label].field.name)
        self.assertEqual('R9', self.seg.nodes[label].field.base.reg)
        self.assertEqual(0x0c, self.seg.nodes[label].field.dsp)
        self.assertEqual("#BITA - CE1SEW=0x80 - CE1CPS=0x40", str(self.seg.nodes[label].bits))
        self.assertEqual(0x3f, self.seg.nodes[label].bits.value)
        self.assertTrue(self.seg.nodes[label].bits.bit6.on)
        # # Check TM with BZ TS010010  # TODO Uncomment when TM is ready
        # label = '$$TS01$$.6'
        # self.assertEqual('TS010010', self.seg.nodes[label].goes)
        # self.assertEqual('BZ', self.seg.nodes[label].on)
        # self.assertSetEqual({'$$TS01$$.7', 'TS010010'}, self.seg.nodes[label].next_labels)
        # # Check fall down to label
        # label = '$$TS01$$.7'
        # self.assertEqual('TS010010', self.seg.nodes[label].fall_down)
        # Check EQU *
        label = 'TS010010'
        self.assertEqual(label, self.seg.nodes[label].label)
        self.assertEqual('EQU', self.seg.nodes[label].command)


if __name__ == '__main__':
    unittest.main()
