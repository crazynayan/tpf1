import unittest

from p2_assembly.seg6_segment import segments, Segment
from p4_execution.ex5_execute import TpfServer


class SegmentTest(unittest.TestCase):
    SEG_NAME: str = "IGR1"

    def test_segment(self):
        self.maxDiff = None
        seg: Segment = segments[self.SEG_NAME]
        seg.assemble()
        unknown = [str(node) for _, node in seg.nodes.items() if node.command not in TpfServer().supported_commands]
        self.assertListEqual(list(), unknown, "\nUnknown in execute.")


if __name__ == "__main__":
    unittest.main()
