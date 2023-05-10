from typing import Optional, List, Tuple

from p5_v3.base_parser import ParserError, Operators, is_char_first_char_of_symbol, is_char_part_of_symbol, GetIndex
from p5_v3.data_type import DataType
from p5_v3.errors import SymbolTableError
from p5_v3.register import Registers
from p5_v3.symbol_table import SymbolTable


class Token:
    DATA_PREFIX = r"\'"
    LENGTH_PREFIX = f"{Operators.LENGTH_ATTRIBUTE}{Operators.QUOTE}"

    def __init__(self, string: str = None, *, data: bool = False, term: Optional['SelfDefinedTerm'] = None):
        if not string and not term:
            raise ParserError("Token -> Cannot be empty.")
        if string == self.DATA_PREFIX:
            raise ParserError("Token -> Cannot be empty data.")
        if not string and data:
            raise ParserError("Token -> Blank string cannot be data.")
        self._string: str = string if string else str()
        self._term: Optional['SelfDefinedTerm'] = term
        if data:
            self._string = f"{self.DATA_PREFIX}{string}"
        if self.is_attributed() and self._string[2] == Operators.LITERAL_IDENTIFIER:
            self._term = SelfDefinedTerm(self._string[2:])

    def __repr__(self) -> str:
        return self._string

    def evaluate_to_str(self, symbol_table: SymbolTable = None) -> str:
        if self.is_arithmetic_operator() or self.is_parenthesis():
            return self._string
        return str(self.evaluate_to_int(symbol_table))

    def evaluate_to_int(self, symbol_table: SymbolTable = None) -> int:
        if self.is_decimal():
            return self.get_value_from_decimal()
        if self.is_register():
            return self.get_value_from_register()
        if not symbol_table:
            raise ParserError("Token -> Symbol Table not provided to evaluate a symbol or location counter.")
        if self.is_symbol():
            return self.evaluate_symbol(symbol_table)
        if self.is_location_counter():
            return symbol_table.get_location_counter()
        raise ParserError("Token -> Cannot evaluate token.")

    def is_decimal(self) -> bool:
        try:
            int(self._string)
        except ValueError:
            return False
        return True

    def get_value_from_decimal(self) -> int:
        try:
            return int(self._string)
        except ValueError:
            raise ParserError("Token -> Is not decimal.")

    def is_register(self) -> bool:
        return Registers.is_symbol_valid(self._string)

    def get_value_from_register(self) -> int:
        return Registers.get_value(self._string)

    def is_attributed(self) -> bool:
        return len(self._string) > 2 and self._string[0] in Operators.ATTRIBUTES and self._string[1] == Operators.QUOTE

    def is_symbol(self) -> bool:
        if self.is_register():
            return False
        first_char_of_symbol: str = self._string[2] if self.is_attributed() else self._string[0]
        return is_char_first_char_of_symbol(first_char_of_symbol)

    def get_symbol(self) -> str:
        if not self.is_symbol():
            raise SymbolTableError
        return self._string[2:] if self.is_attributed() else self._string

    def is_length_attributed(self) -> bool:
        return self.is_symbol() and self.is_attributed() and self._string[0] == Operators.LENGTH_ATTRIBUTE

    def evaluate_symbol(self, symbol_table: SymbolTable) -> int:
        if self._string.startswith(self.LENGTH_PREFIX):
            return symbol_table.get_length(self._string[len(self.LENGTH_PREFIX):])
        return symbol_table.get_dsp(self._string)

    @property
    def data(self) -> str:
        if self._string[:len(self.DATA_PREFIX)] != self.DATA_PREFIX:
            raise ParserError("Token -> Is not data.")
        return self._string[len(self.DATA_PREFIX):]

    def get_value_from_data(self, data_type) -> int:
        pass

    def is_location_counter(self):
        return self._string == Operators.LOCATION_COUNTER

    def is_arithmetic_operator(self):
        return self._string in Operators.ARITHMETIC

    def is_parenthesis(self):
        return self._string in Operators.PARENTHESIS

    def is_quote(self):
        return self._string == Operators.QUOTE

    def is_self_defined_term(self):
        return self._term is not None

    def is_literal(self):
        return self.is_self_defined_term() and self._term.is_literal()


