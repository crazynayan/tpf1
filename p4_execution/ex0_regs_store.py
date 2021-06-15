from datetime import datetime
from typing import Union, Optional, Tuple, Dict

from config import config
from p1_utils.data_type import DataType, Register
from p1_utils.errors import RegisterInvalidError, BaseAddressError, MaskError
from p2_assembly.mac2_data_macro import macros


class Registers:

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
        return f"R0:{self.R0 & config.REG_MAX:08X}," \
               f"R1:{self.R1 & config.REG_MAX:08X}," \
               f"R2:{self.R2 & config.REG_MAX:08X}," \
               f"R3:{self.R3 & config.REG_MAX:08X}," \
               f"R5:{self.R5 & config.REG_MAX:08X}," \
               f"R6:{self.R6 & config.REG_MAX:08X}," \
               f"R7:{self.R7 & config.REG_MAX:08X}," \
               f"R14:{self.R14 & config.REG_MAX:08X}," \
               f"R15:{self.R15 & config.REG_MAX:08X},"

    def get_bytes(self, reg: Union[str, Register]) -> bytearray:
        return DataType('F', input=str(self.get_value(reg))).to_bytes(config.REG_BYTES)

    def get_value(self, reg: Union[str, Register]) -> int:
        try:
            return getattr(self, str(reg))
        except AttributeError:
            raise RegisterInvalidError

    def get_unsigned_value(self, reg: Union[str, Register]) -> int:
        return self.get_value(reg) & config.REG_MAX

    def get_address(self, base: Optional[Register], dsp: int = 0, index: Optional[Register] = None) -> int:
        return (self.get_unsigned_value(base) if base and str(base) != 'R0' else 0) + dsp + \
               (self.get_unsigned_value(index) if index and str(index) != 'R0' else 0)

    def next_reg(self, reg: Union[str, Register]) -> str:
        self.get_value(reg)
        return config.REGISTERS[0] if reg == config.REGISTERS[-1] \
            else config.REGISTERS[config.REGISTERS.index(str(reg)) + 1]

    def get_bytes_from_mask(self, reg: Register, mask: int) -> bytearray:
        reg_bytes = self.get_bytes(reg)
        try:
            return bytearray([reg_bytes[index] for index, bit in enumerate(f'{mask:04b}') if bit == '1'])
        except IndexError:
            raise MaskError

    def set_value(self, value: int, reg: Union[Register, str]) -> None:
        self.get_value(reg)
        if value < -config.REG_NEG or value > config.REG_MAX:
            value &= config.REG_MAX
        if value > 0 and value & config.REG_NEG != 0:
            value -= config.REG_MAX + 1
        setattr(self, str(reg), value)

    def set_bytes_from_mask(self,  byte_array: bytearray, reg: Register, mask: int) -> None:
        reg_bytes = self.get_bytes(reg)
        if len(byte_array) < bin(mask).count('1'):
            raise MaskError
        try:
            reg_bytes = [byte_array.pop(0) if bit == '1' else reg_bytes[index]
                         for index, bit in enumerate(f'{mask:04b}')]
        except IndexError:
            raise MaskError
        setattr(self, str(reg), DataType('F', bytes=bytearray(reg_bytes)).value)

    def get_double_value(self, reg: Register) -> int:
        high_value = self.get_value(reg)
        low_value = self.get_unsigned_value(self.next_reg(reg))
        high_value <<= config.REG_BITS
        return high_value + low_value

    def get_unsigned_double_value(self, reg: Register) -> int:
        high_value = self.get_unsigned_value(reg)
        low_value = self.get_unsigned_value(self.next_reg(reg))
        high_value <<= config.REG_BITS
        return high_value + low_value

    def set_double_value(self, value: int, reg: Register) -> None:
        high_value = value >> config.REG_BITS
        self.set_value(high_value, reg)
        self.set_value(value, self.next_reg(reg))


class Storage:
    def __init__(self):
        self.frames: Dict[str, bytearray] = dict()                 # Frames init with ZERO
        self._frame: Dict[str, bytearray] = dict()                 # Frames init with ONES
        self.nab: int = config.F4K << config.NIBBLE  # To ensure total 16 fixed frames
        self.allocate_fixed(config.ECB)
        self.allocate_fixed(config.GLOBAL)
        self.allocate_fixed(config.AAA)
        self.allocate_fixed(config.IMG)
        self.allocate_fixed(config.MULTI_HOST)
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
        now = datetime.now()
        today = datetime(year=now.year, month=now.month, day=now.day)
        pars_today = (today - config.PARS_DAY_1).days
        self.set_value(pars_today, u1dmo, 2)
        tjord = config.GLOBAL + macros['GLOBAL'].evaluate('@TJORD')
        self.set_value(0x00088EDC, tjord)
        multi_host = config.GLOBAL + macros['GLOBAL'].evaluate('@MHSTC')
        self.set_value(config.MULTI_HOST, multi_host)
        u1tym = config.GLOBAL + macros['GLOBAL'].evaluate('@U1TYM')
        time: str = f"{now.hour:02}{now.minute:02}"
        time_bytes: bytearray = DataType("C", input=time).to_bytes()
        self.set_bytes(time_bytes, u1tym)

    def get_allocated_address(self) -> bytearray:
        return DataType('F', input=str(self.nab - config.F4K)).to_bytes(config.REG_BYTES)

    @staticmethod
    def base_key(address: int) -> str:
        address &= config.REG_MAX
        address = (address >> config.DSP_SHIFT) << config.DSP_SHIFT
        return f"{address:08X}"

    @staticmethod
    def dsp(address: int) -> int:
        return address & (config.F4K - 1)

    def extend_frame(self, base_address: str, length: int) -> None:
        try:
            frame_len = len(self.frames[base_address])
        except KeyError:
            raise BaseAddressError
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

    def set_frame(self, byte_array: bytearray, address: int):
        base_address = self.base_key(address)
        self.frames[base_address] = byte_array
        self._frame[base_address] = byte_array

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
            raise BaseAddressError

    def valid_address(self, address: int) -> int:
        return address if self.base_key(address) in self.frames else self.allocate()
