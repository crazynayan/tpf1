import unittest

from p1_utils.file_line import Line, File
from p2_assembly.mac2_data_macro import macros
from p2_assembly.seg6_segment import segments, Segment
from p4_execution.ex5_execute import TpfServer


class SegmentTest(unittest.TestCase):
    NUMBER_OF_FILES: int = 74
    SEG_NAME: str = "ETA6"

    def test_files(self):
        self.assertTrue("TS02" in segments)
        self.assertTrue("TS01" in segments)
        self.assertFalse("EB0EB" in segments)
        self.assertEqual(self.NUMBER_OF_FILES, len(segments), "Update number of files in SegmentTest")

    def test_segment(self):
        self.maxDiff = None
        seg: Segment = segments[self.SEG_NAME]
        lines = Line.from_file(File.open(segments[self.SEG_NAME].file_name))
        instructions = [line.command for line in lines if line.command not in macros]
        unknown_in_assembly = {command for command in instructions if command not in seg.all_commands}
        self.assertSetEqual(set(), unknown_in_assembly, "\nUnknown in assembly.")
        seg.assemble()
        unknown_in_execute = {node.command for _, node in seg.nodes.items() if node.command not in TpfServer()._ex}
        self.assertSetEqual(set(), unknown_in_execute, "\nUnknown in execute.")


if __name__ == "__main__":
    unittest.main()
