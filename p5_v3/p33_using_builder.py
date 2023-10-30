from typing import Optional, List

from p5_v3.p03_operation_code_tag import OperationCodeTag
from p5_v3.p05_domain import ClientDomain
from p5_v3.p14_symbol_table import SymbolTable
from p5_v3.p15_token_expression import Expression
from p5_v3.p28_parser import ParsedLines
from p5_v3.p31_symbol_table_builder import SymbolTableBuilderFromFilename, SymbolTableBuilderFromStream, SymbolTableBuilder
from p5_v3.p32_using import Using


class UsingBuilder:

    def __init__(self, domain: ClientDomain):
        self.symbol_table: Optional[SymbolTable] = None
        self.parser: Optional[ParsedLines] = None
        self.using: Optional[Using] = None
        self.domain: ClientDomain = domain

    def update_using(self) -> Using:
        self.using = Using(self.symbol_table)
        for parsed_line in self.parser.get_lines():
            if parsed_line.is_operation_code(OperationCodeTag.USING):
                register: Expression = parsed_line.format.get_nth_operand(1)
                dsect_names: List[Expression] = parsed_line.format.get_nth_operand_onwards(2)
                self.using.add_using(register, dsect_names)
            elif parsed_line.is_operation_code(OperationCodeTag.DROP):
                registers: List[Expression] = parsed_line.format.get_nth_operand_onwards(1)
                self.using.drop_using(registers)
            elif parsed_line.is_operation_code(OperationCodeTag.PUSH):
                self.using.push_using()
            elif parsed_line.is_operation_code(OperationCodeTag.POP):
                self.using.pop_using()
            parsed_line.set_using_id(self.using.get_last_using_id())
        return self.using


class UsingBuilderFromFilename(UsingBuilder):

    def __init__(self, filename: str, domain: ClientDomain):
        super().__init__(domain)
        symbol_table_builder: SymbolTableBuilderFromFilename = SymbolTableBuilderFromFilename(filename, self.domain)
        symbol_table_builder.update_symbol_table()
        self.parser = symbol_table_builder.parser
        self.symbol_table = symbol_table_builder.symbol_table


class UsingBuilderFromStream(UsingBuilder):

    def __init__(self, buffer: str, owner: str, domain: ClientDomain):
        super().__init__(domain)
        symbol_table_builder: SymbolTableBuilderFromStream = SymbolTableBuilderFromStream(buffer, owner, self.domain)
        symbol_table_builder.update_symbol_table()
        self.parser = symbol_table_builder.parser
        self.symbol_table = symbol_table_builder.symbol_table


class UsingBuilderFromSymbolTableBuilder(UsingBuilder):

    def __init__(self, symbol_table_builder: SymbolTableBuilder):
        super().__init__(symbol_table_builder.domain)
        self.parser = symbol_table_builder.parser
        self.symbol_table = symbol_table_builder.symbol_table
