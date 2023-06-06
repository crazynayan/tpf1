from typing import Callable, List, Set

from munch import Munch

from p5_v3.p01_errors import SymbolTableError
from p5_v3.p15_token_expression import SelfDefinedTerm, Expression


class InstructionLength:
    DEFAULT: int = 4
    LEN_2: Set[str] = {"BCTR", "BR", "LR", "LTR", "AR", "SR", "BER", "BNER", "BHR", "BNHR", "BLR", "BNLR",
                       "BMR", "BNMR", "BPR", "BNPR", "BCR", "BOR", "BNOR", "BZR", "BNZR", "NOPR", "LPR",
                       "LNR", "LCR", "MR", "DR", "MVCL", "BASR", "CR", "CLR", "CLCL", "ALR", "SLR", "NR",
                       "OR", "XR"}
    LEN_6: Set[str] = {"OC", "CLC", "XC", "UNPK", "PACK", "MVC", "MVZ", "MVN", "MVO", "NC", "ZAP", "AP",
                       "SP", "MP", "DP", "CP", "TP", "SRP", "TR", "TRT", "ED", "EDMK"}
    LEN_0: Set[str] = {"PUSH", "USING", "DSECT", "PGMID", "LTORG", "FINIS", "END", "ORG", "POP", "CSECT",
                       "EJECT", "SPACE", "PRINT", "BEGIN", "DROP", "DATAS", "MACRO", "MEND",
                       "AIF", "AGO", "ANOP", "ACTR", "SETA", "SETB", "SETC", "GBLA", "GBLB", "GBLC", "LCLA", "LCLB", "LCLC"}


class BaseDisplacement(Expression):
    pass


class MacroCall(Expression):
    pass


class OperationCodeConstants:
    PARSE_AS_SPECIFIED, PARSE_BASED_ON_OPERANDS, PARSE_WITH_NO_OPERANDS = 0, 1, 2
    TERM, EXPRESSION, NO_OPERAND, RI1, RIL1, RR, RRE, RS1, RS2, RSL, SI, RX, SS1, SS2, MACRO_CALL = \
        "TERM", "EXPRESSION", "NO_OPERAND", "RI1", "RIL1", "RR", "RRE", "RS1", "RS2", "RSL", "SI", "RX", "SS1", "SS2", "MACRO_CALL"
    TYPE, PARSER = "TYPE", "PARSER"
    DOMAIN: Munch = Munch()

    # DOMAIN.TERM = DOMAIN.EXPRESSION = DOMAIN.NO_OPERAND = DOMAIN.RI1 = DOMAIN.RIL1 = DOMAIN.RR = DOMAIN.RRE = DOMAIN.RS1 = DOMAIN.RS2 = \
    #     DOMAIN.RSL = DOMAIN.SI = DOMAIN.RX = DOMAIN.SS1 = DOMAIN.SS2 = DOMAIN.MACRO_CALL = Munch()
    DOMAIN.TERM = Munch()
    DOMAIN.TERM.TYPE = PARSE_BASED_ON_OPERANDS
    DOMAIN.TERM.PARSER = [SelfDefinedTerm]
    DOMAIN.EXPRESSION = Munch()
    DOMAIN.EXPRESSION.TYPE = PARSE_BASED_ON_OPERANDS
    DOMAIN.EXPRESSION.PARSER = [Expression]
    DOMAIN.NO_OPERAND = Munch()
    DOMAIN.NO_OPERAND.TYPE = PARSE_WITH_NO_OPERANDS
    DOMAIN.NO_OPERAND.PARSER = []
    DOMAIN.RI1 = Munch()
    DOMAIN.RI1.TYPE = PARSE_AS_SPECIFIED
    DOMAIN.RI1.PARSER = [Expression, Expression]
    DOMAIN.RIL1 = DOMAIN.RI1
    DOMAIN.RR = DOMAIN.RI1
    DOMAIN.RRE = DOMAIN.RR
    DOMAIN.RS1 = Munch()
    DOMAIN.RS1.TYPE = PARSE_AS_SPECIFIED
    DOMAIN.RS1.PARSER = [Expression, Expression, BaseDisplacement]
    DOMAIN.RS2 = DOMAIN.RS1
    DOMAIN.RSL = Munch()
    DOMAIN.RSL.TYPE = PARSE_AS_SPECIFIED
    DOMAIN.RSL.PARSER = [BaseDisplacement]
    DOMAIN.RX = Munch()
    DOMAIN.RX.TYPE = PARSE_AS_SPECIFIED
    DOMAIN.RX.PARSER = [Expression, BaseDisplacement]
    DOMAIN.SI = Munch()
    DOMAIN.SI.TYPE = PARSE_AS_SPECIFIED
    DOMAIN.SI.PARSER = [BaseDisplacement, Expression]
    DOMAIN.SS1 = Munch()
    DOMAIN.SS1.TYPE = PARSE_AS_SPECIFIED
    DOMAIN.SS1.PARSER = [BaseDisplacement, BaseDisplacement]
    DOMAIN.SS2 = DOMAIN.SS1
    DOMAIN.MACRO_CALL = Munch()
    DOMAIN.MACRO_CALL.TYPE = PARSE_BASED_ON_OPERANDS
    DOMAIN.MACRO_CALL.PARSER = [MacroCall]
    DS, DC, EQU, ORG, DSECT, CSECT, USING, DROP, PUSH, POP, SPACE, EJECT, PRINT, BEGIN, LTORG, FINIS, END, MACRO = "DS", "DC", "EQU", \
        "ORG", "DSECT", "CSECT", "USING", "DROP", "PUSH", "POP", "SPACE", "EJECT", "PRINT", "BEGIN", "LTORG", "FINIS", "END", "MACRO"
    AIF = "AIF"
    OPERATION = Munch()
    OPERATION.DS = TERM
    OPERATION.DC = TERM
    OPERATION.EQU = EXPRESSION
    OPERATION.ORG = EXPRESSION
    OPERATION.DSECT = NO_OPERAND
    OPERATION.CSECT = NO_OPERAND
    OPERATION.USING = EXPRESSION
    OPERATION.DROP = EXPRESSION
    OPERATION.PUSH = EXPRESSION
    OPERATION.POP = EXPRESSION
    OPERATION.SPACE = EXPRESSION
    OPERATION.PRINT = MACRO_CALL
    OPERATION.EJECT = NO_OPERAND
    OPERATION.BEGIN = MACRO_CALL
    OPERATION.LTORG = NO_OPERAND
    OPERATION.FINIS = NO_OPERAND
    OPERATION.END = NO_OPERAND
    OPERATION.MACRO = NO_OPERAND
    # OPERATION.AIF = EXPRESSION


