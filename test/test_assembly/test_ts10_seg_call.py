import unittest

from assembly2.seg6_segment import segments, Segment


class SegmentCall(unittest.TestCase):
    def test_seg_call(self):
        seg: Segment = segments['TS10']
        seg.assemble()
        # ENTRC TS01
        node = seg.nodes['$$TS10$$.1']
        self.assertEqual('ENTRC', node.command)
        self.assertEqual('TS01', node.keys[0])
        self.assertEqual('$$TS01$$', node.goes)
        self.assertSetEqual({'$$TS01$$', '$$TS10$$.2'}, node.next_labels)
        # ENTNC TS02
        node = seg.nodes['$$TS10$$.3']
        self.assertEqual('ENTNC', node.command)
        self.assertEqual('TS02', node.keys[0])
        self.assertEqual('$$TS02$$', node.goes)
        self.assertSetEqual({'$$TS02$$'}, node.next_labels)
        # ENTDC TS13
        node = seg.nodes['$$TS10$$.2']
        self.assertEqual('ENTDC', node.command)
        self.assertEqual('TS13', node.keys[0])
        self.assertEqual('$$TS13$$', node.goes)
        self.assertSetEqual({'$$TS13$$'}, node.next_labels)


if __name__ == '__main__':
    unittest.main()
