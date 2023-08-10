from copy import deepcopy
from typing import List, Optional

from p5_v3.p01_errors import UsingError
from p5_v3.p12_register import Registers
from p5_v3.p14_symbol_table import SymbolTable
from p5_v3.p15_token_expression import Expression


class UsingState:

    def __init__(self):
        self._usings: List[list] = [list() for _ in range(16)]

    @staticmethod
    def get_register_number_from_expression(register: Expression) -> int:
        register_number: int = register.evaluate_to_int()
        if not Registers.is_value_valid(register_number):
            raise UsingError
        return register_number

    def add_using(self, register: Expression, dsect_name: str):
        register_number: int = self.get_register_number_from_expression(register)
        self._usings[register_number] = [dsect_name]

    def drop_using(self, register: Expression):
        register_number: int = self.get_register_number_from_expression(register)
        self._usings[register_number] = []

    def add_using_datas(self, register: Expression, dsect_name: str):
        register_number: int = self.get_register_number_from_expression(register)
        self._usings[register_number].append(dsect_name)

    def get_register_number(self, dsect_name: str) -> int:
        try:
            return next(using_index for using_index in range(16) if dsect_name in self._usings[using_index])
        except StopIteration:
            raise UsingError


class Using:
    INVALID_ID: int = -1

    def __init__(self):
        self._using_states: List[UsingState] = list()
        self._using_stack: List[int] = list()

    def get_last_using_id(self) -> int:
        return len(self._using_states) - 1

    def get_last_using_state(self) -> Optional[UsingState]:
        using_id: int = self.get_last_using_id()
        if using_id == self.INVALID_ID:
            return None
        return self.get_using_by_id(using_id)

    def create_copy_of_last_using(self) -> UsingState:
        using_state: UsingState = self.get_last_using_state()
        new_using_state: UsingState = deepcopy(using_state) if using_state else UsingState()
        self._using_states.append(new_using_state)
        return new_using_state

    def get_using_by_id(self, using_id: int) -> UsingState:
        if not (0 <= using_id < len(self._using_states)):
            raise UsingError
        return self._using_states[using_id]

    def add_using(self, register: Expression, dsect_name: str) -> int:
        using_state: UsingState = self.create_copy_of_last_using()
        using_state.add_using(register, dsect_name)
        return self.get_last_using_id()

    def drop_using(self, register: Expression) -> int:
        using_state: UsingState = self.create_copy_of_last_using()
        using_state.drop_using(register)
        return self.get_last_using_id()

    def add_using_datas(self, register: Expression, dsect_name: str) -> int:
        using_state: UsingState = self.create_copy_of_last_using()
        using_state.add_using_datas(register, dsect_name)
        return self.get_last_using_id()

    def push_using(self) -> int:
        using_id: int = self.get_last_using_id()
        if using_id == self.INVALID_ID:
            self.create_copy_of_last_using()
            using_id: int = 0
        self._using_stack.append(using_id)
        return self.get_last_using_id()

    def pop_using(self) -> int:
        using_id: int = self._using_stack.pop()
        new_using_state: UsingState = deepcopy(self.get_using_by_id(using_id))
        self._using_states.append(new_using_state)
        return self.get_last_using_id()

    def get_register_number(self, using_id: int, symbol: str, symbol_table: SymbolTable) -> int:
        using_state: UsingState = self.get_using_by_id(using_id)
        dsect_name: str = symbol_table.get_owner(symbol)
        return using_state.get_register_number(dsect_name)
