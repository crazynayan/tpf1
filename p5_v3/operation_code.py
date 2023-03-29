from typing import Callable, List

from munch import Munch

from p5_v3.token_expression import SelfDefinedTerm, Expression


class BaseDisplacement:
    pass


class MacroCall:
    pass


class OperationCode:
    PARSE_AS_SPECIFIED, PARSE_BASED_ON_OPERANDS, PARSE_WITH_NO_OPERANDS = 0, 1, 2
    TERM, EXPRESSION, NO_OPERAND, RI1, RIL1, RR, RRE, RS1, RS2, RSL, SI, RX, SS1, SS2, MACRO_CALL = \
        "term", "expression", "no operand", "RI1", "RIL1", "RR", "RRE", "RS1", "RS2", "RSL", "SI", "RX", "SS1", "SS2", "macro call"
    TYPE, PARSER = "type", "parser"
    DOMAIN: Munch = Munch()
    DOMAIN.TERM = DOMAIN.EXPRESSION = DOMAIN.NO_OPERAND = DOMAIN.RI1 = DOMAIN.RIL1 = DOMAIN.RR = DOMAIN.RRE = DOMAIN.RS1 = DOMAIN.RS2 = \
        DOMAIN.RSL = DOMAIN.SI = DOMAIN.RX = DOMAIN.SS1 = DOMAIN.SS2 = DOMAIN.MACRO_CALL = Munch()
    DOMAIN.TERM.TYPE = PARSE_BASED_ON_OPERANDS
    DOMAIN.TERM.PARSER = [SelfDefinedTerm]
    DOMAIN.EXPRESSION.TYPE = PARSE_BASED_ON_OPERANDS
    DOMAIN.EXPRESSION.PARSER = [Expression]
    DOMAIN.NO_OPERAND.TYPE = PARSE_WITH_NO_OPERANDS
    DOMAIN.NO_OPERAND.PARSER = []
    DOMAIN.RI1.TYPE = DOMAIN.RIL1.TYPE = DOMAIN.RR.TYPE = DOMAIN.RRE.TYPE = DOMAIN.RS1.TYPE = DOMAIN.RS2.TYPE = DOMAIN.RSL.TYPE = \
        DOMAIN.SI.TYPE = DOMAIN.RX.TYPE = DOMAIN.SS1.TYPE = DOMAIN.SS2.TYPE = PARSE_AS_SPECIFIED
    DOMAIN.RI1.PARSER = [Expression, Expression]
    DOMAIN.RIL1.PARSER = [Expression, Expression]
    DOMAIN.RR.PARSER = [Expression, Expression]
    DOMAIN.RRE.PARSER = [Expression, Expression]
    DOMAIN.RS1.PARSER = [Expression, Expression, BaseDisplacement]
    DOMAIN.RS2.PARSER = [Expression, Expression, BaseDisplacement]
    DOMAIN.RSL.PARSER = [BaseDisplacement]
    DOMAIN.RX.PARSER = [Expression, BaseDisplacement]
    DOMAIN.SI.PARSER = [BaseDisplacement, Expression]
    DOMAIN.SS1.PARSER = [BaseDisplacement, BaseDisplacement]
    DOMAIN.SS2.PARSER = [BaseDisplacement, BaseDisplacement]
    DOMAIN.MACRO_CALL.TYPE = PARSE_BASED_ON_OPERANDS
    DOMAIN.MACRO_CALL.PARSER = [MacroCall]
    DS, DC, EQU, ORG, DSECT, CSECT, USING, DROP, PUSH, POP, SPACE, EJECT, PRINT, BEGIN, LTORG, FINIS, END = "DS", "DC", "EQU", \
        "ORG", "DSECT", "CSECT", "USING", "DROP", "PUSH", "POP", "SPACE", "EJECT", "PRINT", "BEGIN", "LTORG", "FINIS", "END"
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

    def __init__(self, operation_code):
        self.operation_code: str = operation_code

    def get_operation_domain(self) -> str:
        if self.operation_code not in self.OPERATION:
            return self.MACRO_CALL
        return self.OPERATION[self.operation_code]

    def get_operation_type(self) -> int:
        return self.DOMAIN[self.get_operation_domain()].TYPE

    def get_operation_parsers(self) -> List[Callable]:
        return self.DOMAIN[self.get_operation_domain()].PARSER

    def is_parse_with_no_operands(self):
        return self.get_operation_type() == self.PARSE_WITH_NO_OPERANDS

    def is_parse_based_on_operands(self):
        return self.get_operation_type() == self.PARSE_BASED_ON_OPERANDS

    def is_parse_as_specified(self):
        return self.get_operation_type() == self.PARSE_AS_SPECIFIED
