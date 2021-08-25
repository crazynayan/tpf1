import unittest

from p1_utils.file_line import Line, File
from p2_assembly.mac2_data_macro import macros
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
        file: File = File(segments[self.SEG_NAME].file_name)
        lines = Line.from_file(file.lines)
        instructions = [line.command for line in lines
                        if line.command not in macros and line.command not in file.macros]
        unknown_in_assembly = {command: "" for command in instructions if command not in seg.all_commands}
        unknown_in_assembly = list(dict.fromkeys(unknown_in_assembly))
        self.assertListEqual(list(), unknown_in_assembly, "\nUnknown in assembly.")
        seg.assemble()
        unknown_in_execute = {node.command for _, node in seg.nodes.items() if node.command not in TpfServer()._ex}
        self.assertSetEqual(set(), unknown_in_execute, "\nUnknown in execute.")

    def test_assemble_segment(self):
        seg: Segment = segments[self.SEG_NAME]
        seg.assemble()


if __name__ == "__main__":
    unittest.main()
