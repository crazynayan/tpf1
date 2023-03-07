from typing import Optional, List

from p5_v3.asm_token import Token, AssemblyError, is_data_type, get_data_type, \
    get_index_after_parenthesis_or_digits, Operators, get_data_type_length, is_char_first_char_of_symbol, is_char_part_of_symbol


class Expression:

    def __init__(self, string):
        self.tokens: List[Token] = list()
        self.self_defined_term: Optional[SelfDefinedTerm] = None
        self.build(string)

    def __repr__(self):
        return " ".join([str(token) for token in self.tokens])

    def build(self, input_string: str):
        string: str = input_string.strip().upper()
        if not string:
            raise AssemblyError("create_expression -> Input string is empty.")
        start_index: int = 0
        in_symbol: bool = False
        in_digit: bool = False
        for index, char in enumerate(string):
            if is_char_first_char_of_symbol(char) and not in_symbol:
                start_index = index
                in_symbol = True
                continue
            if in_symbol:
                if is_char_part_of_symbol(char):
                    continue
                if char == Operators.QUOTE and index > 0 and string[index - 1] == Operators.LENGTH_SYMBOL:
                    continue
            if char.isdigit() and not in_digit:
                start_index = index
                in_digit = True
                continue
            if in_digit and char.isdigit():
                continue
            if is_char_part_of_symbol(char):
                raise AssemblyError("create_expression -> Invalid seperator.")
            if index > start_index and (in_symbol or in_digit):
                self.tokens.append(Token(string[start_index:index]))
            in_symbol = False
            in_digit = False
            if char == Operators.PRODUCT:
                if index == 0 or string[index - 1] in Operators.ARITHMETIC or string[index - 1] == Operators.OPENING_PARENTHESIS:
                    self.tokens.append(Token(Operators.LOCATION_COUNTER))
                    continue
            self.tokens.append(Token(char))
        if in_symbol or in_digit:
            self.tokens.append(Token(string[start_index:]))
        return

    def has_arithmetic_operator(self) -> bool:
        return any(token for token in self.tokens if token.is_arithmetic_operator())

    def has_symbol_or_location_counter(self) -> bool:
        return any(token for token in self.tokens if token.is_symbol() or token.is_location_counter())

    def evaluate(self) -> int:
        if not self.tokens:
            # TODO : Evaluate for self_defined_term
            raise AssemblyError("Expression -> Evaluate only works with tokens.")
        if self.has_symbol_or_location_counter():
            # TODO : Evaluate for symbols and location counter
            raise AssemblyError("Expression -> Evaluate does not work with symbols or location counter")
        if len(self.tokens) == 1:
            return self.tokens[0].evaluate()
        expression: str = "".join([token.evaluate_to_str() for token in self.tokens])
        try:
            return eval(expression)
        except (NameError, SyntaxError):
            raise AssemblyError(f"Expression -> Invalid expression. {expression}")


class SelfDefinedTerm:

    def __init__(self, string):
        self.duplication_factor: Optional[Expression] = None
        self.data_type: str = str()
        self.length: Optional[Expression] = None
        self.opening_enclosure: Optional[Token] = None
        self.values: List[Expression] = list()
        self.value: Optional[Token] = None
        self.closing_enclosure: Optional[Token] = None
        self.build(string)

    def build(self, input_string: str):
        string = input_string.strip().upper()
        if not string:
            raise AssemblyError("SelfDefinedTerm -> Input string cannot be empty.")
        data_type_index = get_index_after_parenthesis_or_digits(string, 0)
        if not is_data_type(string[data_type_index:]):
            raise AssemblyError("SelfDefinedTerm -> The string does not have a valid data type.")
        if data_type_index > 0:
            self.build_duplication_factor(string[:data_type_index])
        self.data_type = get_data_type(string[data_type_index:])
        length_index = data_type_index + len(self.data_type)
        if length_index >= len(string):
            return
        if string[length_index] == "L":
            value_index = get_index_after_parenthesis_or_digits(string, length_index + 1)
            if value_index == 0:
                raise AssemblyError("SelfDefinedTerm -> Length after L is not specified.")
            self.build_length(string[length_index + 1:value_index])
        else:
            value_index = length_index
        if value_index < len(string):
            self.build_values(string[value_index:])
        return

    def build_duplication_factor(self, string: str):
        self.duplication_factor = create_expression_for_duplication_factor_or_length(string)

    def build_length(self, string: str):
        self.length = create_expression_for_duplication_factor_or_length(string)

    def build_values(self, string: str):
        if string[0] == Operators.QUOTE:
            if string[-1] != Operators.QUOTE or len(string) <= 2:
                raise AssemblyError("SelfDefinedTerm -> Values within quotes should have data and end with quote.")
            self.opening_enclosure = self.closing_enclosure = Token(Operators.QUOTE)
            self.value = Token(string[1:-1], data=True)
            return
        if string[0] != Operators.OPENING_PARENTHESIS:
            raise AssemblyError("SelfDefinedTerm -> Values if present should start with parenthesis or quotes.")
        if string[-1] != Operators.CLOSING_PARENTHESIS or len(string) <= 2:
            raise AssemblyError("SelfDefinedTerm -> Values within parenthesis should have data and end with parenthesis.")
        self.values = [Expression(value) for value in string[1:-1].split(Operators.COMMA)]
        self.opening_enclosure = Token(Operators.OPENING_PARENTHESIS)
        self.closing_enclosure = Token(Operators.CLOSING_PARENTHESIS)

    @property
    def duplication_factor_value(self) -> int:
        return self.duplication_factor.evaluate() if self.duplication_factor else 1

    @property
    def length_value(self) -> int:
        return self.length.evaluate() if self.length else get_data_type_length(self.data_type)


def create_expression_for_duplication_factor_or_length(string: str) -> Expression:
    if string.isdigit():
        return Expression(string)
    if string[0] == Operators.OPENING_PARENTHESIS and string[-1] == Operators.CLOSING_PARENTHESIS:
        return Expression(string[1:-1])
    raise AssemblyError("create_expression_for_duplication_factor_or_length -> Invalid string.")
