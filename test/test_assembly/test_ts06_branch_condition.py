import unittest

from assembly2.seg6_segment import Segment, segments
from utils.errors import RegisterInvalidError, ConditionMaskError, BranchIndexError, \
    BranchInvalidError, NotFoundInSymbolTableError
from utils.file_line import Line


class BranchCondition(unittest.TestCase):
    def test_branch_condition(self):
        seg: Segment = segments['TS06']
        self.assertRaises(ConditionMaskError, seg.branch_condition, Line.from_line(' JC -1,TS06E100'))
        self.assertRaises(ConditionMaskError, seg.branch_condition, Line.from_line(' BC 12,TS06E100'))
        self.assertRaises(BranchIndexError, seg.branch_condition, Line.from_line(' B 8(R8,R14)'))
        self.assertRaises(RegisterInvalidError, seg.branch_condition, Line.from_line(' JC 14,8(-1)'))
        self.assertRaises(BranchInvalidError, seg.branch_condition, Line.from_line(' BNZ 1000(R8)'))
        self.assertRaises(NotFoundInSymbolTableError, seg.branch_condition, Line.from_line(' JE TS061000'))
        self.assertRaises(ValueError, seg.branch_condition, Line.from_line(' BC TS060100'))
        self.assertRaises(ValueError, seg.branch_condition, Line.from_line(' JC A,TS060100'))
        seg.assemble()
        # Check TS060100
        node = seg.nodes['TS060100.1']
        # LTR  R1, R1 with multiple goes
        self.assertEqual('LTR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        self.assertSetEqual({'TS060120', 'TS060100.2', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060100.2', node.fall_down)
        self.assertEqual('JNZ', node.on)
        self.assertEqual('TS060120', node.goes)
        # LR    R2,R3
        self.assertEqual('LR', node.conditions[0].command)
        self.assertEqual('R2', node.conditions[0].reg1.reg)
        self.assertEqual('R3', node.conditions[0].reg2.reg)
        # JNZ   TS060120
        self.assertEqual('JNZ', node.conditions[1].command)
        self.assertEqual('TS060120', node.conditions[1].branch.name)
        self.assertEqual(7, node.conditions[1].mask)
        self.assertEqual('R0', node.conditions[1].branch.index.reg)
        # LR    R3,R4
        self.assertEqual('R3', node.conditions[2].reg1.reg)
        self.assertEqual('R4', node.conditions[2].reg2.reg)
        # JP    TS060130
        self.assertEqual('JP', node.conditions[3].command)
        self.assertEqual('TS060130', node.conditions[3].branch.name)
        self.assertEqual(2, node.conditions[3].mask)
        node = seg.nodes['TS060100.2']
        # LR    R5,R6
        self.assertEqual('R5', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # Check TS060110
        node = seg.nodes['TS060110']
        # LTR  R2, R2 with a single goes
        self.assertEqual('R2', node.reg2.reg)
        self.assertSetEqual({'TS060110.1', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060110.1', node.fall_down)
        self.assertEqual('BNE', node.on)
        self.assertEqual('TS060130', node.goes)
        # LR    R2,R3
        self.assertEqual('R2', node.conditions[0].reg1.reg)
        self.assertEqual('R3', node.conditions[0].reg2.reg)
        # JC    7,TS060130
        self.assertEqual('BNE', node.conditions[1].command)
        self.assertEqual('TS060130', node.conditions[1].branch.name)
        self.assertEqual(7, node.conditions[1].mask)
        # LR    R3,R4
        node = seg.nodes['TS060110.1']
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # J     TS060100
        node = seg.nodes['TS060110.2']
        self.assertEqual('J', node.command)
        self.assertEqual('TS060100', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertSetEqual({'TS060100'}, node.next_labels)
        self.assertIsNone(node.fall_down)
        self.assertEqual('J', node.on)
        self.assertEqual('TS060100', node.goes)
        # Check TS060120
        node = seg.nodes['TS060120.1']
        # LTR   R3,R3 with a single goes
        self.assertEqual('R3', node.reg2.reg)
        self.assertSetEqual({'TS060120.2', 'TS060110'}, node.next_labels)
        self.assertEqual('TS060120.2', node.fall_down)
        self.assertEqual('BE', node.on)
        self.assertEqual('TS060110', node.goes)
        # BC    8,TS060110
        self.assertEqual('BE', node.conditions[0].command)
        self.assertEqual('TS060110', node.conditions[0].branch.name)
        self.assertEqual(8, node.conditions[0].mask)
        # AR    R5,R2 with a single goes
        node = seg.nodes['TS060120.2']
        self.assertEqual('R2', node.reg2.reg)
        self.assertSetEqual({'TS060120', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060130', node.fall_down)
        self.assertEqual('BH', node.on)
        self.assertEqual('TS060120', node.goes)
        # LR    R2,R4
        self.assertEqual('R2', node.conditions[0].reg1.reg)
        self.assertEqual('R4', node.conditions[0].reg2.reg)
        # BC    2,TS060120
        self.assertEqual('BH', node.conditions[1].command)
        self.assertEqual('TS060120', node.conditions[1].branch.name)
        self.assertEqual(2, node.conditions[1].mask)
        # Check TS060130
        node = seg.nodes['TS060130.1']
        # LTR   R4,R4 with single goes
        self.assertEqual('R4', node.reg2.reg)
        self.assertSetEqual({'TS060100', 'TS060130.2'}, node.next_labels)
        self.assertEqual('TS060130.2', node.fall_down)
        self.assertEqual('BNO', node.on)
        self.assertEqual('TS060100', node.goes)
        # BNO   TS060100
        self.assertEqual('BNO', node.conditions[0].command)
        self.assertEqual('TS060100', node.conditions[0].branch.name)
        self.assertEqual(14, node.conditions[0].mask)
        # JC    15,TS060120 & BC    15,TS060120
        for node in {seg.nodes['TS060130.2'], seg.nodes['TS060130.4']}:
            self.assertEqual('B', node.command)
            self.assertEqual('TS060120', node.branch.name)
            self.assertEqual(15, node.mask)
            self.assertSetEqual({'TS060120'}, node.next_labels)
            self.assertIsNone(node.fall_down)
            self.assertEqual('B', node.on)
            self.assertEqual('TS060120', node.goes)
        # LR    R3,R5
        node = seg.nodes['TS060130.5']
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R5', node.reg2.reg)
        # BACKC
        node = seg.nodes['TS060130.6']
        self.assertEqual('BACKC', node.command)
        # B     TS060100
        node = seg.nodes['TS060130.7']
        self.assertEqual('B', node.command)
        self.assertEqual('TS060100', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertSetEqual({'TS060100'}, node.next_labels)
        self.assertIsNone(node.fall_down)
        self.assertEqual('B', node.on)
        self.assertEqual('TS060100', node.goes)
        # Check TS060140
        # BC    0,TS060130
        node = seg.nodes['TS060140.2']
        self.assertEqual('JNOP', node.command)
        self.assertIsNone(node.branch)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.3'}, node.next_labels)
        self.assertEqual('TS060140.3', node.fall_down)
        self.assertIsNone(node.goes)
        self.assertEqual('JNOP', node.on)
        # NOP   TS060130
        node = seg.nodes['TS060140.4']
        self.assertEqual('NOP', node.command)
        self.assertIsNone(node.branch)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.5'}, node.next_labels)
        self.assertEqual('TS060140.5', node.fall_down)
        # JC    0,TS060130
        node = seg.nodes['TS060140.6']
        self.assertEqual('JNOP', node.command)
        self.assertIsNone(node.branch)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.7'}, node.next_labels)
        self.assertEqual('TS060140.7', node.fall_down)
        # JNOP  TS060130
        node = seg.nodes['TS060140.8']
        self.assertEqual('JNOP', node.command)
        self.assertIsNone(node.branch)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS06E100'}, node.next_labels)
        self.assertEqual('TS06E100', node.fall_down)


if __name__ == '__main__':
    unittest.main()
