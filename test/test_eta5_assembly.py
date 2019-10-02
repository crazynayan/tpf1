import unittest

from test.test_ts08_assembly import AssemblyTest
from assembly.directive import AssemblerDirective
from assembly.file_line import Line, File
from assembly.instruction import Instruction
from assembly.program import program


class SegmentTest(AssemblyTest):
    def test_eta5(self):
        seg_name = 'ETA5'
        accepted_errors_list = [
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # CLI   FQTUSH1-FQTUAAC(R14),C'*' with BNE   ETA9027X
        node = self.seg.nodes['ETA9027X.7']
        self.assertEqual('CLI', node.command)
        self.assertEqual('R14_AREA', node.field.name)
        self.assertEqual(29, node.field.dsp)
        self.assertEqual('R14', node.field.base.reg)
        self.assertEqual(0x5c, node.data)
        self.assertEqual('*', node.data.to_bytes(1, 'big').decode('cp037'))
        self.assertEqual('ETA9027X', node.goes)
        self.assertEqual('BNE', node.on)

    def test_check_segment(self):
        seg_name = 'ETA5'
        self.maxDiff = None
        lines = Line.from_file(File.open(program.segments[seg_name].file_name))
        unknown = [line.command for line in lines
                   if line.command not in Instruction.INS
                   and line.command not in program.macros
                   and line.command not in AssemblerDirective.AD]
        self.assertListEqual(list(), unknown)


if __name__ == '__main__':
    unittest.main()
