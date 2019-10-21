import unittest

from assembly.program import program


class AssemblyTest(unittest.TestCase):
    NUMBER_OF_FILES = 40

    def old_common_checks(self, seg_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        program.load(seg_name)
        self.seg = program.segments[seg_name]
        self.assertListEqual(accepted_errors_list, self.seg.errors, '\n\n\n' + '\n'.join(list(
            set(self.seg.errors) - set(accepted_errors_list))))
        self.assertTrue(self.seg.assembled)


if __name__ == '__main__':
    unittest.main()
