from typing import Union, Optional, Tuple, Dict, List

from config import config
from v2.data_type import DataType, Register
from v2.segment import Program, Segment


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
        self.nab: int = config.F4K << config.NIBBLE                  # To ensure total 16 fixed frames
        self.frames[self.base_key(config.ECB)] = bytearray([config.ZERO] * config.F4K)
        self.frames[self.base_key(config.GLOBAL)] = bytearray([config.ZERO] * config.GLOBAL_FRAME_SIZE)
        self._frame[self.base_key(config.ECB)] = bytearray([config.ONES] * config.F4K)
        self._frame[self.base_key(config.GLOBAL)] = bytearray([config.ONES] * config.GLOBAL_FRAME_SIZE)

    def __repr__(self) -> str:
        return f"Storage:{len(self.frames)}"

    def allocate(self) -> int:
        base_address = self.base_key(self.nab)
        self.frames[base_address] = bytearray()
        self._frame[base_address] = bytearray()
        self.nab += config.F4K
        return self.nab - config.F4K

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


class State:
    def __init__(self, global_program: Program):
        self.global_program: Program = global_program
        self.seg: Optional[Segment] = None
        self.regs: Registers = Registers()
        self.vm: Storage = Storage()
        self.detac_stack: Dict[str, List] = {level: list() for level in config.ECB_LEVELS}
        self.message: Optional[str] = None
        self.dumps: List[str] = list()
        self.heap: Dict[str, int] = dict()
        self.call_stack: List[str] = list()
        self.loaded_seg: Dict[str, Tuple[Segment, int]] = dict()

    def __repr__(self) -> str:
        return f"State:{self.seg}:{self.regs}:{self.vm}"

    def init_seg(self, seg_name: str) -> None:
        if seg_name in self.loaded_seg:
            self.regs.R8 = self.loaded_seg[seg_name][1]
            self.seg = self.loaded_seg[seg_name][0]
        else:
            self.global_program.load(seg_name)
            self.regs.R8 = self.vm.allocate()   # Constant
            literal = self.vm.allocate()        # Literal is immediately the next frame
            self.seg = self.global_program.segments[seg_name]
            self.vm.set_bytes(self.seg.data.constant, self.regs.R8, len(self.seg.data.constant))
            self.vm.set_bytes(self.seg.data.literal, literal, len(self.seg.data.literal))
            self.loaded_seg[seg_name] = (self.seg, self.regs.R8)

    def validate(self, address: int) -> int:
        return address if address else self.vm.allocate()

    def get_ecb_address(self, level: str, ecb_label: str) -> int:
        # level is from D0 to DF, ecb_label is the partial label to which the level number (0-F) to be appended
        if not level.startswith('D') or len(level) != 2 or level[1] not in config.ECB_LEVELS:
            # For DECB=(R1) DECB=L1ADR
            raise TypeError
        level = f"{ecb_label}{level[1]}"
        dsp = self.global_program.macros['EB0EB'].symbol_table[level].dsp
        return config.ECB + dsp
