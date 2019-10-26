import unittest

from assembly.seg6_segment import Segment, segments
from utils.errors import RegisterInvalidError, ConditionMaskError, BranchInvalidError, NotFoundInSymbolTableError
from utils.file_line import Line


class BranchCondition(unittest.TestCase):
    def test_branch_condition(self):
        seg: Segment = segments['TS06']
        seg.add_label('TS06INVALID', 0, 0, 'NOT_TS06')
        self.assertRaises(BranchInvalidError, seg.branch_mnemonic, Line.from_line(' BNZ TS06INVALID'))
        self.assertRaises(ConditionMaskError, seg.branch_condition, Line.from_line(' JC -1,TS06E100'))
        self.assertRaises(ConditionMaskError, seg.branch_condition, Line.from_line(' BC 16,TS06E100'))
        self.assertRaises(RegisterInvalidError, seg.branch_condition, Line.from_line(' JC 14,8(-1)'))
        self.assertRaises(NotFoundInSymbolTableError, seg.branch_mnemonic, Line.from_line(' JE 12,TS061000'))
        self.assertRaises(ValueError, seg.branch_condition, Line.from_line(' BC TS060100'))
        self.assertRaises(ValueError, seg.branch_condition, Line.from_line(' JC A,TS060100'))
        seg.assemble()
        # LTR  R1, R1 with multiple goes
        node = seg.nodes['TS060100.1']
        self.assertEqual('LTR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        # LR    R2,R3
        node = seg.nodes['TS060100.2']
        self.assertEqual('LR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # JNZ   TS060120
        node = seg.nodes['TS060100.3']
        self.assertEqual('TS060100.4', node.fall_down)
        self.assertEqual('JNZ', node.on)
        self.assertEqual('TS060120', node.goes)
        self.assertEqual('JNZ', node.command)
        self.assertEqual('TS060120', node.branch.name)
        self.assertEqual(7, node.mask)
        self.assertEqual('R0', node.branch.index.reg)
        # LR    R3,R4
        node = seg.nodes['TS060100.4']
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # JP    TS060130
        node = seg.nodes['TS060100.5']
        self.assertEqual('JP', node.command)
        self.assertEqual('TS060130', node.branch.name)
        self.assertEqual(2, node.mask)
        node = seg.nodes['TS060100.6']
        # LR    R5,R6
        self.assertEqual('R5', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # LTR  R2, R2 with a single goes
        node = seg.nodes['TS060110']
        self.assertEqual('R2', node.reg2.reg)
        # LR    R2,R3
        node = seg.nodes['TS060110.1']
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # JC    7,TS060130
        node = seg.nodes['TS060110.2']
        self.assertSetEqual({'TS060110.3', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060110.3', node.fall_down)
        self.assertEqual('JC', node.on)
        self.assertEqual('TS060130', node.goes)
        self.assertEqual('JC', node.command)
        self.assertEqual('TS060130', node.branch.name)
        self.assertEqual(7, node.mask)
        # LR    R3,R4
        node = seg.nodes['TS060110.3']
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # J     TS060100
        node = seg.nodes['TS060110.4']
        self.assertEqual('J', node.command)
        self.assertEqual('TS060100', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertSetEqual({'TS060100'}, node.next_labels)
        self.assertIsNone(node.fall_down)
        self.assertEqual('J', node.on)
        self.assertEqual('TS060100', node.goes)
        # LTR   R3,R3 with a single goes
        node = seg.nodes['TS060120.1']
        self.assertEqual('R3', node.reg2.reg)
        # BC    8,TS060110
        node = seg.nodes['TS060120.2']
        self.assertSetEqual({'TS060120.3', 'TS060110'}, node.next_labels)
        self.assertEqual('TS060120.3', node.fall_down)
        self.assertEqual('BC', node.on)
        self.assertEqual('TS060110', node.goes)
        self.assertEqual('TS060120.2', node.label)
        self.assertEqual('BC', node.command)
        self.assertEqual('TS060110', node.branch.name)
        self.assertEqual(8, node.mask)
        # AR    R5,R2 with a single goes
        node = seg.nodes['TS060120.3']
        self.assertEqual('R2', node.reg2.reg)
        # LR    R2,R4
        node = seg.nodes['TS060120.4']
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # BC    2,TS060120
        node = seg.nodes['TS060120.5']
        self.assertSetEqual({'TS060120', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060130', node.fall_down)
        self.assertEqual('BC', node.on)
        self.assertEqual('TS060120', node.goes)
        self.assertEqual('BC', node.command)
        self.assertEqual('TS060120', node.branch.name)
        self.assertEqual(2, node.mask)
        # LTR   R4,R4 with single goes
        node = seg.nodes['TS060130.1']
        self.assertEqual('R4', node.reg2.reg)
        # BNO   TS060100
        node = seg.nodes['TS060130.2']
        self.assertSetEqual({'TS060100', 'TS060130.3'}, node.next_labels)
        self.assertEqual('TS060130.3', node.fall_down)
        self.assertEqual('BNO', node.on)
        self.assertEqual('TS060100', node.goes)
        self.assertEqual('BNO', node.command)
        self.assertEqual('TS060100', node.branch.name)
        self.assertEqual(14, node.mask)
        # JC    15,TS060120
        node = seg.nodes['TS060130.3']
        self.assertEqual('JC', node.command)
        self.assertEqual('JC', node.on)
        self.assertEqual('TS060130.4', node.fall_down)
        self.assertEqual('TS060120', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertEqual('TS060120', node.goes)
        # BC    15,TS060120
        node = seg.nodes['TS060130.6']
        self.assertEqual('BC', node.command)
        self.assertEqual('BC', node.on)
        self.assertEqual('TS060130.7', node.fall_down)
        self.assertEqual('TS060120', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertEqual('TS060120', node.goes)
        # LR    R3,R5
        node = seg.nodes['TS060130.7']
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R5', node.reg2.reg)
        # BACKC
        node = seg.nodes['TS060130.8']
        self.assertEqual('BACKC', node.command)
        # B     TS060100
        node = seg.nodes['TS060130.9']
        self.assertEqual('B', node.command)
        self.assertEqual('TS060100', node.branch.name)
        self.assertEqual(15, node.mask)
        self.assertSetEqual({'TS060100'}, node.next_labels)
        self.assertIsNone(node.fall_down)
        self.assertEqual('B', node.on)
        self.assertEqual('TS060100', node.goes)
        # Check TS060140
        # BC    0,TS060130
        node = seg.nodes['TS060140.3']
        self.assertEqual('BC', node.command)
        self.assertEqual('TS060130', node.goes)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.4', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060140.4', node.fall_down)
        self.assertEqual('BC', node.on)
        # NOP   TS060130
        node = seg.nodes['TS060140.6']
        self.assertEqual('NOP', node.command)
        self.assertEqual('TS060130', node.goes)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.7', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060140.7', node.fall_down)
        # JC    0,TS060130
        node = seg.nodes['TS060140.9']
        self.assertEqual('JC', node.command)
        self.assertEqual('TS060130', node.goes)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060140.10', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060140.10', node.fall_down)
        # JNOP  TS060130
        node = seg.nodes['TS060140.12']
        self.assertEqual('JNOP', node.command)
        self.assertEqual('TS060130', node.goes)
        self.assertEqual(0, node.mask)
        self.assertSetEqual({'TS060150', 'TS060130'}, node.next_labels)
        self.assertEqual('TS060150', node.fall_down)
        # B     TS06E100(R14)
        node = seg.nodes['TS060150']
        self.assertEqual('B', node.command)
        self.assertEqual(15, node.mask)
        self.assertEqual('TS06E100', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual('R14', node.branch.index.reg)


if __name__ == '__main__':
    unittest.main()
