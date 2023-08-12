from typing import Optional, List

from p5_v3.p03_operation_code_tag import OperationCodeTag
from p5_v3.p14_symbol_table import SymbolTable
from p5_v3.p15_token_expression import Expression
from p5_v3.p28_parser import ParsedLines
from p5_v3.p32_using import Using


class UsingBuilder:

    def __init__(self):
        self.symbol_table: Optional[SymbolTable] = None
        self.parser: Optional[ParsedLines] = None
        self.using: Optional[Using] = None

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
