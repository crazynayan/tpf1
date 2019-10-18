import unittest

from assembly.directive import Directive
from assembly.file_line import Line, File
from assembly.instruction import Instruction
from assembly.program import program
from test.test_ts08_assembly import AssemblyTest
from utils.test_data import T


class SegmentTest(AssemblyTest):
    def setUp(self) -> None:
        self.seg_name = 'ETA5'

    def test_segment(self):
        self.old_common_checks(self.seg_name)
        # CLI   FQTUSH1-FQTUAAC(R14),C'*' with BNE   ETA9027X
        # node = self.seg.nodes['ETA9027X.7']
        # self.assertEqual('CLI', node.command)
        # self.assertEqual('R14_AREA', node.field.name)
        # self.assertEqual(29, node.field.dsp)
        # self.assertEqual('R14', node.field.base.reg)
        # self.assertEqual(0x5c, node.data)
        # self.assertEqual('*', DataType('X', bytes=bytes([node.data])).decode)
        # self.assertEqual('ETA9027X', node.goes)
        # self.assertEqual('BNE', node.on)

    def test_check_segment(self):
        self.maxDiff = None
        lines = Line.from_file(File.open(program.segments[self.seg_name].file_name))
        instructions = [line.command for line in lines
                        if line.command not in [*list(Directive.AD), *list(program.macros), *['GLOBZ']]
                        and not line.is_check_cc]
        unknown_in_assembly = {command for command in instructions if command not in Instruction.INS}
        self.assertSetEqual(set(), unknown_in_assembly, "\nUnknown in assembly.")
        unknown_in_execute = {command for command in instructions if command not in T.state.ex}
        self.assertSetEqual(set(), unknown_in_execute, "\nUnknown in execute.")


if __name__ == '__main__':
    unittest.main()
