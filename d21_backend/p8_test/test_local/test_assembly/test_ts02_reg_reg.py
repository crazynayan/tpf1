import unittest

from d21_backend.p1_utils.errors import RegisterInvalidError
from d21_backend.p1_utils.file_line import Line
from d21_backend.p2_assembly.seg6_segment import Segment
from d21_backend.p2_assembly.seg9_collection import get_seg_collection


class RegReg(unittest.TestCase):
    def test_reg_reg(self):
        seg: Segment = get_seg_collection().get_seg("TS02")
        self.assertRaises(RegisterInvalidError, seg.reg_reg, Line.from_line(" LR R16,R15"))
        self.assertRaises(RegisterInvalidError, seg.reg_reg, Line.from_line(" LR R1,RBD"))
        seg.assemble()
        # Check R02,RDA
        node = seg.nodes["TS020010"]
        self.assertEqual(0x008, seg.lookup("TS020010").dsp)
        self.assertEqual(2, seg.lookup("TS020010").length)
        self.assertEqual("R2", node.reg1.reg)
        self.assertEqual("R14", node.reg2.reg)
        # Check RGA,2 with JNZ TS020010 & it contains multiple instruction before JNZ
        node = seg.nodes["TS020020"]
        self.assertEqual(0x00A, seg.lookup("TS020020").dsp)
        self.assertEqual("R2", node.reg1.reg)
        self.assertEqual("R2", node.reg2.reg)
        node = seg.nodes["TS020020.5"]
        self.assertEqual("JNZ", node.on)
        self.assertSetEqual({"TS020030", "TS020040"}, node.next_labels)
        for index in range(1, 5):
            node = seg.nodes[f"TS020020.{index}"]
            self.assertEqual("R6", node.reg1.reg)
            self.assertEqual("LR", node.command)
        # Check 4,R04
        node = seg.nodes["TS020030"]
        self.assertEqual(0x018, seg.lookup("TS020030").dsp)
        self.assertEqual(2, seg.lookup("TS020030").length)
        self.assertEqual("R4", node.reg1.reg)
        self.assertEqual("R4", node.reg2.reg)
        self.assertSetEqual({"TS020040"}, node.next_labels)
        # Check DS    0H
        node = seg.nodes["TS020040"]
        self.assertEqual(0x01A, seg.lookup("TS020040").dsp)
        self.assertEqual("TS020040", node.label)
        self.assertEqual("DS", node.command)
        # Check  BCTR  R5,0
        node = seg.nodes["TS020040.1"]
        self.assertEqual("R5", node.reg1.reg)
        self.assertEqual("R0", node.reg2.reg)


if __name__ == "__main__":
    unittest.main()
