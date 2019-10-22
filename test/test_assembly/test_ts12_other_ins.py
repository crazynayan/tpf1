import unittest

from assembly2.seg6_segment import Segment, segments


class OtherInstruction(unittest.TestCase):
    def test_other_ins(self):
        seg: Segment = segments['TS12']
        seg.assemble()
        # LH    R1,FNAME(R2)
        node = seg.nodes['TS120100.1']
        self.assertEqual('LH', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual('FNAME', node.field.name)
        self.assertEqual('R2', node.field.index.reg)
        self.assertEqual('R3', node.field.base.reg)
        self.assertEqual(0x090, node.field.dsp)
        self.assertEqual(8, seg.lookup('FNAME').length)
        # LPR   R1,R3
        node = seg.nodes['TS120100.2']
        self.assertEqual('LPR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # LNR   R2,R2
        node = seg.nodes['TS120100.3']
        self.assertEqual('LNR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R2', node.reg2.reg)
        # LCR   R2,R1
        node = seg.nodes['TS120100.4']
        self.assertEqual('LCR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        # A     R5,FWDA
        node = seg.nodes['TS120200.1']
        self.assertEqual('A', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('FWDA', node.field.name)
        self.assertEqual('R0', node.field.index.reg)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x000, node.field.dsp)
        self.assertEqual(4, seg.lookup('FWDA').length)
        # AH    R1,HWD
        node = seg.nodes['TS120200.2']
        self.assertEqual('AH', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual('HWD', node.field.name)
        self.assertEqual('R0', node.field.index.reg)
        self.assertEqual('R3', node.field.base.reg)
        self.assertEqual(0x090, node.field.dsp)
        self.assertEqual(2, seg.lookup('HWD').length)
        # S     R5,FWD(R15)
        node = seg.nodes['TS120200.3']
        self.assertEqual('S', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R15', node.field.index.reg)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        self.assertEqual(4, seg.lookup('FWD').length)
        # SH    R4,HWDA
        node = seg.nodes['TS120200.4']
        self.assertEqual('SH', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('HWDA', node.field.name)
        self.assertEqual('R0', node.field.index.reg)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x004, node.field.dsp)
        self.assertEqual(4, seg.lookup('HWDA').length)
        # MH    R5,HWDA
        node = seg.nodes['TS120200.5']
        self.assertEqual('MH', node.command)
        self.assertEqual('R5', node.reg.reg)
        # MHI   R5,-2
        node = seg.nodes['TS120200.6']
        self.assertEqual('MHI', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual(-2, node.data)
        # M     R4,=F'1'
        node = seg.nodes['TS120200.7']
        self.assertEqual('M', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('R8', node.field.base.reg)
        self.assertTrue(seg.lookup(node.field.name).is_literal)
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x01]), seg.get_constant_bytes(node.field.name))
        # MR    R4,R15
        node = seg.nodes['TS120200.8']
        self.assertEqual('MR', node.command)
        self.assertEqual('R4', node.reg1.reg)
        self.assertEqual('R15', node.reg2.reg)
        # DR    R4,R7
        node = seg.nodes['TS120200.9']
        self.assertEqual('DR', node.command)
        self.assertEqual('R4', node.reg1.reg)
        self.assertEqual('R7', node.reg2.reg)
        # D     R4,NUM
        node = seg.nodes['TS120200.10']
        self.assertEqual('D', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x00c, node.field.dsp)
        # SLA   R1,1(R2)
        node = seg.nodes['TS120200.11']
        self.assertEqual('SLA', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual('R0', node.field.index.reg)
        self.assertEqual('R2_AREA', node.field.name)
        self.assertEqual('R2', node.field.base.reg)
        self.assertEqual(1, node.field.dsp)
        # SRA   R3,12
        node = seg.nodes['TS120200.12']
        self.assertEqual('SRA', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('R0', node.field.index.reg)
        self.assertEqual('R0_AREA', node.field.name)
        self.assertEqual('R0', node.field.base.reg)
        self.assertEqual(12, node.field.dsp)
        # SLDA  R2,4
        node = seg.nodes['TS120200.13']
        self.assertEqual('SLDA', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(4, node.field.dsp)
        # SRDA  R2,32
        node = seg.nodes['TS120200.14']
        self.assertEqual('SRDA', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(32, node.field.dsp)
        # MVCL  R2,R6
        node = seg.nodes['TS120300.1']
        self.assertEqual('MVCL', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # MVZ   FLD1,FLD2
        node = seg.nodes['TS120300.2']
        self.assertEqual('MVZ', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(4, node.field_len.length)
        self.assertEqual('R8', node.field.base.reg)
        self.assertTrue(seg.lookup(node.field.name).is_literal)
        self.assertEqual(bytearray([0xC1, 0xC2, 0xC3, 0x40, 0x40]), seg.get_constant_bytes(node.field.name))
        # MVN   FLD1,FLD1+3
        node = seg.nodes['TS120300.3']
        self.assertEqual('MVN', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(4, node.field_len.length)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x503, node.field.dsp)
        # MVO   FIELDB,FIELDA
        node = seg.nodes['TS120300.4']
        self.assertEqual('MVO', node.command)
        self.assertEqual('FIELDB', node.field_len1.name)
        self.assertEqual('R8', node.field_len1.base.reg)
        self.assertEqual(0x013, node.field_len1.dsp)
        self.assertEqual(3, node.field_len1.length)
        self.assertEqual('FIELDA', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x010, node.field_len2.dsp)
        self.assertEqual(2, node.field_len2.length)
        # BCT   R3,TS120300
        node = seg.nodes['TS120300.5']
        self.assertEqual('BCT', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('TS120300', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(70, node.branch.dsp)
        self.assertEqual('R0', node.branch.index.reg)
        self.assertEqual('TS120300', node.goes)
        self.assertSetEqual({'TS120300', 'TS120300.6'}, node.next_labels)
        # BXH   R1,R4,TS120100
        node = seg.nodes['TS120300.6']
        self.assertEqual('BXH', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        self.assertEqual('TS120100', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(8, node.branch.dsp)
        self.assertEqual('R0', node.branch.index.reg)
        self.assertEqual('TS120100', node.goes)
        self.assertSetEqual({'TS120100', 'TS120300.7'}, node.next_labels)
        # BXLE  R2,R6,TS120200
        node = seg.nodes['TS120300.7']
        self.assertEqual('BXLE', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        self.assertEqual('TS120200', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(18, node.branch.dsp)
        self.assertEqual('R0', node.branch.index.reg)
        self.assertEqual('TS120200', node.goes)
        self.assertSetEqual({'TS120200', 'TS120300.8'}, node.next_labels)
        # BASR  R8,R0
        node = seg.nodes['TS120300.8']
        self.assertEqual('BASR', node.command)
        self.assertEqual('R8', node.reg1.reg)
        self.assertEqual('R0', node.reg2.reg)
        # CR    R3,R5
        node = seg.nodes['TS120400.1']
        self.assertEqual('CR', node.command)
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R5', node.reg2.reg)
        # C     R3,FWDA
        node = seg.nodes['TS120400.2']
        self.assertEqual('C', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('FWDA', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x000, node.field.dsp)
        # CHI   R3,-1
        node = seg.nodes['TS120400.3']
        self.assertEqual('CHI', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual(-1, node.data)
        # CL    R3,NUM
        node = seg.nodes['TS120400.4']
        self.assertEqual('CL', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x00c, node.field.dsp)
        # CLR   R3,R4
        node = seg.nodes['TS120400.5']
        self.assertEqual('CLR', node.command)
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # CLM   R3,9,FLD1
        node = seg.nodes['TS120400.6']
        self.assertEqual('CLM', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual(9, node.data)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x500, node.field.dsp)
        # CLCL  R2,R6
        node = seg.nodes['TS120400.7']
        self.assertEqual('CLCL', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # SLL   R1,7
        node = seg.nodes['TS120400.8']
        self.assertEqual('SLL', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual(7, node.field.dsp)
        # SRL   R4,10(R5)
        node = seg.nodes['TS120400.9']
        self.assertEqual('SRL', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual(10, node.field.dsp)
        self.assertEqual('R5', node.field.base.reg)
        # SLDL  R2,4
        node = seg.nodes['TS120400.10']
        self.assertEqual('SLDL', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(4, node.field.dsp)
        # SRDL  R2,32
        node = seg.nodes['TS120400.11']
        self.assertEqual('SRDL', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(32, node.field.dsp)
        # ALR   R5,R15
        # BC    3,TS120400
        node = seg.nodes['TS120400.12']
        self.assertEqual('ALR', node.command)
        self.assertEqual('R5', node.reg1.reg)
        self.assertEqual('R15', node.reg2.reg)
        self.assertEqual('TS120400', node.goes)
        self.assertEqual('BCRY', node.on)
        # AL    R5,ONE
        node = seg.nodes['TS120400.13']
        self.assertEqual('AL', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('ONE', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x008, node.field.dsp)
        # SLR   R1,R3
        # BC    4,TS120400
        node = seg.nodes['TS120400.14']
        self.assertEqual('SLR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        self.assertEqual('TS120400', node.goes)
        self.assertEqual('BL', node.on)
        # SL    R5,ZERO
        node = seg.nodes['TS120400.15']
        self.assertEqual('SL', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('ZERO', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x018, node.field.dsp)
        # NC    FLD1,FLD1
        node = seg.nodes['TS120500.1']
        self.assertEqual('NC', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(4, node.field_len.length)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x500, node.field.dsp)
        # NR    R2,R3
        node = seg.nodes['TS120500.2']
        self.assertEqual('NR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # OR    R0,R3
        node = seg.nodes['TS120500.3']
        self.assertEqual('OR', node.command)
        self.assertEqual('R0', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # XR    R1,R1
        node = seg.nodes['TS120500.4']
        self.assertEqual('XR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        # O     R2,FWD
        node = seg.nodes['TS120500.5']
        self.assertEqual('O', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        # X     R0,FWD
        node = seg.nodes['TS120500.6']
        self.assertEqual('X', node.command)
        self.assertEqual('R0', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        # XI    TEST,X'CA'
        node = seg.nodes['TS120500.7']
        self.assertEqual('TEST', node.field.name)
        self.assertEqual('R6', node.field.base.reg)
        self.assertEqual(0x3cc, node.field.dsp)
        self.assertEqual(0xCA, node.bits.value)
        self.assertEqual('#BIT0=0x80 + #BIT1=0x40 + #BIT4=0x08 + #BIT6=0x02', str(node.bits))
        # ZAP   FLD1,FLD1+1(2)
        node = seg.nodes['TS120600.1']
        self.assertEqual('ZAP', node.command)
        self.assertEqual('FLD1', node.field_len1.name)
        self.assertEqual('R6', node.field_len1.base.reg)
        self.assertEqual(0x500, node.field_len1.dsp)
        self.assertEqual(4, node.field_len1.length)
        self.assertEqual('FLD1', node.field_len2.name)
        self.assertEqual('R6', node.field_len2.base.reg)
        self.assertEqual(0x501, node.field_len2.dsp)
        self.assertEqual(1, node.field_len2.length)
        # AP    WORK,PACKED
        node = seg.nodes['TS120600.2']
        self.assertEqual('AP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('R6', node.field_len1.base.reg)
        self.assertEqual(0x3d0, node.field_len1.dsp)
        self.assertEqual(3, node.field_len1.length)
        self.assertEqual('PACKED', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x01f, node.field_len2.dsp)
        self.assertEqual(1, node.field_len2.length)
        # SP    WORK,PACKED
        node = seg.nodes['TS120600.3']
        self.assertEqual('SP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('PACKED', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x01f, node.field_len2.dsp)
        self.assertEqual(1, node.field_len2.length)
        # MP    WORK,P2
        node = seg.nodes['TS120600.4']
        self.assertEqual('MP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('P2', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x021, node.field_len2.dsp)
        self.assertEqual(1, node.field_len2.length)
        # DP    WORK,P2
        node = seg.nodes['TS120600.5']
        self.assertEqual('DP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(1, node.field_len2.length)
        literal = node.field_len2.name
        self.assertTrue(seg.lookup(literal).is_literal)
        self.assertEqual(bytearray([0x03, 0x9D]), seg.get_constant_bytes(literal))
        # CP    =P'0',FLD2
        node = seg.nodes['TS120600.6']
        self.assertEqual('CP', node.command)
        self.assertEqual('R8', node.field_len1.base.reg)
        self.assertEqual(0, node.field_len1.length)
        literal = node.field_len1.name
        self.assertTrue(seg.lookup(literal).is_literal)
        self.assertEqual(bytearray([0x0C]), seg.get_constant_bytes(literal))
        self.assertEqual('FLD2', node.field_len2.name)
        self.assertEqual('R6', node.field_len2.base.reg)
        self.assertEqual(0x505, node.field_len2.dsp)
        self.assertEqual(4, node.field_len2.length)
        # TP    NUM
        node = seg.nodes['TS120600.7']
        self.assertEqual('TP', node.command)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x00c, node.field.dsp)
        self.assertEqual(3, node.field.length)
        # SRP   FLD1,4,0
        node = seg.nodes['TS120600.8']
        self.assertEqual('SRP', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R6', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(4, node.field_len.length)
        self.assertEqual(4, node.field.dsp)
        self.assertEqual('R0', node.field.base.reg)
        self.assertEqual(0, node.data)
        # TR    INPT,TABLE
        node = seg.nodes['TS120600.9']
        self.assertEqual('TR', node.command)
        self.assertEqual('INPT', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x023, node.field_len.dsp)
        self.assertEqual(2, node.field_len.length)
        self.assertEqual('TABLE', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x026, node.field.dsp)
        # TRT   SENT,FULLTBL
        node = seg.nodes['TS120600.10']
        self.assertEqual('TRT', node.command)
        self.assertEqual('SENT', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x30, node.field_len.dsp)
        self.assertEqual(10, node.field_len.length)
        self.assertEqual('FULLTBL', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x03b, node.field.dsp)
        # ED    PATTERN,PCK1
        node = seg.nodes['TS120600.11']
        self.assertEqual('ED', node.command)
        self.assertEqual('PATTERN', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x13b, node.field_len.dsp)
        self.assertEqual(9, node.field_len.length)
        self.assertEqual('PCK1', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x01c, node.field.dsp)
        # EDMK  PATTERN,PCK1
        node = seg.nodes['TS120600.12']
        self.assertEqual('PATTERN', node.field_len.name)
        self.assertEqual('PCK1', node.field.name)
        # FULLTBL  DC    193X'FF',9X'00',7X'FF',9X'00',8X'FF',8X'00',22X'FF'
        self.assertEqual(bytearray([0xFF] * 193), seg.get_constant_bytes('FULLTBL', 193))
        self.assertEqual(bytearray([0x00] * 9), seg.get_constant_bytes("FULLTBL+C'A'", 9))
        self.assertEqual(bytearray([0xFF] * 7), seg.get_constant_bytes("FULLTBL+C'I'+1", 7))
        self.assertEqual(bytearray([0x00] * 9), seg.get_constant_bytes("FULLTBL+C'J'", 9))
        self.assertEqual(bytearray([0xFF] * 8), seg.get_constant_bytes("FULLTBL+C'R'+1", 8))
        self.assertEqual(bytearray([0x00] * 8), seg.get_constant_bytes("FULLTBL+C'S'", 8))
        self.assertEqual(bytearray([0xFF] * 22), seg.get_constant_bytes("FULLTBL+C'Z'+1", 22))


if __name__ == '__main__':
    unittest.main()
