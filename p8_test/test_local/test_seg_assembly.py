import unittest

from p1_utils.errors import AssemblyError
from p2_assembly.seg6_segment import seg_collection, Segment
from p4_execution.ex5_execute import TpfServer


class SegmentTest(unittest.TestCase):
    SEG_NAME: str = "IGR1"

    def test_segment(self):
        self.maxDiff = None
        seg: Segment = seg_collection.get_seg(self.SEG_NAME)
        try:
            seg.assemble()
        except AssemblyError:
            self.assertFalse(True, msg=seg.error_line)
        unknown = [str(node)[:60] for _, node in seg.nodes.items() if
                   node.command not in TpfServer().supported_commands]
        # all_nodes = [str(node) for _, node in seg.nodes.items()]
        # all_nodes.sort()
        # with open(f"tmp/{self.SEG_NAME}-assemble.txt", "w") as fh:
        #     fh.writelines(f"{node}\n" for node in all_nodes)
        self.assertListEqual(list(), unknown, "\nUnsupported Instruction.")


if __name__ == "__main__":
    unittest.main()
