import unittest

from d21_backend.p1_utils.errors import RegisterInvalidError, RegisterIndexInvalidError
from d21_backend.p1_utils.file_line import Line
from d21_backend.p2_assembly.seg6_segment import Segment
from d21_backend.p2_assembly.seg9_collection import get_seg_collection


class RegFieldIndex(unittest.TestCase):
    def test_reg_field_index(self):
        seg: Segment = get_seg_collection().get_seg("TS03")
        self.assertRaises(RegisterInvalidError, seg.reg_field_index, Line.from_line(" LA R1,2(R1,R3,R4)"))
        self.assertRaises(RegisterInvalidError, seg.reg_field_index, Line.from_line(" L R16,0(R9)"))
        self.assertRaises(RegisterIndexInvalidError, seg.reg_field_index, Line.from_line(" LA R1,2(ABC,R1)"))
        seg.assemble()
        # L     R1,CE1CR1
        node = seg.nodes["$$TS03$$.1"]
        self.assertEqual("R1", node.reg.reg)
        self.assertEqual("CE1CR1", node.field.name)
        self.assertEqual("R9", node.field.base.reg)
        self.assertEqual(0x170, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # LA    R2,2
        node = seg.nodes["$$TS03$$.2"]
        self.assertEqual("R2", node.reg.reg)
        self.assertEqual("2", node.field.name)
        self.assertEqual("R0", node.field.base.reg)
        self.assertEqual(2, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # IC    R1,3(R3,R4)
        node = seg.nodes["$$TS03$$.3"]
        self.assertEqual("R1", node.reg.reg)
        self.assertEqual("R4_AREA", node.field.name)
        self.assertEqual("R4", node.field.base.reg)
        self.assertEqual(3, node.field.dsp)
        self.assertEqual("R3", node.field.index.reg)
        # STH   R3,L"CE1CR1
        node = seg.nodes["$$TS03$$.4"]
        self.assertEqual("R3", node.reg.reg)
        # noinspection SpellCheckingInspection
        self.assertEqual("L'CE1CR1", node.field.name)
        self.assertEqual("R0", node.field.base.reg)
        self.assertEqual(4, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # N     R5,EBW008-EB0EB(R6)
        node = seg.nodes["$$TS03$$.5"]
        self.assertEqual("R5", node.reg.reg)
        self.assertEqual("R6_AREA", node.field.name)
        self.assertEqual("R6", node.field.base.reg)
        self.assertEqual(16, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # ST    R2,L"EBW000+2(R6,)
        node = seg.nodes["$$TS03$$.6"]
        self.assertEqual("R2", node.reg.reg)
        self.assertEqual("R6_AREA", node.field.name)
        self.assertEqual("R6", node.field.base.reg)
        self.assertEqual(3, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # STC   5,EBT000(0,9)
        node = seg.nodes["$$TS03$$.7"]
        self.assertEqual("R5", node.reg.reg)
        self.assertEqual("R9_AREA", node.field.name)
        self.assertEqual("R9", node.field.base.reg)
        self.assertEqual(0x070, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # STC   CVB   RGC,L"CE1CR1+EBW000(,REB)
        node = seg.nodes["$$TS03$$.8"]
        self.assertEqual("R4", node.reg.reg)
        self.assertEqual("R9_AREA", node.field.name)
        self.assertEqual("R9", node.field.base.reg)
        self.assertEqual(12, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # CVD   R06,6000(R00,R00)
        node = seg.nodes["$$TS03$$.9"]
        self.assertEqual("R6", node.reg.reg)
        self.assertEqual("R0_AREA", node.field.name)
        self.assertEqual("R0", node.field.base.reg)
        self.assertEqual(4095, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # CH    R15,4(R15)
        node = seg.nodes["$$TS03$$.10"]
        self.assertEqual("R15", node.reg.reg)
        self.assertEqual("R15_AREA", node.field.name)
        self.assertEqual("R15", node.field.base.reg)
        self.assertEqual(4, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # L     R1,CE1CR1(R3)
        node = seg.nodes["$$TS03$$.11"]
        self.assertEqual("R1", node.reg.reg)
        self.assertEqual("CE1CR1", node.field.name)
        self.assertEqual("R9", node.field.base.reg)
        self.assertEqual(0x170, node.field.dsp)
        self.assertEqual("R3", node.field.index.reg)
        # L     R1,12
        node = seg.nodes["$$TS03$$.12"]
        self.assertEqual("R1", node.reg.reg)
        self.assertEqual("12", node.field.name)
        self.assertEqual("R0", node.field.base.reg)
        self.assertEqual(12, node.field.dsp)
        self.assertEqual("R0", node.field.index.reg)
        # CH    R15,=H"99"
        node = seg.nodes["$$TS03$$.13"]
        self.assertEqual("R15", node.reg.reg)
        self.assertEqual("R8", node.field.base.reg)
        literal = node.field.name
        self.assertTrue(seg.lookup(literal).is_literal)
        self.assertEqual(bytearray([0x00, 0x63]), seg.get_constant_bytes(literal))
        # N     R0,=A(X"1F")
        node = seg.nodes["$$TS03$$.14"]
        self.assertEqual("R0", node.reg.reg)
        self.assertEqual("R8", node.field.base.reg)
        literal = node.field.name
        self.assertTrue(seg.lookup(literal).is_literal)
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x1F]), seg.get_constant_bytes(literal))
        # L     R6,PD0_RT_ADR
        node = seg.nodes["$$TS03$$.15"]
        self.assertEqual("R4", node.field.base.reg)
        self.assertEqual(0x078, node.field.dsp)
        field_name = node.field.name
        self.assertEqual(4, seg.lookup(field_name).length)
        self.assertEqual("PD0WRK", seg.lookup(field_name).name)
        # L     R6,PD0_RT_ADRX
        node = seg.nodes["$$TS03$$.16"]
        self.assertEqual("R5", node.field.base.reg)
        self.assertEqual(0x078, node.field.dsp)
        field_name = node.field.name
        self.assertEqual(4, seg.lookup(field_name).length)
        self.assertEqual("PD0WRKX", seg.lookup(field_name).name)


if __name__ == "__main__":
    unittest.main()