class Expression:

    def __init__(self, string):
        self.tokens: List[Token] = list()
        self.build(string)

    def __repr__(self):
        return " ".join([str(token) for token in self.tokens])

    def build(self, input_string: str):
        string: str = input_string.strip().upper()
        if not string:
            raise ParserError("Expression -> Input string is empty.")
        start_index: int = 0
        in_symbol: bool = bool()
        in_digit: bool = bool()
        term_end_index: int = int()
        for index, char in enumerate(string):
            if term_end_index:
                if index < term_end_index:
                    continue
                term_end_index = 0
            if in_symbol:
                if is_char_part_of_symbol(char):
                    continue
                if char == Operators.QUOTE and index > 0 and string[index - 1] in Operators.ATTRIBUTES:
                    continue
                if char == Operators.LITERAL_IDENTIFIER and index > 0 and string[index - 1] == Operators.QUOTE:
                    term = SelfDefinedTerm(string[index:])
                    if not term.is_self_defined_term():
                        raise ParserError("Expression -> Attributed literal needs to be a self defined term")
                    term_end_index = term.length_of_string + index
                    continue
            if in_digit and char.isdigit():
                continue
            if index > start_index and (in_symbol or in_digit):
                self.tokens.append(Token(string[start_index:index]))
            in_symbol = in_digit = False
            if char.isalnum() or char == Operators.OPENING_PARENTHESIS or char == Operators.LITERAL_IDENTIFIER:
                term = SelfDefinedTerm(string[index:])
                if term.is_self_defined_term():
                    self.tokens.append(Token(term=term))
                    term_end_index = term.length_of_string + index
                    continue
            if is_char_first_char_of_symbol(char):
                start_index = index
                in_symbol = True
                continue
            if char.isdigit() or (char == Operators.MINUS and (index == 0 or (string[index - 1] == Operators.OPENING_PARENTHESIS))):
                start_index = index
                in_digit = True
                continue
            if is_char_part_of_symbol(char):
                raise ParserError("create_expression -> Invalid seperator.")
            if char == Operators.PRODUCT:
                if index == 0 or string[index - 1] in Operators.ARITHMETIC or string[index - 1] == Operators.OPENING_PARENTHESIS:
                    self.tokens.append(Token(Operators.LOCATION_COUNTER))
                    continue
            self.tokens.append(Token(char))
        if in_symbol or in_digit:
            self.tokens.append(Token(string[start_index:]))
        return

    def evaluate_to_int(self, symbol_table=None) -> int:
        if len(self.tokens) == 1:
            return self.tokens[0].evaluate_to_int(symbol_table)
        expression: str = "".join([token.evaluate_to_str(symbol_table) for token in self.tokens])
        try:
            return eval(expression)
        except (NameError, SyntaxError):
            raise ParserError(f"Expression -> Invalid expression. {expression}")

    def evaluate_to_register(self) -> str:
        register_value = self.evaluate_to_int()
        return Registers.get_symbol(register_value)


