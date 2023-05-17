from typing import Optional, List

from p5_v3.errors import SymbolTableError
from p5_v3.file import File
from p5_v3.parser import ParsedLines, FileParser, ParsedLine
from p5_v3.symbol_table import SymbolTable, Symbol
from p5_v3.token_expression import Expression, SelfDefinedTerm, Token


class SymbolTableBuilder:

    def __init__(self):
        self.symbol_table: Optional[SymbolTable] = None
        self.parser: Optional[ParsedLines] = None

    def create(self) -> SymbolTable:
        self.evaluate_absolute_symbols()
        self.evaluate_recursively()
        return self.symbol_table

    def evaluate_absolute_symbols(self) -> None:
        for parsed_line in self.parser.get_lines():
            if parsed_line.operation_code.is_csect():
                self.symbol_table.switch_to_csect()
                continue
            if not parsed_line.is_label_present():
                continue
            if parsed_line.operation_code.is_dsect():
                self.symbol_table.switch_to_dsect(parsed_line.label)
                continue
            self.symbol_table.add_symbol(parsed_line.label)
            if parsed_line.operation_code.is_equ():
                if parsed_line.has_no_operands():
                    raise SymbolTableError
                self.update_symbol_displacement_from_expression(parsed_line.label, parsed_line.get_nth_operand(1))
                if parsed_line.number_of_operands() == 1 or not parsed_line.get_nth_operand(2):
                    self.symbol_table.update_length(parsed_line.label, 1)
                else:
                    self.update_symbol_length_from_expression(parsed_line.label, parsed_line.get_nth_operand(2))
                continue
            self.symbol_table.update_displacement_as_relocatable(parsed_line.label)
            if parsed_line.operation_code.is_ds_or_dc():
                if parsed_line.has_no_operands():
                    raise SymbolTableError(f"SymbolTableBuilder -> DS/DC has no operands. {parsed_line}")
                term: SelfDefinedTerm = parsed_line.get_nth_operand(1)
                if term.is_length_present():
                    self.update_symbol_length_from_expression(parsed_line.label, term.length)
                else:
                    self.symbol_table.update_length(parsed_line.label, term.get_implicit_length())
                continue
            self.symbol_table.update_length(parsed_line.label, parsed_line.operation_code.get_length())
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
        if not parsed_line.operation_code.is_equ():
            raise SymbolTableError
        expression: Expression = parsed_line.get_nth_operand(1)
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
        if parsed_line.operation_code.is_equ():
            if parsed_line.has_no_operands():
                raise SymbolTableError
            if parsed_line.number_of_operands() == 1 or not parsed_line.get_nth_operand(2):
                self.symbol_table.update_length(label, 1)
                return self.symbol_table.get_symbol(label)
            expression: Expression = parsed_line.get_nth_operand(2)
        elif parsed_line.operation_code.is_ds_or_dc():
            if parsed_line.has_no_operands():
                raise SymbolTableError
            term: SelfDefinedTerm = parsed_line.get_nth_operand(1)
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


class SymbolTableBuilderFromFilename(SymbolTableBuilder):

    def __init__(self, filename: str):
        super().__init__()
        file = File(filename)
        self.parser = FileParser(filename)
        self.symbol_table = SymbolTable(file.get_name())


class SymbolTableBuilderFromParser(SymbolTableBuilder):

    def __init__(self, name: str, parser: ParsedLines):
        super().__init__()
        self.parser: ParsedLines = parser
        self.symbol_table: SymbolTable = SymbolTable(name)