class OperationCode:

    def __init__(self, operation_code: str):
        self.operation_code: str = operation_code

    def __repr__(self):
        return self.operation_code

    def get_operation_code(self):
        return self.operation_code

    def get_operation_domain(self) -> str:
        if self.operation_code not in OperationCodeConstants.OPERATION:
            return OperationCodeConstants.MACRO_CALL
        return OperationCodeConstants.OPERATION[self.operation_code]

    def get_operation_type(self) -> int:
        return OperationCodeConstants.DOMAIN[self.get_operation_domain()].TYPE

    def get_operation_parsers(self) -> List[Callable]:
        return OperationCodeConstants.DOMAIN[self.get_operation_domain()].PARSER

    def is_parse_with_no_operands(self) -> bool:
        return self.get_operation_type() == OperationCodeConstants.PARSE_WITH_NO_OPERANDS

    def is_parse_based_on_operands(self) -> bool:
        return self.get_operation_type() == OperationCodeConstants.PARSE_BASED_ON_OPERANDS

    def is_parse_as_specified(self) -> bool:
        return self.get_operation_type() == OperationCodeConstants.PARSE_AS_SPECIFIED

    def get_length(self) -> int:
        if self.is_ds_or_dc() or self.is_equ():
            raise SymbolTableError
        if self.operation_code in InstructionLength.LEN_0:
            return 0
        if self.operation_code in InstructionLength.LEN_2:
            return 2
        if self.operation_code in InstructionLength.LEN_6:
            return 6
        # Consider raising exception for unknown operation code
        return 4

    def is_dsect(self) -> bool:
        return self.operation_code == OperationCodeConstants.DSECT

    def is_csect(self) -> bool:
        return self.operation_code == OperationCodeConstants.CSECT

    def is_equ(self) -> bool:
        return self.operation_code == OperationCodeConstants.EQU

    def is_ds(self) -> bool:
        return self.operation_code == OperationCodeConstants.DS

    def is_dc(self) -> bool:
        return self.operation_code == OperationCodeConstants.DC

    def is_ds_or_dc(self) -> bool:
        return self.is_ds() or self.is_dc()

    def is_org(self) -> bool:
        return self.operation_code == OperationCodeConstants.ORG
