from typing import List, Union

from p5_v3.p01_errors import ParserError
from p5_v3.p11_base_parser import split_operand, is_segment_name
from p5_v3.p14_symbol_table import SymbolTable
from p5_v3.p15_token_expression import SelfDefinedTerm, Expression
from p5_v3.p19_macro_arguments import MacroArguments
from p5_v3.p20_base_displacement import BaseDisplacement


class GenericFormat:
    def __init__(self, operand: str):
        self.operands: List[str] = split_operand(operand)
        self._parsed_operands: list = self._parse()

    def _parse(self) -> list:
        return list()

    def get_length(self):
        return 0

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

    def raise_error_if_no_operands(self):
        if len(self.operands) == 0:
            raise ParserError

    def number_of_operands(self):
        return len(self._parsed_operands)

    def has_no_operands(self):
        return self.number_of_operands() == 0

    def get_nth_operand(self, n: int):
        try:
            return self._parsed_operands[n - 1]
        except IndexError:
            raise ParserError("ParsedLine -> Invalid index of operand requested.")

    def get_nth_operand_onwards(self, n: int) -> list:
        return self._parsed_operands[n - 1:]


class AssemblerDirectiveFormat(GenericFormat):

    @staticmethod
    def is_assembler_directive() -> bool:
        return True


class TermFormat(AssemblerDirectiveFormat):

    def _parse(self) -> List[SelfDefinedTerm]:
        self.raise_error_if_no_operands()
        return [SelfDefinedTerm(operand) for operand in self.operands]

    def get_length(self, symbol_table: SymbolTable = None) -> int:
        length = 0
        location_counter: int = symbol_table.get_location_counter()
        for term in self._parse():
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


class ExpressionAssemblerDirectiveFormat(AssemblerDirectiveFormat):

    def _parse(self) -> List[Expression]:
        return [Expression(operand) for operand in self.operands if operand]


class EquFormat(ExpressionAssemblerDirectiveFormat):

    def get_length(self, symbol_table: SymbolTable = None) -> int:
        self.raise_error_if_no_operands()
        if len(self.operands) < 2:
            return 1
        return self._parse()[1].evaluate_to_int(symbol_table)

    @staticmethod
    def is_equ() -> bool:
        return True


class OrgFormat(ExpressionAssemblerDirectiveFormat):

    @staticmethod
    def is_org() -> bool:
        return True


class NoOperandAssemblerDirectiveFormat(AssemblerDirectiveFormat):

    def _parse(self) -> list:
        return list()


class DsectFormat(NoOperandAssemblerDirectiveFormat):

    @staticmethod
    def is_dsect() -> bool:
        return True


class CsectFormat(NoOperandAssemblerDirectiveFormat):

    @staticmethod
    def is_csect() -> bool:
        return True


class MachineInstructionFormat(GenericFormat):

    @staticmethod
    def is_machine_instruction() -> bool:
        return True


class EFormat(MachineInstructionFormat):

    def _parse(self) -> list:
        return list()

    def get_length(self) -> int:
        return 2


class RI1Format(MachineInstructionFormat):

    def _parse(self) -> List[Expression]:
        if len(self.operands) not in (1, 2):
            raise ParserError
        return [Expression(self.operands[0]), Expression(self.operands[1]) if len(self.operands) == 2 else Expression("R0")]

    def get_length(self) -> int:
        return 4


class RI2Format(RI1Format):
    pass


class RI2MnemonicFormat(RI2Format):

    def _parse(self) -> List[Expression]:
        self.raise_error_if_operand_count_not_match(1)
        return [Expression(self.operands[0])]


class RIL1Format(RI1Format):
    # The operand 2 is an immediate operand field

    def get_length(self) -> int:
        return 6


class RIL2Format(RIL1Format):
    # The operand 2 is a relative-immediate operand field
    pass


class RRFormat(RI1Format):

    def get_length(self) -> int:
        return 2


class RREFormat(RI1Format):
    pass


class RS1Format(MachineInstructionFormat):

    def _parse(self) -> List[Union[BaseDisplacement, Expression]]:
        if len(self.operands) not in (2, 3):
            raise ParserError
        return [Expression(self.operands[0]), Expression(self.operands[1]),
                BaseDisplacement(self.operands[2]) if len(self.operands) == 3 else BaseDisplacement("R0")]

    def get_length(self) -> int:
        return 4


