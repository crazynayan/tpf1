import unittest

from p5_v3.expression import SelfDefinedTerm


class SelfDefinedTermTest(unittest.TestCase):

    def test_only_data_type(self):
        term = SelfDefinedTerm("X")
        self.assertEqual(None, term.duplication_factor)
        self.assertEqual(1, term.duplication_factor_value)
        self.assertEqual("X", term.data_type)
        self.assertEqual(None, term.length)
        self.assertEqual(1, term.length_value)

    def test_duplication_factor_as_number(self):
        term = SelfDefinedTerm("2D")
        self.assertEqual(2, term.duplication_factor_value)
        self.assertEqual("D", term.data_type)
        self.assertEqual(None, term.length)
        self.assertEqual(8, term.length_value)

    def test_length_as_number(self):
        term = SelfDefinedTerm("CL10")
        self.assertEqual(1, term.duplication_factor_value)
        self.assertEqual("C", term.data_type)
        self.assertEqual(10, term.length_value)


if __name__ == '__main__':
    unittest.main()
