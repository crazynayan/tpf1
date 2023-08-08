from typing import Optional, List, Set

from p5_v3.p01_errors import SymbolTableError, SymbolNotFoundError
from p5_v3.p14_symbol_table import SymbolTable, Symbol
from p5_v3.p15_token_expression import Expression, SelfDefinedTerm, Token
from p5_v3.p16_file import File
from p5_v3.p28_parser import ParsedLines, FileParser, ParsedLine, StreamParser
from p5_v3.p30_data_macro import is_data_macro_valid, get_data_macro_file_path


class SymbolTableBuilder:

    def __init__(self):
        self.symbol_table: Optional[SymbolTable] = None
        self.parser: Optional[ParsedLines] = None
        self.macro_names: Set[str] = set()

    def update_symbol_table(self) -> SymbolTable:
        self.evaluate_absolute_symbols()
        self.evaluate_recursively()
        self.evaluate_with_location_counter()
        self.evaluate_inline_data_macro_calls()
        return self.symbol_table

    def evaluate_csect_dsect(self, parsed_line: ParsedLine) -> bool:
        if parsed_line.format.is_csect():
            self.symbol_table.switch_to_csect()
            return True
        if parsed_line.format.is_dsect():
            if not parsed_line.label:
                raise SymbolTableError
            self.symbol_table.switch_to_dsect(parsed_line.label)
            return True
        return False

    def evaluate_absolute_symbols(self) -> None:
        for parsed_line in self.parser.get_lines():
            if self.evaluate_csect_dsect(parsed_line):
                continue
            if not parsed_line.is_label_present():
                continue
            self.symbol_table.add_symbol(parsed_line.label)
            if parsed_line.format.is_equ():
                if parsed_line.format.has_no_operands():
                    raise SymbolTableError
                self.update_symbol_displacement_from_expression(parsed_line.label, parsed_line.format.get_nth_operand(1))
                if parsed_line.format.number_of_operands() == 1 or not parsed_line.format.get_nth_operand(2):
                    self.symbol_table.update_length(parsed_line.label, 1)
                else:
                    self.update_symbol_length_from_expression(parsed_line.label, parsed_line.format.get_nth_operand(2))
                continue
            self.symbol_table.update_displacement_as_relocatable(parsed_line.label)
            if parsed_line.format.is_ds_or_dc():
                if parsed_line.format.has_no_operands():
                    raise SymbolTableError(f"SymbolTableBuilder -> DS/DC has no operands. {parsed_line}")
                term: SelfDefinedTerm = parsed_line.format.get_nth_operand(1)
                if term.is_length_present():
                    self.update_symbol_length_from_expression(parsed_line.label, term.length)
                else:
                    self.symbol_table.update_length(parsed_line.label, term.get_implicit_length())
                continue
            self.symbol_table.update_length(parsed_line.label, parsed_line.format.get_length())
        return

    def evaluate_recursively(self) -> None:
        for label, symbol in self.symbol_table.items():
            if not symbol.is_displacement_evaluated() and not symbol.is_displacement_relocatable():
                self.evaluate_symbol_for_displacement(label)
            if not symbol.is_length_evaluated() and not symbol.is_length_relocatable():
                self.evaluate_symbol_for_length(label)
        return

    def evaluate_symbol_for_displacement(self, label: str) -> Symbol:
        symbol: Symbol = self.symbol_table.get_symbol(label)
        if symbol.is_displacement_evaluated() or symbol.is_displacement_relocatable():
            return symbol
        parsed_line: ParsedLine = self.parser.get_parsed_line(label)
        if not parsed_line.format.is_equ():
            raise SymbolTableError
        expression: Expression = parsed_line.format.get_nth_operand(1)
        relocatable_flag: bool = self.evaluate_expression(expression)
        if relocatable_flag:
            self.symbol_table.update_displacement_as_relocatable(label)
            return self.symbol_table.get_symbol(label)
        displacement: int = expression.evaluate_to_int(self.symbol_table)
        self.symbol_table.update_displacement(label, displacement)
        return self.symbol_table.get_symbol(label)

    def evaluate_symbol_for_length(self, label: str) -> Symbol:
        symbol: Symbol = self.symbol_table.get_symbol(label)
        if symbol.is_length_evaluated() or symbol.is_length_relocatable():
            return symbol
        parsed_line: ParsedLine = self.parser.get_parsed_line(label)
        if parsed_line.format.is_equ():
            if parsed_line.format.has_no_operands():
                raise SymbolTableError
            if parsed_line.format.number_of_operands() == 1 or not parsed_line.format.get_nth_operand(2):
                self.symbol_table.update_length(label, 1)
                return self.symbol_table.get_symbol(label)
            expression: Expression = parsed_line.format.get_nth_operand(2)
        elif parsed_line.format.is_ds_or_dc():
            if parsed_line.format.has_no_operands():
                raise SymbolTableError
            term: SelfDefinedTerm = parsed_line.format.get_nth_operand(1)
            expression: Expression = term.length
        else:
            raise SymbolTableError
        relocatable_flag: bool = self.evaluate_expression(expression)
        if relocatable_flag:
            self.symbol_table.update_length_as_relocatable(label)
            return self.symbol_table.get_symbol(label)
        length: int = expression.evaluate_to_int(self.symbol_table)
        self.symbol_table.update_length(label, length)
        return self.symbol_table.get_symbol(label)

    def evaluate_expression(self, expression: Expression) -> bool:
        relocatable_flag: bool = False
        tokens: List[Token] = expression.get_token_with_symbol()
        for token in tokens:
            symbol_name: str = token.get_symbol()
            if token.is_length_attributed():
                evaluated_symbol: Symbol = self.evaluate_symbol_for_length(symbol_name)
                if evaluated_symbol.is_length_relocatable():
                    relocatable_flag = True
            else:
                evaluated_symbol: Symbol = self.evaluate_symbol_for_displacement(symbol_name)
                if evaluated_symbol.is_displacement_relocatable():
                    relocatable_flag = True
        return relocatable_flag

    def update_symbol_displacement_from_expression(self, label: str, expression: Expression):
        if expression.has_location_counter():
            self.symbol_table.update_displacement_as_relocatable(label)
        elif not expression.has_symbol():
            self.symbol_table.update_displacement(label, expression.evaluate_to_int())
        return

    def update_symbol_length_from_expression(self, label: str, expression: Expression):
        if expression.has_location_counter():
            self.symbol_table.update_length_as_relocatable(label)
        elif not expression.has_symbol():
            self.symbol_table.update_length(label, expression.evaluate_to_int())
        return

    def evaluate_with_location_counter(self):
        for parsed_line in self.parser.get_lines():
            parsed_line.set_location_counter(self.symbol_table.get_location_counter())
            if self.evaluate_csect_dsect(parsed_line):
                continue
            label: str = parsed_line.label if parsed_line.is_label_present() else str()
            symbol: Symbol = self.symbol_table.get_symbol(label) if label else None
            if parsed_line.format.is_equ():
                if not symbol or parsed_line.format.number_of_operands() < 1 or not parsed_line.format.get_nth_operand(1):
                    raise SymbolTableError
                if not symbol.is_displacement_evaluated():
                    self.symbol_table.update_displacement(label, parsed_line.format.get_nth_operand(1).evaluate_to_int(self.symbol_table))
                if not symbol.is_length_evaluated():
                    if parsed_line.format.number_of_operands() < 2 or not parsed_line.format.get_nth_operand(2):
                        raise SymbolTableError
                    self.symbol_table.update_length(label, parsed_line.format.get_nth_operand(2).evaluate_to_int(self.symbol_table))
                continue
            if parsed_line.format.is_org():
                if label:
                    raise SymbolTableError
                if parsed_line.format.number_of_operands() < 1:
                    new_location_counter = self.symbol_table.get_max_location_counter()
                else:
                    try:
                        new_location_counter = parsed_line.format.get_nth_operand(1).evaluate_to_int(self.symbol_table)
                    except SymbolNotFoundError:
                        if parsed_line.format.get_nth_operand(1).pretty_print() == "E&GCDATAS":
                            continue
                        raise SymbolNotFoundError
                self.symbol_table.set_location_counter(new_location_counter)
                continue
            if parsed_line.format.is_ds_or_dc():
                if parsed_line.format.number_of_operands() < 1:
                    raise SymbolTableError
                first_term: SelfDefinedTerm = parsed_line.format.get_nth_operand(1)
                adjusted_counter: int = first_term.get_boundary_aligned_adjustment(self.symbol_table.get_location_counter())
                if symbol and not symbol.is_displacement_evaluated():
                    self.symbol_table.update_displacement(label, self.symbol_table.get_location_counter() + adjusted_counter)
                if symbol and not symbol.is_length_evaluated():
                    self.symbol_table.update_length(label, first_term.get_length_value(self.symbol_table))
                for n in range(1, parsed_line.format.number_of_operands() + 1):
                    term = parsed_line.format.get_nth_operand(n)
                    boundary_alignment: int = term.get_boundary_aligned_adjustment(self.symbol_table.get_location_counter())
                    generated_term_length: int = term.get_length_of_generated_term(self.symbol_table)
                    self.symbol_table.update_location_counter_by(boundary_alignment + generated_term_length)
                continue
            if symbol and not symbol.is_displacement_evaluated():
                self.symbol_table.update_displacement(label, self.symbol_table.get_location_counter())
            self.symbol_table.update_location_counter_by(parsed_line.format.get_length())
        return

    def evaluate_inline_data_macro_calls(self):
        for parsed_line in self.parser.get_lines():
            if not is_data_macro_valid(parsed_line.operation_code):
                continue
            if self.data_macro_already_processed(parsed_line.operation_code):
                continue
            symbol_table_builder = SymbolTableBuilderFromFilename(filename=get_data_macro_file_path(parsed_line.operation_code),
                                                                  symbol_table=self.symbol_table,
                                                                  macro_names=self.macro_names)
            symbol_table_builder.update_symbol_table()
        return

    def data_macro_already_processed(self, data_macro_name: str) -> bool:
        return data_macro_name in self.macro_names


class SymbolTableBuilderFromFilename(SymbolTableBuilder):

    def __init__(self, filename: str, symbol_table: SymbolTable = None, macro_names: Optional[set] = None):
        super().__init__()
        macro_name = File(filename).get_name()
        self.parser = FileParser(filename)
        self.symbol_table = symbol_table if symbol_table else SymbolTable(macro_name)
        self.macro_names: Set[str] = macro_names if macro_names else set()
        self.macro_names.add(macro_name)


class SymbolTableBuilderFromStream(SymbolTableBuilder):

    def __init__(self, buffer: str, owner: str, symbol_table: SymbolTable = None):
        super().__init__()
        self.parser = StreamParser(buffer)
        self.symbol_table = symbol_table if symbol_table else SymbolTable(owner)


class SymbolTableBuilderFromParser(SymbolTableBuilder):

    def __init__(self, name: str, parser: ParsedLines, symbol_table: SymbolTable = None):
        super().__init__()
        self.parser: ParsedLines = parser
        self.symbol_table: SymbolTable = symbol_table if symbol_table else SymbolTable(name)
