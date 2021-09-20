import unittest

from p1_utils.errors import FieldLengthInvalidError
from p1_utils.file_line import Line
from p2_assembly.seg6_segment import seg_collection, Segment


class FieldVariants(unittest.TestCase):
    # noinspection SpellCheckingInspection
    def test_field_variants(self):
        seg: Segment = seg_collection.get_seg("TS04")
        self.assertRaises(FieldLengthInvalidError, seg.field_len_field, Line.from_line(" MVC 2(257,R3),26(R4)"))
        self.assertRaises(FieldLengthInvalidError, seg.field_len_field, Line.from_line(" OC EBW000(,R4),EBW000"))
        self.assertRaises(FieldLengthInvalidError, seg.field_len_field, Line.from_line(" OC EBW000(,R4),EBW000"))
        seg.assemble()
        # Check FieldLenField
        # XC    CE1WKA,CE1WKA
        node = seg.nodes["TS040100.1"]
        self.assertEqual("CE1WKA", node.field_len.name)
        self.assertEqual("R9", node.field_len.base.reg)
        self.assertEqual(0x8, node.field_len.dsp)
        self.assertEqual(211, node.field_len.length)
        # CLC   L"CE1WKA+EBW000+4(CE1FA1-CE1FA0,R9),CE1FA1(R9) with BNE   TS040110
        node = seg.nodes["TS040100.2"]
        self.assertEqual("R9_AREA", node.field_len.name)
        self.assertEqual("R9", node.field_len.base.reg)
        self.assertEqual(0xe0, node.field_len.dsp)
        self.assertEqual(7, node.field_len.length)
        self.assertEqual("R9_AREA", node.field.name)
        self.assertEqual(0xe8, node.field.dsp)
        node = seg.nodes["TS040100.3"]
        self.assertEqual("BNE", node.on)
        self.assertEqual("TS040110", node.goes)
        # MVC   EBW000(L"CE1WKA-1),EBW001
        node = seg.nodes["TS040100.4"]
        self.assertEqual("EBW000", node.field_len.name)
        self.assertEqual("R9", node.field_len.base.reg)
        self.assertEqual(0x8, node.field_len.dsp)
        self.assertEqual(210, node.field_len.length)
        self.assertEqual("EBW001", node.field.name)
        self.assertEqual(0x9, node.field.dsp)
        self.assertEqual("TS040100.5", node.fall_down)
        # CLC   2(2,R2),=C"I/" with BE    TS040110
        node = seg.nodes["TS040100.5"]
        self.assertEqual("R2_AREA", node.field_len.name)
        self.assertEqual("R2", node.field_len.base.reg)
        self.assertEqual(2, node.field_len.dsp)
        self.assertEqual(1, node.field_len.length)
        self.assertEqual("R8", node.field.base.reg)
        literal = node.field.name
        self.assertTrue(seg.lookup(literal).is_literal)
        self.assertEqual("I/", seg.get_constant_bytes(literal).decode(encoding="cp037"))
        node = seg.nodes["TS040100.6"]
        self.assertEqual("TS040110", node.goes)
        self.assertEqual("BE", node.on)
        # CLC   =C"C/",2(R2) with BL    TS040110
        node = seg.nodes["TS040100.7"]
        self.assertEqual("R2_AREA", node.field.name)
        self.assertEqual("R2", node.field.base.reg)
        self.assertEqual(2, node.field.dsp)
        self.assertEqual("R8", node.field_len.base.reg)
        self.assertEqual(1, node.field_len.length)
        literal = node.field_len.name
        self.assertTrue(seg.lookup(literal).is_literal)
        self.assertEqual("C/", seg.get_constant_bytes(literal).decode(encoding="cp037"))
        node = seg.nodes["TS040100.8"]
        self.assertEqual("TS040110", node.goes)
        self.assertEqual("BL", node.on)
        # MVC   23(L"CE1WKA,R3),26(R4)
        node = seg.nodes["TS040110.1"]
        self.assertEqual("R3_AREA", node.field_len.name)
        self.assertEqual("R3", node.field_len.base.reg)
        self.assertEqual(23, node.field_len.dsp)
        self.assertEqual(211, node.field_len.length)
        self.assertEqual("R4_AREA", node.field.name)
        self.assertEqual(26, node.field.dsp)
        # Check FieldLenFieldLen
        # PACK  CE1DCT,CE1DET
        node = seg.nodes["TS040200.1"]
        self.assertEqual("CE1DCT", node.field_len1.name)
        self.assertEqual("CE1DET", node.field_len2.name)
        self.assertEqual("R9", node.field_len2.base.reg)
        self.assertEqual(15, node.field_len1.length)
        self.assertEqual(3, node.field_len2.length)
        self.assertEqual(0x374, node.field_len1.dsp)
        self.assertEqual(0x370, node.field_len2.dsp)
        # UNPK  EBW008-EBW000(L"CE1FA1,R3),10(16,R15)
        node = seg.nodes["TS040200.2"]
        self.assertEqual("R3_AREA", node.field_len1.name)
        self.assertEqual("R15_AREA", node.field_len2.name)
        self.assertEqual("R15", node.field_len2.base.reg)
        self.assertEqual(3, node.field_len1.length)
        self.assertEqual(15, node.field_len2.length)
        self.assertEqual(8, node.field_len1.dsp)
        self.assertEqual(10, node.field_len2.dsp)
        # Check FieldData
        # CLI   EBW000,#$BCLASS with BNE   TS040310
        node = seg.nodes["TS040300.1"]
        self.assertEqual("EBW000", node.field.name)
        self.assertEqual(0xC2, node.data)
        node = seg.nodes["TS040300.2"]
        self.assertEqual("BNE", node.on)
        self.assertEqual("TS040310", node.goes)
        # MVI   23(R4),L"CE1WKA
        node = seg.nodes["TS040300.3"]
        self.assertEqual("R4_AREA", node.field.name)
        self.assertEqual("R4", node.field.base.reg)
        self.assertEqual(23, node.field.dsp)
        self.assertEqual(212, node.data)


if __name__ == "__main__":
    unittest.main()
