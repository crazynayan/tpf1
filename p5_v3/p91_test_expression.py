import unittest
from typing import List

from p5_v3.p02_source_file import continuation_lines
from p5_v3.p11_base_parser import split_operand
from p5_v3.p14_symbol_table import SymbolTable
from p5_v3.p15_token_expression import SelfDefinedTerm, Expression
from p5_v3.p16_file import StreamPreprocessor
from p5_v3.p17_line import AssemblerLines, AssemblerLine
from p5_v3.p19_macro_arguments import MacroArguments
from p5_v3.p20_base_displacement import BaseDisplacement
from p5_v3.p28_parser import FileParser, ParsedLine
from p5_v3.p30_data_macro import get_data_macro_file_path
from p5_v3.p31_symbol_table_builder import SymbolTableBuilderFromFilename, SymbolTableBuilderFromStream


# noinspection SpellCheckingInspection
class SelfDefinedTermTest(unittest.TestCase):
    WA0AA_FILENAME = get_data_macro_file_path("WA0AA")

    def test_only_data_type(self):
        term = SelfDefinedTerm("X")
        self.assertEqual(None, term.duplication_factor)
        self.assertEqual(1, term.get_duplication_factor_value())
        self.assertEqual("X", term.data_type)
        self.assertEqual(None, term.length)
        self.assertEqual(1, term.get_length_value())

    def test_duplication_factor_as_number(self):
        term = SelfDefinedTerm("2D")
        self.assertEqual(2, term.get_duplication_factor_value())
        self.assertEqual("D", term.data_type)
        self.assertEqual(None, term.length)
        self.assertEqual(8, term.get_length_value())

    def test_length_as_number(self):
        term = SelfDefinedTerm("CL10")
        self.assertEqual(1, term.get_duplication_factor_value())
        self.assertEqual("C", term.data_type)
        self.assertEqual(10, term.get_length_value())

    def test_duplication_factor_and_length_as_expression(self):
        term = SelfDefinedTerm("(4*(3-1))FL(6/3-1)")
        self.assertEqual(8, term.get_duplication_factor_value())
        self.assertEqual("F", term.data_type)
        self.assertEqual(1, term.get_length_value())

    def test_negative_one(self):
        term = SelfDefinedTerm("(-1+3)FD")
        self.assertEqual(2, term.get_duplication_factor_value())
        self.assertEqual("FD", term.data_type)
        self.assertEqual(8, term.get_length_value())

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
        self.assertEqual("01", term.value.get_data())

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
        file_parser = FileParser(self.WA0AA_FILENAME)
        line: ParsedLine = file_parser.get_parsed_line("WA0BID")
        self.assertEqual("WA0BID", line.label)
        self.assertEqual("DS", line.operation_code)
        self.assertEqual("CL2", line.format.get_nth_operand(1).pretty_print())

    def test_continuing_lines(self):
        preprocessor = StreamPreprocessor(continuation_lines)
        lines: List[AssemblerLine] = AssemblerLines(preprocessor.get_lines()).get_lines()
        self.assertEqual("BIG", lines[0].label)
        self.assertEqual("DC", lines[0].operation_code)
        self.assertEqual("Y(ADR1-EXAM,L'ADR1-L'EXAM),X'23',YL1(EXAM+ADR1,L'ZON3+L'HALF1-EXAM+#UI2NXT)", lines[0].operand)
        self.assertEqual(",", lines[3].operand)
        bump_for_org: int = 3
        self.assertEqual("TS110060", lines[bump_for_org + 1].label)
        self.assertEqual("SENDA", lines[bump_for_org + 1].operation_code)
        self.assertEqual("MSG='MAXIMUM NUMBER OF NAMES,PER PNR IS 99 - CREATE NEW PNR'", lines[bump_for_org + 1].operand)
        self.assertEqual("TEST1", lines[bump_for_org + 2].label)
        self.assertEqual("DS", lines[bump_for_org + 2].operation_code)
        self.assertEqual("Y(LONG_LABEL_TO_FILL_UP_SPACE_IN_THE_LINES_OF_OPERANDS+L'SOME_LABEL)", lines[bump_for_org + 2].operand)
        self.assertEqual("MSG='RAMMAANAARJUNA''S DINNER IS ALWAYS MADE FIRST, ISN''T IT?'", lines[bump_for_org + 3].operand)

    def test_term_length(self):
        term = SelfDefinedTerm("X'010'")
        self.assertEqual(2, term.get_length_value())
        term = SelfDefinedTerm("C'CAKE'")
        self.assertEqual(4, term.get_length_value())
        term = SelfDefinedTerm("Z'-123'")
        self.assertEqual(3, term.get_length_value())
        term = SelfDefinedTerm("P'-123'")
        self.assertEqual(2, term.get_length_value())
        term = SelfDefinedTerm("F'0'")
        self.assertEqual(4, term.get_length_value())
        term = SelfDefinedTerm("FL3'0'")
        self.assertEqual(3, term.get_length_value())

    def test_split_operands(self):
        operands = split_operand("0(R2,1),10(R3,1)")
        self.assertEqual(2, len(operands))
        self.assertEqual("0(R2,1)", operands[0])
        self.assertEqual("10(R3,1)", operands[1])
        operands = split_operand("MSG='A,B,C',")
        self.assertEqual(2, len(operands))
        self.assertEqual("MSG='A,B,C'", operands[0])
        self.assertEqual("", operands[1])
        operands = split_operand(",")
        self.assertEqual(2, len(operands))
        self.assertEqual("", operands[0])
        self.assertEqual("", operands[1])

    def test_file_parser(self):
        file_parser = FileParser(self.WA0AA_FILENAME)
        line: ParsedLine = file_parser.get_parsed_line("WA0BID")
        self.assertEqual("WA0BID", line.label)
        self.assertEqual("DS", line.operation_code)
        self.assertEqual("C", line.format.get_nth_operand(1).data_type)
        self.assertEqual(2, line.format.get_nth_operand(1).get_length_value())

    def test_literal(self):
        expression = Expression("=F'2'")
        self.assertTrue(expression.tokens[0].is_literal())
        expression = Expression("S'=P'975.32'")
        self.assertTrue(expression.tokens[0].is_literal())

    def test_symbol_table_builder(self):
        symbol_table: SymbolTable = SymbolTableBuilderFromFilename(self.WA0AA_FILENAME).update_symbol_table()
        self.assertEqual("WA0AA", symbol_table.get_owner("WA0PCL"))
        self.assertEqual(36, symbol_table.get_dsp("#WA0TA4"))
        self.assertEqual(0x80, symbol_table.get_dsp("#WA0PTP"))
        self.assertEqual(0x7F, symbol_table.get_dsp("#WA0IUU"))
        self.assertEqual(0x258, symbol_table.get_dsp("WA0PCL"))
        self.assertEqual(0x2F8, symbol_table.get_dsp("WA2LD6"))
        self.assertEqual(0x70, symbol_table.get_dsp("TPTCPIP"))
        self.assertEqual(0xA1, symbol_table.get_dsp("TP88FF"))
        symbol_table: SymbolTable = SymbolTableBuilderFromStream(continuation_lines, "TEST").update_symbol_table()
        self.assertEqual(7, symbol_table.get_dsp("TS110060"))
        self.assertEqual(5, symbol_table.get_dsp("TEST_ORG"))

    def test_base_displacement(self):
        base_dsp: BaseDisplacement = BaseDisplacement("ABC")
        self.assertEqual(True, base_dsp.is_nth_expression_present(1))
        self.assertEqual(False, base_dsp.is_nth_expression_present(2))
        self.assertEqual(False, base_dsp.is_nth_expression_present(3))
        self.assertEqual("ABC", base_dsp.expression1.tokens[0].get_symbol())
        base_dsp: BaseDisplacement = BaseDisplacement("0(2,R3)")
        self.assertEqual(True, base_dsp.is_nth_expression_present(1))
        self.assertEqual(True, base_dsp.is_nth_expression_present(2))
        self.assertEqual(True, base_dsp.is_nth_expression_present(3))
        self.assertEqual(0, base_dsp.expression1.tokens[0].evaluate_to_int())
        self.assertEqual(2, base_dsp.expression2.tokens[0].evaluate_to_int())
        self.assertEqual("R2", base_dsp.expression2.evaluate_to_register())
        self.assertEqual("R3", base_dsp.expression3.evaluate_to_register())
        base_dsp: BaseDisplacement = BaseDisplacement("0(,)")
        self.assertEqual(True, base_dsp.is_nth_expression_present(1))
        self.assertEqual(False, base_dsp.is_nth_expression_present(2))
        self.assertEqual(False, base_dsp.is_nth_expression_present(3))
        self.assertEqual(0, base_dsp.expression1.tokens[0].evaluate_to_int())

    def test_macro_arguments(self):
        getcc = MacroArguments(["D1", "L4"])
        self.assertEqual("D1", getcc.get_nth_key(1))
        self.assertEqual(True, getcc.is_key_only("D1"))
        dbred = "REF=TR1GAA,REG=R4,BEGIN,KEY1=(PKY=#TR1GK40),KEY2=(R=TR1G_40_OCC,S=$C_AA),KEY3=(R=TR1G_40_ACSTIERCODE,S=FQTUUFF)," \
                "KEY4=(R=TR1G_40_TIER_EFFD,S=EFFD,C=LE),KEY5=(R=TR1G_40_TIER_DISD,S=EFFD,C=GE),ERRORA=TS110020"
        dbred = MacroArguments(split_operand(dbred))
        self.assertEqual(9, dbred.get_number_of_keys())
        self.assertEqual("#TR1GK40", dbred.get_macro_arguments("KEY1").get_value("PKY"))
        self.assertEqual("EFFD", dbred.get_macro_arguments("KEY5").get_value("S"))


if __name__ == '__main__':
    unittest.main()
