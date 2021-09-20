import unittest

from p1_utils.errors import EquLabelRequiredError
from p1_utils.file_line import Line
from p2_assembly.seg6_segment import seg_collection, Segment


class Constant(unittest.TestCase):
    # noinspection SpellCheckingInspection
    def test_constant(self):
        seg: Segment = seg_collection.get_seg("TS07")
        self.assertRaises(EquLabelRequiredError, seg.equ, Line.from_line(" EQU 23"))
        seg.assemble()
        at = 0x018
        label = "TS070010"
        self.assertEqual(0x008, seg.lookup(label).dsp)
        self.assertEqual(1, seg.lookup(label).length)
        self.assertEqual("TS07", seg.lookup(label).name)
        label = "TS070020"
        self.assertEqual(at, seg.lookup(label).dsp)
        self.assertEqual(4, seg.lookup(label).length)
        # C'CLASS'
        label = "NAME"
        self.assertEqual(at, seg.lookup(label).dsp)
        self.assertEqual(5, seg.lookup(label).length)
        class_name = bytearray([0xC3, 0xD3, 0xC1, 0xE2, 0xE2])
        self.assertEqual(class_name, seg.data.constant[at: at + 5])
        self.assertEqual(class_name, seg.get_constant_bytes(label))
        # 2C'NAM'
        label = "EXAM"
        self.assertEqual(at + 0x005, seg.lookup(label).dsp)
        self.assertEqual(3, seg.lookup(label).length)
        exam_name = bytearray([0xD5, 0xC1, 0xD4, 0xD5, 0xC1, 0xD4])
        self.assertEqual(exam_name, seg.get_constant_bytes(label, len(exam_name)))
        # A(EXAM)
        label = "ADR1"
        self.assertEqual(at + 0x00C, seg.lookup(label).dsp)
        self.assertEqual(4, seg.lookup(label).length)
        self.assertEqual(bytearray(int(at + 5).to_bytes(4, "big")), seg.get_constant_bytes(label))
        self.assertEqual(bytearray(int(at + 5).to_bytes(5, "big")), seg.data.constant[at + 0x00B: at + 0x010])
        # Y(ADR1-EXAM)
        label = "ADR2"
        self.assertEqual(at + 0x010, seg.lookup(label).dsp)
        self.assertEqual(2, seg.lookup(label).length)
        self.assertEqual(bytearray(int(7).to_bytes(2, "big")), seg.get_constant_bytes(label))
        # CHAR1    DC    C"ASDC"
        self.assertEqual(bytearray([0xC1, 0xE2, 0xC4, 0xC3]), seg.get_constant_bytes("CHAR1"))
        # CHAR2    DC    CL6"ASDC"
        self.assertEqual(bytearray([0xC1, 0xE2, 0xC4, 0xC3, 0x40, 0x40]), seg.get_constant_bytes("CHAR2"))
        # CHAR3    DC    CL2"ASDC"
        self.assertEqual(bytearray([0xC1, 0xE2]), seg.get_constant_bytes("CHAR3"))
        # HEX1     DC    X"E"
        self.assertEqual(bytearray([0x0E]), seg.get_constant_bytes("HEX1"))
        # HEX2     DC    XL4"FACE"
        self.assertEqual(bytearray([0x00, 0x00, 0xFA, 0xCE]), seg.get_constant_bytes("HEX2"))
        # HEX3     DC    XL1"4243"
        self.assertEqual(bytearray([0x43]), seg.get_constant_bytes("HEX3"))
        # BIN1     DC    BL5"0100"
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x00, 0x04]), seg.get_constant_bytes("BIN1"))
        # BIN2     DC    BL1"101010"
        self.assertEqual(bytearray([0x2A]), seg.get_constant_bytes("BIN2"))
        # ZON1     DC    Z"6940"
        self.assertEqual(bytearray([0xF6, 0xF9, 0xF4, 0xC0]), seg.get_constant_bytes("ZON1"))
        # ZON2     DC    ZL1"-555"
        self.assertEqual(bytearray([0xD5]), seg.get_constant_bytes("ZON2"))
        # ZON3     DC    ZL5"555"
        self.assertEqual(bytearray([0xF0, 0xF0, 0xF5, 0xF5, 0xC5]), seg.get_constant_bytes("ZON3"))
        # PCK1     DC    P"1234"
        self.assertEqual(bytearray([0x01, 0x23, 0x4C]), seg.get_constant_bytes("PCK1"))
        # PCK2     DC    PL2"-12345678"
        self.assertEqual(bytearray([0x67, 0x8D]), seg.get_constant_bytes("PCK2"))
        # FULL1    DC    F"2000"
        self.assertEqual(bytearray([0x00, 0x00, 0x07, 0xD0]), seg.get_constant_bytes("FULL1"))
        self.assertEqual(bytearray([0x8D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07]), seg.data.constant[at + 56: at + 63])
        # FULL2    DC    FL2"100.7"
        self.assertEqual(bytearray([0x00, 0x65]), seg.get_constant_bytes("FULL2"))
        # HALF1    DC    H"2000"
        self.assertEqual(bytearray([0x07, 0xD0]), seg.get_constant_bytes("HALF1"))
        # HALF2    DC    H"-2"
        self.assertEqual(bytearray([0xFF, 0xFE]), seg.get_constant_bytes("HALF2"))
        self.assertEqual(bytearray([0xFF, 0xFE]), seg.data.constant[at + 68: at + 70])
        # FLV      DC    PL2"-29"
        self.assertEqual(bytearray([0x02, 0x9D]), seg.get_constant_bytes("FLV"))
        # FLW      DC    Z"246"
        self.assertEqual(bytearray([0xF2, 0xF4, 0xC6]), seg.get_constant_bytes("FLW"))
        # FLX      DC    FL5"-1"
        self.assertEqual(bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF]), seg.get_constant_bytes("FLX"))
        # FLY      DC    PL2"4096"
        self.assertEqual(bytearray([0x09, 0x6C]), seg.get_constant_bytes("FLY"))
        # FLZ      DC    ZL2"-29"
        self.assertEqual(bytearray([0xF2, 0xD9]), seg.get_constant_bytes("FLZ"))
        # FLU      DC    C"-29"
        self.assertEqual(bytearray([0x60, 0xF2, 0xF9]), seg.get_constant_bytes("FLU"))
        # BIG      DC    Y(ADR1-EXAM,L"ADR1-L"EXAM),X"23",YL1(EXAM+ADR1,L"ZON3+L"HALF1-EXAM+#UI2NXT)
        self.assertEqual(bytearray([0x00, 0x07]), seg.get_constant_bytes("BIG"))
        self.assertEqual(bytearray([0x00, 0x07, 0x00, 0x01, 0x23, 0x11 + 2 * at, 5 + 2 - (at + 5) + 0xF2]),
                         seg.get_constant_bytes("BIG", 7))


if __name__ == "__main__":
    unittest.main()
