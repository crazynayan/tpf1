from datetime import datetime
from typing import Union, Optional, Tuple, Dict

from assembly.mac2_data_macro import macros
from config import config
from utils.data_type import DataType, Register


class Registers:
    ORDER = ('R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15')
    LEN = 4
    L = 0xFFFFFFFF

    def __init__(self):
        self.R0 = 0
        self.R1 = 0
        self.R2 = 0
        self.R3 = 0
        self.R4 = 0
        self.R5 = 0
        self.R6 = 0
        self.R7 = 0
        self.R8 = 0
        self.R9 = 0
        self.R10 = 0
        self.R11 = 0
        self.R12 = 0
        self.R13 = 0
        self.R14 = 0
        self.R15 = 0

    def __repr__(self) -> str:
        return f"R0:{self.R0 & self.L:08x},R1:{self.R1 & self.L:08x},R2:{self.R2 & self.L:08x}," \
               f"R3:{self.R3 & self.L:08x},R4:{self.R4 & self.L:08x},R5:{self.R5 & self.L:08x},"

    def get_bytes(self, reg: Union[str, Register]) -> bytearray:
        return DataType('F', input=str(self.get_value(reg))).to_bytes(self.LEN)

    def get_value(self, reg: Union[str, Register]) -> int:
        try:
            return getattr(self, str(reg))
        except AttributeError:
            raise AttributeError

    def get_unsigned_value(self, reg: Union[str, Register]) -> int:
        return self.get_value(reg) & self.L

    def get_address(self, base: Register, dsp: int, index: Optional[Register] = None) -> int:
        return (self.get_value(base) if str(base) != 'R0' else 0) + dsp + \
               (self.get_value(index) if index and str(index) != 'R0' else 0)

    def next_reg(self, reg: str) -> str:
        self.get_value(reg)
        return self.ORDER[0] if reg == self.ORDER[-1] else self.ORDER[self.ORDER.index(reg) + 1]

    def get_bytes_from_mask(self, reg: Register, mask: int) -> bytearray:
        reg_bytes = self.get_bytes(reg)
        try:
            return bytearray([reg_bytes[index] for index, bit in enumerate(f'{mask:04b}') if bit == '1'])
        except IndexError:
            raise IndexError

    def set_bytes(self, byte_array: bytearray, reg: Register) -> None:
        self.get_value(reg)
        if len(byte_array) != self.LEN:
            raise ValueError
        setattr(self, str(reg), DataType('F', bytes=byte_array).value)

    def set_value(self, value: int, reg: Union[Register, str]) -> None:
        self.get_value(reg)
        setattr(self, str(reg), value)

    def set_bytes_from_mask(self,  byte_array: bytearray, reg: Register, mask: int) -> None:
        reg_bytes = self.get_bytes(reg)
        if len(byte_array) < bin(mask).count('1'):
            raise ValueError
        try:
            reg_bytes = [byte_array.pop(0) if bit == '1' else reg_bytes[index]
                         for index, bit in enumerate(f'{mask:04b}')]
        except IndexError:
            raise IndexError
        setattr(self, str(reg), DataType('F', bytes=bytearray(reg_bytes)).value)


