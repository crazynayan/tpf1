import unittest

from p5_v3.asm_token import AssemblyError
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

    def test_duplication_factor_and_length_as_expression(self):
        term = SelfDefinedTerm("(4*(3-1))fl(6/3-1)")
        self.assertEqual(8, term.duplication_factor_value)
        self.assertEqual("F", term.data_type)
        self.assertEqual(1, term.length_value)

    def test_negative_one(self):
        term = SelfDefinedTerm("(-1+3)FD")
        self.assertEqual(2, term.duplication_factor_value)
        self.assertEqual("FD", term.data_type)
        self.assertEqual(8, term.length_value)

    def test_location_counter(self):
        term = SelfDefinedTerm("A(*+2,@ABC)")
        self.assertTrue(term.values.tokens[0].is_parenthesis())
        self.assertTrue(term.values.tokens[1].is_location_counter())
        self.assertTrue(term.values.tokens[2].is_arithmetic_operator())
        self.assertTrue(term.values.tokens[3].is_decimal())
        self.assertTrue(term.values.tokens[4].is_comma())
        self.assertTrue(term.values.tokens[5].is_symbol())
        print("".join([token.evaluate_to_str(symbol_table="abc", location_counter=23) for token in term.values.tokens[:4]]))

    def test_error_invalid_data_type(self):
        self.assertRaises(AssemblyError, SelfDefinedTerm, "E")

    def test_error_length_not_specified(self):
        self.assertRaises(AssemblyError, SelfDefinedTerm, "FL")

    def test_error_length_invalid(self):
        self.assertRaises(AssemblyError, SelfDefinedTerm, "FL'1'")

    def test_error_term_empty(self):
        self.assertRaises(AssemblyError, SelfDefinedTerm, " ")

    # def test_file_preprocessor(self):
    #     preprocessor = FilePreprocessor("p0_source/sabre/macro/wa0aa.mac")
    #     [print(line) for line in preprocessor.process()]

if __name__ == '__main__':
    unittest.main()
