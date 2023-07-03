from typing import List, Union

from p5_v3.p01_errors import ParserError
from p5_v3.p11_base_parser import split_operand
from p5_v3.p14_symbol_table import SymbolTable
from p5_v3.p15_token_expression import SelfDefinedTerm, Expression
from p5_v3.p19_macro_arguments import MacroArguments
from p5_v3.p20_base_displacement import BaseDisplacement


class GenericFormat:
    def __init__(self, operand: str):
        self.operands: List[str] = split_operand(operand)

    def is_ds_or_dc(self) -> bool:
        return self.is_ds() or self.is_dc()

    @staticmethod
    def is_assembler_directive() -> bool:
        return False

    @staticmethod
    def is_machine_instruction() -> bool:
        return False

    @staticmethod
    def is_macro_call() -> bool:
        return False

    @staticmethod
    def is_ds() -> bool:
        return False

    @staticmethod
    def is_dc() -> bool:
        return False

    @staticmethod
    def is_equ() -> bool:
        return False

    @staticmethod
    def is_org() -> bool:
        return False

    @staticmethod
    def is_dsect() -> bool:
        return False

    @staticmethod
    def is_csect() -> bool:
        return False

    def raise_error_if_operand_count_not_match(self, number_of_operands: int) -> None:
        if len(self.operands) != number_of_operands:
            raise ParserError


class AssemblerDirectiveFormat(GenericFormat):

    @staticmethod
    def is_assembler_directive() -> bool:
        return True


class MachineInstructionFormat(GenericFormat):

    @staticmethod
    def is_machine_instruction() -> bool:
        return True


class MacroCallFormat(GenericFormat):

    @staticmethod
    def is_macro_call() -> bool:
        return True


class TermFormat(AssemblerDirectiveFormat):

    def parse(self) -> List[SelfDefinedTerm]:
        self.raise_error_if_operand_count_not_match(0)
        return [SelfDefinedTerm(operand) for operand in self.operands]

    def get_length(self, symbol_table: SymbolTable = None) -> int:
        length = 0
        location_counter: int = symbol_table.get_location_counter()
        for term in self.parse():
            term_length: int = term.get_boundary_aligned_adjustment(location_counter) + term.get_length_of_generated_term(symbol_table)
            length += term.length
            location_counter += term_length
        return length


class DSFormat(TermFormat):
    @staticmethod
    def is_ds() -> bool:
        return True


class DCFormat(TermFormat):
    @staticmethod
    def is_dc() -> bool:
        return True


class ExpressionFormat(AssemblerDirectiveFormat):

    def parse(self) -> List[Expression]:
        return [Expression(operand) for operand in self.operands]


class EquFormat(ExpressionFormat):

    def get_length(self, symbol_table: SymbolTable = None) -> int:
        self.raise_error_if_operand_count_not_match(0)
        if len(self.operands) < 2:
            return 1
        return self.parse()[1].evaluate_to_int(symbol_table)

    @staticmethod
    def is_equ() -> bool:
        return True


class OrgFormat(ExpressionFormat):

    @staticmethod
    def is_org() -> bool:
        return True


class AssemblerDirectiveNoOperandFormat(AssemblerDirectiveFormat):

    @staticmethod
    def parse() -> list:
        return list()


class DsectFormat(AssemblerDirectiveNoOperandFormat):

    @staticmethod
    def is_dsect() -> bool:
        return True


class CsectFormat(AssemblerDirectiveNoOperandFormat):

    @staticmethod
    def is_csect() -> bool:
        return True


class RI1Format(GenericFormat):

    def parse(self) -> List[Expression]:
        self.raise_error_if_operand_count_not_match(2)
        return [Expression(self.operands[0]), Expression(self.operands[1])]

    @staticmethod
    def get_length() -> int:
        return 4


class RI2Format(RI1Format):
    pass


class RI2MnemonicFormat(RI2Format):

    def parse(self) -> List[Expression]:
        self.raise_error_if_operand_count_not_match(1)
        return [Expression(self.operands[1])]


class RIL1Format(RI1Format):

    @staticmethod
    def get_length() -> int:
        return 6


class RRFormat(RI1Format):

    @staticmethod
    def get_length() -> int:
        return 2


class RREFormat(RI1Format):
    pass


class RS1Format(GenericFormat):

    def parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(3)
        return [Expression(self.operands[0]), Expression(self.operands[1]), BaseDisplacement(self.operands[2])]

    @staticmethod
    def get_length() -> int:
        return 4


class RS2Format(RS1Format):
    pass


class RSIFormat(GenericFormat):
    def parse(self) -> List[Expression]:
        self.raise_error_if_operand_count_not_match(3)
        return [Expression(self.operands[0]), Expression(self.operands[1]), Expression(self.operands[2])]

    @staticmethod
    def get_length() -> int:
        return 4


class RSLFormat(GenericFormat):

    def parse(self) -> List[BaseDisplacement]:
        self.raise_error_if_operand_count_not_match(1)
        return [BaseDisplacement(self.operands[0])]

    @staticmethod
    def get_length() -> int:
        return 6


class RXFormat(GenericFormat):

    def parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(2)
        return [Expression(self.operands[0]), BaseDisplacement(self.operands[1])]

    @staticmethod
    def get_length() -> int:
        return 4


class RXMnemonicFormat(RXFormat):

    def parse(self) -> List[BaseDisplacement]:
        self.raise_error_if_operand_count_not_match(1)
        return [BaseDisplacement(self.operands[1])]


class RXYFormat(RXFormat):
    @staticmethod
    def get_length() -> int:
        return 6


class SFormat(GenericFormat):

    def parse(self) -> List[BaseDisplacement]:
        self.raise_error_if_operand_count_not_match(1)
        return [BaseDisplacement(self.operands[0])]


class SIFormat(GenericFormat):
    def parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(2)
        return [BaseDisplacement(self.operands[0]), Expression(self.operands[1])]

    @staticmethod
    def get_length() -> int:
        return 4


class SILFormat(GenericFormat):
    def parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(2)
        return [BaseDisplacement(self.operands[0]), Expression(self.operands[1])]

    @staticmethod
    def get_length() -> int:
        return 6


class SS1Format(GenericFormat):
    def parse(self) -> List[BaseDisplacement]:
        self.raise_error_if_operand_count_not_match(2)
        return [BaseDisplacement(self.operands[0]), BaseDisplacement(self.operands[1])]

    @staticmethod
    def get_length() -> int:
        return 6


class SS2Format(SS1Format):
    pass


class SS3Format(SS1Format):

    def parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(3)
        return [BaseDisplacement(self.operands[0]), BaseDisplacement(self.operands[1]), Expression(self.operands[2])]


class MacroCallFormat(GenericFormat):

    def parse(self) -> List[MacroArguments]:
        return [MacroArguments(self.operands)]

    @staticmethod
    def get_length() -> int:
        return 4


class MacroCallNoOperandFormat(MacroCallFormat):

    def parse(self) -> list:
        return list()