class Storage:
    def __init__(self):
        self.frames: Dict[str, bytearray] = dict()                 # Frames init with ZERO
        self._frame: Dict[str, bytearray] = dict()                 # Frames init with ONES
        self.nab: int = config.F4K << config.NIBBLE  # To ensure total 16 fixed frames
        self.allocate_fixed(config.ECB)
        self.allocate_fixed(config.GLOBAL)
        self.allocate_fixed(config.AAA)
        self.allocate_fixed(config.IMG)
        self._setup_global()

    def __repr__(self) -> str:
        return f"Storage:{len(self.frames)}"

    def allocate(self) -> int:
        base_address = self.base_key(self.nab)
        self.frames[base_address] = bytearray()
        self._frame[base_address] = bytearray()
        self.nab += config.F4K
        return self.nab - config.F4K

    def allocate_fixed(self, address: int) -> None:
        base_address = self.base_key(address)
        self.frames[base_address] = bytearray()
        self._frame[base_address] = bytearray()

    def _setup_global(self):
        haalc = config.GLOBAL + macros['GLOBAL'].evaluate('@HAALC')
        self.set_bytes(bytearray([0xC1, 0xC1]), haalc, 2)
        u1dmo = config.GLOBAL + macros['GLOBAL'].evaluate('@U1DMO')
        today = datetime.today()
        today = datetime(year=today.year, month=today.month, day=today.day)
        pars_today = (today - config.START).days
        self.set_value(pars_today, u1dmo, 2)

    def get_allocated_address(self) -> bytearray:
        return DataType('F', input=str(self.nab - config.F4K)).to_bytes(Registers.LEN)

    @staticmethod
    def base_key(address: int) -> str:
        address = (address >> config.DSP_SHIFT) << config.DSP_SHIFT
        return f"{address:08x}"

    @staticmethod
    def dsp(address: int) -> int:
        return address & (config.F4K - 1)

    def extend_frame(self, base_address: str, length: int) -> None:
        try:
            frame_len = len(self.frames[base_address])
        except KeyError:
            raise KeyError
        if length > frame_len:
            self.frames[base_address].extend(bytearray([config.ZERO] * (length - frame_len)))
            self._frame[base_address].extend(bytearray([config.ONES] * (length - frame_len)))

    def _get_data(self, address: int, length: Optional[int] = None) -> Tuple[str, int, int]:
        base_address = self.base_key(address)
        start = self.dsp(address)
        end = start + 1 if length is None else start + length
        self.extend_frame(base_address, end)
        return base_address, start, end

    def get_bytes(self, address: int, length: Optional[int] = None) -> bytearray:
        base_address, start, end = self._get_data(address, length)
        return self.frames[base_address][start: end]

    def get_byte(self, address: int) -> int:
        base_address, dsp, _ = self._get_data(address)
        return self.frames[base_address][dsp]

    def get_value(self, address: int, length: int = 4) -> int:
        return DataType('F', bytes=self.get_bytes(address, length)).value

    def get_unsigned_value(self, address: int, length: int = 4) -> int:
        return DataType('X', bytes=self.get_bytes(address, length)).value

    def set_bytes(self, byte_array: bytearray, address: int, length: Optional[int] = None) -> None:
        base_address, start, end = self._get_data(address, length)
        for index, byte in enumerate(byte_array[: end - start]):
            self.frames[base_address][index + start] = byte
            self._frame[base_address][index + start] = byte

    def set_byte(self, byte: int, address: int) -> None:
        base_address, dsp, _ = self._get_data(address)
        self.frames[base_address][dsp] = byte
        self._frame[base_address][dsp] = byte

    def set_value(self, value: int, address: int, length: int = 4):
        base_address, start, end = self._get_data(address, length)
        for index, byte in enumerate(DataType('F', input=str(value)).to_bytes(end - start)):
            self.frames[base_address][index + start] = byte
            self._frame[base_address][index + start] = byte

    def is_updated(self, address: int, length: Optional[int] = None) -> bool:
        # Will return True only if all requested bytes are updated
        base_address, start, end = self._get_data(address, length)
        return self.frames[base_address][start: end] == self._frame[base_address][start: end]

    def all_bits_on(self, address: int, bits: int) -> bool:
        # Will return True only if all requested bits are ON
        base_address, dsp, _ = self._get_data(address)
        return self.frames[base_address][dsp] & bits == bits

    def all_bits_off(self, address: int, bits: int) -> bool:
        # Will return True only if all requested bits are OFF
        base_address, dsp, _ = self._get_data(address)
        return self.frames[base_address][dsp] & bits == 0

    def or_bit(self, address: int, bit: int) -> None:
        base_address, dsp, _ = self._get_data(address)
        self.frames[base_address][dsp] |= bit
        self._frame[base_address][dsp] |= bit

    def and_bit(self, address: int, bit: int) -> None:
        base_address, dsp, _ = self._get_data(address)
        self.frames[base_address][dsp] = self.frames[base_address][dsp] & bit
        self._frame[base_address][dsp] = self._frame[base_address][dsp] & bit

    def is_updated_bit(self, address: int, bit: int) -> bool:
        # Will return True only if all requested bits are updated
        base_address, dsp, _ = self._get_data(address)
        return self.frames[base_address][dsp] & bit == self._frame[base_address][dsp] & bit

    def init(self, address: int) -> None:
        base_address = self.base_key(address)
        try:
            self.frames[base_address] = bytearray()
            self._frame[base_address] = bytearray()
        except KeyError:
            raise KeyError

    def valid_address(self, address: int) -> int:
        return address if self.base_key(address) in self.frames else self.allocate()
