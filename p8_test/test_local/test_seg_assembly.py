import unittest

from p2_assembly.seg6_segment import Segment
from p2_assembly.seg9_collection import seg_collection
from p4_execution.ex5_execute import TpfServer


class SegmentTest(unittest.TestCase):
    SEG_NAME: str = "IGR1"

    def test_segment(self):
        self.maxDiff = None
        seg: Segment = seg_collection.get_seg(self.SEG_NAME)
        seg.assemble()
        self.assertEqual(str(), seg.error_line)
        self.assertEqual(str(), seg.error_constant)
        unknown = [str(node)[:60] for _, node in seg.nodes.items() if
                   node.command not in TpfServer().supported_commands]
        # all_nodes = [str(node) for _, node in seg.nodes.items()]
        # all_nodes.sort()
        # with open(f"tmp/{self.SEG_NAME}-assemble.txt", "w") as fh:
        #     fh.writelines(f"{node}\n" for node in all_nodes)
        self.assertListEqual(list(), unknown, "\nUnsupported Instruction.")


if __name__ == "__main__":
    unittest.main()