class SelfDefinedTerm:
    INVALID_SELF_DEFINED_TERM = -99

    def __init__(self, string: str):
        self._string: str = string.strip()
        self._literal: bool = False
        if self._string and self._string[0] == Operators.LITERAL_IDENTIFIER:
            self._literal = True
            self._string = self._string[1:]
        self.duplication_factor: Optional[Expression] = None
        self.data_type: str = str()
        self.length: Optional[Expression] = None
        self.opening_enclosure: Optional[Token] = None
        self.values: List[Expression] = list()
        self.value: Optional[Token] = None
        self.closing_enclosure: Optional[Token] = None
        self.length_of_string: int = int()
        self.build()

    def build(self):
        data_type_index, length_index = self.build_data_type()
        if not self.is_data_type_present():
            return
        self.build_duplication_factor(data_type_index)
        if not self.is_data_type_present():
            return
        if length_index >= len(self._string):
            return
        value_index = self.build_length(length_index)
        if not self.is_data_type_present():
            return
        if value_index >= len(self._string):
            if self._literal:  # Literals need to have values specified
                self.remove_term()
            return
        self.build_values(value_index)

    def build_data_type(self) -> Tuple[int, int]:
        if not self._string:
            return self.INVALID_SELF_DEFINED_TERM, self.INVALID_SELF_DEFINED_TERM
        data_type_index = 0
        if self._string[data_type_index] == Operators.OPENING_PARENTHESIS or self._string[data_type_index].isdigit():
            data_type_index = GetIndex.after_parenthesis_or_digits(self._string, 0)
        if data_type_index == GetIndex.INVALID_ENCLOSURE or not DataType.is_data_type_at_start_of_string(self._string[data_type_index:]):
            return self.INVALID_SELF_DEFINED_TERM, self.INVALID_SELF_DEFINED_TERM
        self.data_type = DataType.get_data_type_from_start_of_string(self._string[data_type_index:])
        length_index = data_type_index + len(self.data_type)
        return data_type_index, length_index

    def remove_term(self):
        self.duplication_factor: Optional[Expression] = None
        self.data_type: str = str()
        self.length: Optional[Expression] = None
        self.opening_enclosure: Optional[Token] = None
        self.values: List[Expression] = list()
        self.value: Optional[Token] = None
        self.closing_enclosure: Optional[Token] = None
        self.length_of_string: int = int()

    def build_duplication_factor(self, data_type_index: int):
        if data_type_index == 0:
            return
        self.duplication_factor = self.create_expression_for_duplication_factor_or_length(0, data_type_index)

    def build_length(self, length_index: int) -> int:
        if self._string[length_index] != Operators.LENGTH_ATTRIBUTE:
            return length_index
        value_index = GetIndex.after_parenthesis_or_digits(self._string, length_index + 1)
        if value_index == GetIndex.INVALID_ENCLOSURE:
            self.remove_term()
            return self.INVALID_SELF_DEFINED_TERM
        self.length = self.create_expression_for_duplication_factor_or_length(length_index + 1, value_index)
        return value_index

    def build_values(self, value_index: int):
        if self._string[value_index] not in {Operators.QUOTE, Operators.OPENING_PARENTHESIS}:
            self.remove_term()
            return
            # raise ParserError("SelfDefinedTerm -> Values if present should start with a quote or parenthesis.")
        end_index_of_string = GetIndex.after_parenthesis_or_quote(self._string, value_index)
        if end_index_of_string == GetIndex.INVALID_ENCLOSURE:
            self.remove_term()
            return
        string = self._string[value_index:end_index_of_string]
        if len(string) <= 2:
            self.remove_term()
            return
        self.length_of_string = end_index_of_string
        if string[0] == Operators.QUOTE == DataType.get_opening_enclosure(self.data_type):
            self.value = Token(string[1:-1], data=True)
            self.opening_enclosure = self.closing_enclosure = Token(Operators.QUOTE)
        elif string[0] == Operators.OPENING_PARENTHESIS == DataType.get_opening_enclosure(self.data_type):
            self.values = [Expression(value) for value in string[1:-1].split(Operators.COMMA)]
            self.opening_enclosure = Token(Operators.OPENING_PARENTHESIS)
            self.closing_enclosure = Token(Operators.CLOSING_PARENTHESIS)
        else:
            self.remove_term()
        if self.is_literal():
            self.length_of_string += 1
        return

    def is_data_type_present(self) -> bool:
        return bool(self.data_type)

    def is_literal(self) -> bool:
        return self.is_self_defined_term() and self._literal

    def is_duplication_factor_present(self) -> bool:
        return self.duplication_factor is not None

    def is_length_present(self) -> bool:
        return self.length is not None

    def is_self_defined_term(self) -> bool:
        return self.opening_enclosure is not None

    def is_self_defined_term_with_quote(self) -> bool:
        return self.is_self_defined_term() and self.opening_enclosure.is_quote()

    def get_duplication_factor_value(self, symbol_table: SymbolTable = None) -> int:
        return self.duplication_factor.evaluate_to_int(symbol_table) if self.is_duplication_factor_present() else 1

    def get_length_value(self, symbol_table: SymbolTable = None) -> int:
        return self.length.evaluate_to_int(symbol_table) if self.is_length_present() else self.get_implicit_length()

    def get_implicit_length(self) -> int:
        value: str = self.value.data if self.is_self_defined_term_with_quote() else str()
        return DataType.get_length(self.data_type, value)

    def get_length_of_generate_term(self, symbol_table: SymbolTable = None) -> int:
        return self.get_duplication_factor_value(symbol_table) * self.get_length_value(symbol_table)

    def create_expression_for_duplication_factor_or_length(self, start_index: int, end_index: int) -> Optional[Expression]:
        string = self._string[start_index:end_index]
        if string.isdigit():
            return Expression(string)
        if string[0] == Operators.OPENING_PARENTHESIS and string[-1] == Operators.CLOSING_PARENTHESIS:
            return Expression(string[1:-1])
        self.remove_term()
        return None
