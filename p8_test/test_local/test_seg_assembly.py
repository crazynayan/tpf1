import unittest

from p2_assembly.seg6_segment import segments, Segment
from p4_execution.ex5_execute import TpfServer


class SegmentTest(unittest.TestCase):
    NUMBER_OF_FILES: int = 131
    SEG_NAME: str = "IGR1"

    def test_files(self):
        self.assertTrue("TS02" in segments)
        self.assertTrue("TS01" in segments)
        self.assertFalse("EB0EB" in segments)
        self.assertEqual(self.NUMBER_OF_FILES, len(segments), "Update number of files in SegmentTest")

    def test_segment(self):
        self.maxDiff = None
        seg: Segment = segments[self.SEG_NAME]
        seg.assemble()
        unknown_in_execute = {node.command for _, node in seg.nodes.items() if node.command not in TpfServer()._ex}
        self.assertSetEqual(set(), unknown_in_execute, "\nUnknown in execute.")


if __name__ == "__main__":
    unittest.main()
