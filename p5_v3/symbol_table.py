from p5_v3.errors import SymbolNotFoundError
from p5_v3.register import Registers


class Symbol:
    DEFAULT_BASE = Registers.R0
    INVALID_VALUE = -1
    RELOCATABLE_VALUE = -2

    def __init__(self, name, owner):
        self.name: str = name
        self.dsp: int = self.INVALID_VALUE
        self.length: int = self.INVALID_VALUE
        self.base: str = self.DEFAULT_BASE
        self.owner: str = owner

    def set_displacement_as_relocatable(self):
        self.dsp = self.RELOCATABLE_VALUE

    def set_length_as_relocatable(self):
        self.length = self.RELOCATABLE_VALUE

    def is_displacement_evaluated(self):
        return self.dsp not in (self.INVALID_VALUE, self.RELOCATABLE_VALUE)

    def is_length_evaluated(self):
        return self.length not in (self.INVALID_VALUE, self.RELOCATABLE_VALUE)


class SymbolTable:
    DEFAULT_OWNER_PREFIX = "START__"

    def __init__(self, name: str):
        self._symbol_table: dict = dict()
        self.active_usings: dict = dict()
        self.current_location_counter: int = int()
        self.max_location_counter: int = int()
        self.csect_location_counter: int = int()
        self.default_owner_name: str = f"{self.DEFAULT_OWNER_PREFIX}{name}"
        self.current_owner_name: str = self.default_owner_name

    def add_symbol(self, name: str):
        symbol = Symbol(name, self.current_owner_name)
        self._symbol_table[name] = symbol

    def get_symbol(self, name: str) -> Symbol:
        try:
            return self._symbol_table[name]
        except KeyError:
            raise SymbolNotFoundError("SymbolTable -> Symbol not found.")

    def get_dsp(self, name: str) -> int:
        return self.get_symbol(name).dsp

    def get_length(self, name: str) -> int:
        return self.get_symbol(name).length

    def get_base(self, name: str) -> str:
        return self.get_symbol(name).base

    def update_location_counter_by(self, increment: int) -> None:
        self.current_location_counter += increment
        self.max_location_counter = max(self.current_location_counter, self.max_location_counter)

    def get_location_counter(self) -> int:
        return self.current_location_counter

    def get_max_location_counter(self) -> int:
        return self.max_location_counter

    def switch_to_dsect(self, dsect_name: str) -> None:
        if self.current_owner_name == self.default_owner_name:
            self.csect_location_counter = self.current_location_counter
        self.current_owner_name = dsect_name
        self.current_location_counter = self.max_location_counter = 0

    def switch_to_csect(self) -> None:
        self.current_owner_name = self.default_owner_name
        self.current_location_counter = self.max_location_counter = self.csect_location_counter
