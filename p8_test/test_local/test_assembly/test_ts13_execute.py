import unittest

from p2_assembly.seg6_segment import segments, Segment


class Execute(unittest.TestCase):
    def test_execute(self):
        seg: Segment = segments['TS13']
        seg.assemble()
        # TM    EBW000,0
        node = seg.nodes['TS130010.1']
        self.assertEqual('TM', node.command)
        self.assertSetEqual({'TS130010.2'}, node.next_labels)
        # EX    R15,*-4 with BNO   TS130010 on TM    EBW000,0
        node = seg.nodes['TS130010.2']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130010.1', node.field.name)
        ex_node = seg.nodes[node.field.name]
        node = seg.nodes['TS130010.3']
        self.assertEqual('TS130040', node.goes)
        self.assertSetEqual({'TS130010.4', 'TS130040'}, node.next_labels)
        self.assertEqual('TM', ex_node.command)
        self.assertEqual(0, ex_node.bits.value)
        # EX    R1,*-6 on MVC   EBW000,EBT000
        node = seg.nodes['TS130020.2']
        self.assertEqual('EX', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual('TS130020.1', node.field.name)
        self.assertSetEqual({'TS130010'}, node.next_labels)
        ex_node = seg.nodes[node.field.name]
        self.assertEqual('MVC', ex_node.command)
        self.assertEqual(0, ex_node.field_len.length)
        self.assertEqual('EBW000', ex_node.field_len.name)
        self.assertEqual('EBT000', ex_node.field.name)
        # EX    R15,TS130030 on PACK  EBW088(8),4(1,R2)
        node = seg.nodes['TS130010.4']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130030', node.field.name)
        self.assertSetEqual({'TS130030'}, node.next_labels)
        ex_node = seg.nodes[node.field.name]
        self.assertEqual('PACK', ex_node.command)
        self.assertEqual(7, ex_node.field_len1.length)
        self.assertEqual(0, ex_node.field_len2.length)
        self.assertEqual('EBW088', ex_node.field_len1.name)
        self.assertEqual('R2', ex_node.field_len2.base.reg)
        self.assertEqual(4, ex_node.field_len2.dsp)
        # EX    R15,TS130040 with MVC   EBW000,EBT000
        node = seg.nodes['TS130030.1']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130040', node.field.name)
        self.assertSetEqual({'TS130040'}, node.next_labels)
        ex_node = seg.nodes[node.field.name]
        self.assertEqual('DS', ex_node.command)
        ex_node = seg.nodes[seg.nodes[node.field.name].fall_down]
        self.assertEqual('MVC', ex_node.command)
        self.assertEqual(0, ex_node.field_len.length)
        self.assertEqual('EBW000', ex_node.field_len.name)
        self.assertEqual('EBT000', ex_node.field.name)


if __name__ == '__main__':
    unittest.main()
