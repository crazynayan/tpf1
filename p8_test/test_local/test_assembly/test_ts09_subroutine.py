import unittest

from p1_utils.errors import RegisterInvalidError
from p1_utils.file_line import Line
from p2_assembly.seg6_segment import Segment
from p2_assembly.seg9_collection import get_seg_collection


class Subroutine(unittest.TestCase):
    def test_subroutine(self):
        seg: Segment = get_seg_collection().get_seg("TS09")
        self.assertRaises(RegisterInvalidError, seg.reg_branch, Line.from_line(" BAS R16,TS09S100"))
        self.assertRaises(RegisterInvalidError, seg.branch_mnemonic_reg, Line.from_line(" BR -1"))
        seg.assemble()
        # BAS   R4,TS09S100
        node = seg.nodes["TS090010.1"]
        self.assertEqual("R4", node.reg.reg)
        self.assertEqual("TS09S100", node.branch.name)
        self.assertEqual("R8", node.branch.base.reg)
        # JAS   R2,TS09S100
        node = seg.nodes["TS090010.2"]
        self.assertEqual("R2", node.reg.reg)
        self.assertEqual("TS09S200", node.branch.name)
        self.assertEqual("R8", node.branch.base.reg)
        # BZR   R4
        node = seg.nodes["TS09S100.2"]
        self.assertIsNone(node.goes)
        self.assertEqual({"TS09S100.3"}, node.next_labels)
        self.assertEqual("BZR", node.on)
        self.assertEqual("R4", node.reg.reg)
        self.assertEqual(8, node.mask)
        # AHI   R2,1
        self.assertEqual("AHI", seg.nodes["TS09S100.3"].command)
        # LTR   R1,R1
        self.assertEqual("LTR", seg.nodes["TS09S100.4"].command)
        # NOPR  0
        node = seg.nodes["TS09S100.5"]
        self.assertEqual("NOPR", node.command)
        self.assertIsNone(node.goes)
        self.assertEqual({"TS09S100.6"}, node.next_labels)
        self.assertEqual("NOPR", node.on)
        self.assertEqual("R0", node.reg.reg)
        self.assertEqual(0, node.mask)
        # AHI   R2,1
        self.assertEqual("AHI", seg.nodes["TS09S100.6"].command)
        # BR    R4
        node = seg.nodes["TS09S100.7"]
        self.assertEqual("BR", node.command)
        self.assertIsNone(node.goes)
        self.assertEqual(set(), node.next_labels)
        self.assertEqual("BR", node.on)
        self.assertEqual("R4", node.reg.reg)
        self.assertEqual(15, node.mask)
        # BCR   0,R2
        node = seg.nodes["TS09S200.1"]
        self.assertEqual("BCR", node.command)
        self.assertIsNone(node.goes)
        self.assertEqual({"TS09S200.2"}, node.next_labels)
        self.assertEqual("BCR", node.on)
        self.assertEqual("R2", node.reg.reg)
        self.assertEqual(0, node.mask)
        # BCR   15,R2
        node = seg.nodes["TS09S200.2"]
        self.assertEqual("BCR", node.command)
        self.assertIsNone(node.goes)
        self.assertEqual("TS09S200.3", node.fall_down)
        self.assertEqual("R2", node.reg.reg)
        self.assertEqual(15, node.mask)
        # BCR   8,R2
        node = seg.nodes["TS09S200.3"]
        self.assertIsNone(node.goes)
        self.assertEqual({"TS09S200.4"}, node.next_labels)
        self.assertEqual("R2", node.reg.reg)
        self.assertEqual("BCR", node.on)
        self.assertEqual(8, node.mask)


if __name__ == "__main__":
    unittest.main()
