import unittest

from p2_assembly.seg6_segment import Segment
from p2_assembly.seg9_collection import seg_collection


class Dsect(unittest.TestCase):
    def test_dsect(self):
        seg: Segment = seg_collection.get_seg("TS08")
        seg.assemble()
        self.assertEqual(48, seg.lookup("TS08IND").dsp)
        self.assertEqual("TS08BLK", seg.lookup("TS08IND").name)
        self.assertEqual(0x80, seg.lookup("#ELIGIND").dsp)
        self.assertEqual(56, seg.lookup("TS08FQ").dsp)
        self.assertEqual(256, seg.lookup("TS08REC").length)
        self.assertEqual(64, seg.lookup("TS08REC").dsp)
        self.assertEqual(64, seg.lookup("TS08ITM").dsp)
        self.assertEqual(64, seg.lookup("TS08AAC").dsp)
        self.assertEqual(0, seg.lookup("TS08PGR").dsp)
        self.assertEqual("TS08AWD", seg.lookup("TS08PGR").name)
        self.assertEqual(30, seg.lookup("TS080010").dsp)
        self.assertEqual("R9", seg.nodes["$$TS08$$.1"].field.base.reg)
        self.assertEqual("R1", seg.nodes["$$TS08$$.3"].field.base.reg)
        self.assertEqual("WA0ET4", seg.nodes["$$TS08$$.3"].field.name)
        self.assertEqual(0x10, seg.nodes["$$TS08$$.3"].bits.value)
        self.assertTrue(seg.nodes["$$TS08$$.3"].bits.bit_by_name("#WA0TTY").on)
        self.assertEqual("R14", seg.nodes["$$TS08$$.5"].field_len.base.reg)
        self.assertEqual(1, seg.nodes["$$TS08$$.5"].field_len.length)
        self.assertEqual("R8", seg.nodes["$$TS08$$.5"].field.base.reg)
        self.assertEqual(60, seg.nodes["$$TS08$$.5"].field.dsp)
        self.assertEqual(60, seg.lookup("$C_AA").dsp)
        self.assertEqual(bytearray([0xC1, 0xC1]), seg.get_constant_bytes("$C_AA"))
        self.assertEqual("R14_AREA", seg.nodes["TS080010.1"].field_len.name)
        self.assertEqual("R14", seg.nodes["TS080010.1"].field_len.base.reg)
        self.assertEqual(1, seg.nodes["TS080010.1"].field_len.length)
        self.assertEqual("R1", seg.nodes["TS080010.1"].field.base.reg)
        self.assertEqual("R14", seg.nodes["TS080010.2"].field_len.base.reg)
        self.assertEqual(255, seg.nodes["TS080010.2"].field_len.length)
        self.assertEqual("R8", seg.nodes["TS080010.2"].field.base.reg)
        self.assertEqual(62, seg.lookup("$X_00").dsp)
        self.assertEqual(bytearray([0x00] * 256), seg.get_constant_bytes("$X_00"))
        self.assertEqual("R2", seg.nodes["TS080010.3"].field.base.reg)
        self.assertEqual("R1", seg.nodes["TS080010.4"].field.base.reg)
        self.assertEqual("R14", seg.nodes["TS080010.5"].field.base.reg)
        self.assertEqual("R6", seg.nodes["TS08A010"].field_len.base.reg)
        self.assertEqual("R5", seg.nodes["TS08A010"].field.base.reg)
        self.assertEqual("R6", seg.nodes["TS08A020"].field_len.base.reg)
        self.assertEqual("R5", seg.nodes["TS08A020"].field.base.reg)


if __name__ == "__main__":
    unittest.main()