class RS2Format(RS1Format):
    pass


class RSY1Format(RS1Format):

    def get_length(self) -> int:
        return 6


class RSIFormat(MachineInstructionFormat):

    def _parse(self) -> List[Expression]:
        self.raise_error_if_operand_count_not_match(3)
        return [Expression(self.operands[0]), Expression(self.operands[1]), Expression(self.operands[2])]

    def get_length(self) -> int:
        return 4


class RSLFormat(MachineInstructionFormat):

    def _parse(self) -> List[BaseDisplacement]:
        self.raise_error_if_operand_count_not_match(1)
        return [BaseDisplacement(self.operands[0])]

    def get_length(self) -> int:
        return 6


class RXFormat(MachineInstructionFormat):

    def _parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(2)
        return [Expression(self.operands[0]), BaseDisplacement(self.operands[1])]

    def get_length(self) -> int:
        return 4


class RXMnemonicFormat(RXFormat):

    def _parse(self) -> List[BaseDisplacement]:
        self.raise_error_if_operand_count_not_match(1)
        return [BaseDisplacement(self.operands[0])]


class RXYFormat(RXFormat):
    def get_length(self) -> int:
        return 6


class SFormat(MachineInstructionFormat):

    def _parse(self) -> List[BaseDisplacement]:
        self.raise_error_if_operand_count_not_match(1)
        return [BaseDisplacement(self.operands[0])]


class SIFormat(MachineInstructionFormat):
    def _parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(2)
        return [BaseDisplacement(self.operands[0]), Expression(self.operands[1])]

    def get_length(self) -> int:
        return 4


class SILFormat(MachineInstructionFormat):
    def _parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(2)
        return [BaseDisplacement(self.operands[0]), Expression(self.operands[1])]

    def get_length(self) -> int:
        return 6


class SS1Format(MachineInstructionFormat):
    def _parse(self) -> List[BaseDisplacement]:
        self.raise_error_if_operand_count_not_match(2)
        return [BaseDisplacement(self.operands[0]), BaseDisplacement(self.operands[1])]

    def get_length(self) -> int:
        return 6


class SS2Format(SS1Format):
    pass


class SS3Format(SS1Format):

    def _parse(self) -> List[Union[BaseDisplacement, Expression]]:
        self.raise_error_if_operand_count_not_match(3)
        return [BaseDisplacement(self.operands[0]), BaseDisplacement(self.operands[1]), Expression(self.operands[2])]


class MacroCallFormat(GenericFormat):

    @staticmethod
    def is_macro_call() -> bool:
        return True

    def _parse(self) -> List[MacroArguments]:
        return [MacroArguments(self.operands)]

    def get_length(self) -> int:
        return 4


class NoOperandMacroCallFormat(MacroCallFormat):

    def _parse(self) -> list:
        return list()


class DataMacroCallFormat(MacroCallFormat):
    def _parse(self) -> List[MacroArguments]:
        if all([bool(operand) is False for operand in self.operands]):
            return list()
        return [MacroArguments(self.operands)]

    def get_length(self) -> int:
        return 0


class CallSegmentFormat(MacroCallFormat):

    def return_on_error(self, optional: bool):
        if optional:
            return str()
        raise ParserError("Segment name not found.")

    def get_seg_name_based_on_operand_number(self, operand_number: int, optional: bool = False) -> str:
        macro_arguments: MacroArguments = self._parsed_operands[0]
        if operand_number > macro_arguments.get_number_of_keys():
            return self.return_on_error(optional)
        seg_name: str = macro_arguments.get_nth_key(operand_number)
        if is_segment_name(seg_name):
            return seg_name
        if seg_name == "PROGRAM":
            seg_name: str = macro_arguments.get_value("PROGRAM")
            if is_segment_name(seg_name):
                return seg_name
        return self.return_on_error(optional)

    def get_segment_name(self):
        return self.get_seg_name_based_on_operand_number(1)


class CretcFormat(CallSegmentFormat):

    def get_segment_name(self):
        return self.get_seg_name_based_on_operand_number(2)


class SwiscFormat(CallSegmentFormat):

    def get_segment_name(self):
        return self.get_seg_name_based_on_operand_number(1, optional=True)
