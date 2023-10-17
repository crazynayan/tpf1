from typing import List

from p5_v3.p01_errors import SymbolNotFoundError, SymbolTableError
from p5_v3.p12_register import Registers


class SymbolConstants:
    DEFAULT_BASE = Registers.R0
    INVALID_VALUE = -1
    RELOCATABLE_VALUE = -2


class Symbol:

    def __init__(self, name, owner):
        self.name: str = name
        self.dsp: int = SymbolConstants.INVALID_VALUE
        self.length: int = SymbolConstants.INVALID_VALUE
        self.owner: str = owner

    def __repr__(self):
        return f"{self.name:20}{self.dsp:06X}{self.length:5}  {self.owner}"

    def print(self):
        print(str(self))

    def set_displacement_as_relocatable(self):
        self.dsp = SymbolConstants.RELOCATABLE_VALUE

    def set_length_as_relocatable(self):
        self.length = SymbolConstants.RELOCATABLE_VALUE

    def is_displacement_evaluated(self):
        return self.dsp not in (SymbolConstants.INVALID_VALUE, SymbolConstants.RELOCATABLE_VALUE)

    def is_length_evaluated(self):
        return self.length not in (SymbolConstants.INVALID_VALUE, SymbolConstants.RELOCATABLE_VALUE)

    def is_displacement_relocatable(self):
        return self.dsp == SymbolConstants.RELOCATABLE_VALUE

    def is_length_relocatable(self):
        return self.length == SymbolConstants.RELOCATABLE_VALUE

    def set_displacement(self, value: int):
        if value < 0:
            raise SymbolTableError
        self.dsp = value

    def set_length(self, value: int):
        if value < 0:
            raise SymbolTableError
        self.length = value


class SymbolTable:
    DEFAULT_OWNER_PREFIX = str()

    def __init__(self, name: str):
        self._symbol_table: dict = dict()
        self.active_usings: dict = dict()
        self.current_location_counter: int = int()
        self.max_location_counter: int = int()
        self.csect_location_counter: int = int()
        self.default_owner_name: str = f"{self.DEFAULT_OWNER_PREFIX}{name}"
        self.current_owner_name: str = self.default_owner_name

    def add_symbol(self, name: str):
        if self.is_symbol_created(name):
            print(f"Duplicate symbol added: {name}")
        symbol = Symbol(name, self.current_owner_name)
        self._symbol_table[name] = symbol

    def is_symbol_created(self, name: str) -> bool:
        return name in self._symbol_table

    def get_symbol(self, name: str) -> Symbol:
        try:
            return self._symbol_table[name]
        except KeyError:
            raise SymbolNotFoundError("SymbolTable -> Symbol not found.")

    def get_dsp(self, name: str) -> int:
        return self.get_symbol(name).dsp

    def get_length(self, name: str) -> int:
        return self.get_symbol(name).length

    def get_owner(self, name: str) -> str:
        return self.get_symbol(name).owner

    def update_location_counter_by(self, increment: int) -> None:
        self.current_location_counter += increment
        self.max_location_counter = max(self.current_location_counter, self.max_location_counter)

    def set_location_counter(self, location_counter: int) -> None:
        self.current_location_counter = location_counter
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
        if not self.is_symbol_created(dsect_name):
            self.add_symbol(dsect_name)
            self.update_displacement(dsect_name, 0)
            self.update_length(dsect_name, 1)
        return

    def switch_to_csect(self) -> None:
        self.current_owner_name = self.default_owner_name
        self.current_location_counter = self.max_location_counter = self.csect_location_counter

    def update_displacement_as_relocatable(self, label: str):
        symbol: Symbol = self.get_symbol(label)
        symbol.set_displacement_as_relocatable()

    def update_displacement(self, label: str, value: int):
        symbol: Symbol = self.get_symbol(label)
        symbol.set_displacement(value)

    def update_length_as_relocatable(self, label: str):
        symbol: Symbol = self.get_symbol(label)
        symbol.set_length_as_relocatable()

    def update_length(self, label: str, value: int):
        symbol: Symbol = self.get_symbol(label)
        symbol.set_length(value)

    def items(self):
        return self._symbol_table.items()

    def print(self):
        symbols: List[Symbol] = [symbol for _, symbol in self._symbol_table.items()]
        symbols.sort(key=lambda item: item.dsp)
        for symbol in symbols:
            symbol.print()
        return
