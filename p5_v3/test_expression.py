import unittest

from p5_v3.line import AssemblerLines
from p5_v3.token_expression import SelfDefinedTerm, Expression


# noinspection SpellCheckingInspection
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
        term = SelfDefinedTerm("(4*(3-1))FL(6/3-1)")
        self.assertEqual(8, term.duplication_factor_value)
        self.assertEqual("F", term.data_type)
        self.assertEqual(1, term.length_value)

    def test_negative_one(self):
        term = SelfDefinedTerm("(-1+3)FD")
        self.assertEqual(2, term.duplication_factor_value)
        self.assertEqual("FD", term.data_type)
        self.assertEqual(8, term.length_value)

    def test_location_counter(self):
        term = SelfDefinedTerm("A(*+2-R1+#EQ-L'J,@ABC)")
        self.assertTrue(term.opening_enclosure.is_parenthesis())
        self.assertTrue(term.closing_enclosure.is_parenthesis())
        self.assertTrue(term.values[0].tokens[0].is_location_counter())
        self.assertTrue(term.values[0].tokens[1].is_arithmetic_operator())
        self.assertTrue(term.values[0].tokens[2].is_decimal())
        self.assertTrue(term.values[1].tokens[0].is_symbol())
        # print("".join([token.evaluate_to_str(symbol_table="abc", location_counter=23) for token in term.values[0].tokens]))

    def test_error_invalid_data_type(self):
        self.assertFalse(SelfDefinedTerm("E").is_data_type_present())

    def test_error_length_not_specified(self):
        self.assertFalse(SelfDefinedTerm("FL").is_data_type_present())

    def test_error_length_invalid(self):
        self.assertFalse(SelfDefinedTerm("FL'1'").is_data_type_present())

    def test_error_term_empty(self):
        self.assertFalse(SelfDefinedTerm(" ").is_data_type_present())

    def test_term(self):
        term = SelfDefinedTerm("X'01'")
        self.assertTrue(term.is_self_defined_term())
        self.assertEqual("X", term.data_type)
        self.assertTrue(term.opening_enclosure.is_quote())
        self.assertEqual("01", term.value.data)

    def test_error_term_start_with_arithmetic(self):
        self.assertFalse(SelfDefinedTerm("+F").is_data_type_present())

    def test_expression_register(self):
        register = Expression("2+3*4-6").evaluate_to_register()
        self.assertEqual("R8", register)
        self.assertFalse(Expression("R8").tokens[0].is_symbol())

    def test_term_in_expression(self):
        expression = Expression("X'FF'-#BIT2")
        self.assertTrue(expression.tokens[0].is_self_defined_term())
        self.assertTrue(expression.tokens[1].is_arithmetic_operator())
        self.assertTrue(expression.tokens[2].is_symbol())
        self.assertFalse(SelfDefinedTerm("X''").is_data_type_present())
        self.assertFalse(SelfDefinedTerm("X'01").is_data_type_present())

    def test_file_preprocessor(self):
        from p5_v3.file import FilePreprocessor
        preprocessor = FilePreprocessor("p0_source/sabre/macro/wa0aa.mac")
        lines = AssemblerLines(preprocessor.process()).process()
        self.assertEqual("WA0BID&LC0", lines[14].label)
        self.assertEqual("DS", lines[14].command)
        self.assertEqual("CL2", lines[14].operand)

    def test_continuing_lines(self):
        from p5_v3.file import StreamPreprocessor
        from p5_v3.source_file import continuation_lines
        preprocessor = StreamPreprocessor(continuation_lines)
        lines = AssemblerLines(preprocessor.process()).process()
        self.assertEqual("BIG", lines[0].label)
        self.assertEqual("DC", lines[0].command)
        self.assertEqual("Y(ADR1-EXAM,L'ADR1-L'EXAM),X'23',YL1(EXAM+ADR1,L'ZON3+L'HALF1-EXAM+#UI2NXT)", lines[0].operand)
        self.assertEqual("TS110060", lines[1].label)
        self.assertEqual("SENDA", lines[1].command)
        self.assertEqual("MSG='MAXIMUM NUMBER OF NAMES,PER PNR IS 99 - CREATE NEW PNR'", lines[1].operand)
        self.assertEqual("TEST1", lines[2].label)
        self.assertEqual("DS", lines[2].command)
        self.assertEqual("Y(LONG_LABEL_TO_FILL_UP_SPACE_IN_THE_LINES_OF_OPERANDS+L'SOME_LABEL)", lines[2].operand)

    def test_term_length(self):
        term = SelfDefinedTerm("X'010'")
        self.assertEqual(2, term.length_value)
        term = SelfDefinedTerm("C'CAKE'")
        self.assertEqual(4, term.length_value)
        term = SelfDefinedTerm("Z'-123'")
        self.assertEqual(3, term.length_value)
        term = SelfDefinedTerm("P'-123'")
        self.assertEqual(2, term.length_value)
        term = SelfDefinedTerm("F'0'")
        self.assertEqual(4, term.length_value)
        term = SelfDefinedTerm("FL3'0'")
        self.assertEqual(3, term.length_value)


if __name__ == '__main__':
    unittest.main()
