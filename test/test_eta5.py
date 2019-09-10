import unittest

from v2.directive import AssemblerDirective
from v2.file_line import Line, File
from v2.instruction import Instruction
from v2.segment import Program


class SegmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.program = Program()
        self.seg = None

    def _common_checks(self, seg_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.program.load(seg_name)
        self.seg = self.program.segments[seg_name]
        self.assertListEqual(accepted_errors_list, self.seg.errors, '\n\n\n' + '\n'.join(list(
            set(self.seg.errors) - set(accepted_errors_list))))
        self.assertTrue(self.seg.assembled)

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
        lines = Line.from_file(File.open(self.program.segments[seg_name].file_name))
        unknown = [line.command for line in lines
                   if line.command not in Instruction.INS
                   and line.command not in self.program.macros
                   and line.command not in AssemblerDirective.AD]
        self.assertListEqual(list(), unknown)


if __name__ == '__main__':
    unittest.main()
