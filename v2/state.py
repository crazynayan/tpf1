from v2.data_type import DataType


class Registers:
    ORDER = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15']
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

    def __repr__(self):
        return f"R0:{self.R0 & self.L:08x},R1:{self.R1 & self.L:08x},R2:{self.R2 & self.L:08x}," \
               f"R3:{self.R3 & self.L:08x},R4:{self.R4 & self.L:08x},R5:{self.R5 & self.L:08x},"

    def get_bytes(self, reg):
        return DataType('F', input=str(self.get_value(reg))).to_bytes(self.LEN)

    def get_value(self, reg):
        try:
            return getattr(self, str(reg))
        except AttributeError:
            raise AttributeError

    def get_address(self, base, dsp, index=None):
        return (self.get_value(str(base)) if str(base) != 'R0' else 0) + dsp + \
               (self.get_value(str(index)) if index and str(index) != 'R0' else 0)

    def next_reg(self, reg):
        self.get_value(reg)
        return self.ORDER[0] if reg == self.ORDER[-1] else self.ORDER[self.ORDER.index(reg) + 1]

    def get_bytes_from_mask(self, reg, mask):
        reg_bytes = self.get_bytes(reg)
        try:
            return bytearray([reg_bytes[index] for index, bit in enumerate(f'{mask:04b}') if bit == '1'])
        except IndexError:
            raise IndexError

    def set_bytes(self, byte_array, reg):
        self.get_value(reg)
        if len(byte_array) != self.LEN:
            raise ValueError
        setattr(self, str(reg), DataType('F', bytes=byte_array).value)

    def set_value(self, value, reg):
        self.get_value(reg)
        setattr(self, str(reg), value)

    def set_bytes_from_mask(self,  byte_array, reg, mask):
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
    F4K = 0x00001000
    ECB = F4K * 1
    GLOBAL = F4K * 2     # 14 more fixed frames are spare
    GLOBAL_FRAME_SIZE = 1 << 4
    NIBBLE = 4
    NIBBLE_3 = 12
    ZERO = 0x00
    ONES = 0xFF

    def __init__(self):
        self.frames = dict()                # Frames init with ZERO
        self._frame = dict()               # Frames init with ONES
        self.nab = self.F4K << self.NIBBLE  # To ensure total 16 fixed frames
        self.frames[self.base_key(self.ECB)] = bytearray([self.ZERO] * self.F4K)
        self.frames[self.base_key(self.GLOBAL)] = bytearray([self.ZERO] * self.GLOBAL_FRAME_SIZE)
        self._frame[self.base_key(self.ECB)] = bytearray([self.ONES] * self.F4K)
        self._frame[self.base_key(self.GLOBAL)] = bytearray([self.ONES] * self.GLOBAL_FRAME_SIZE)

    def __repr__(self):
        return f"Storage:{len(self.frames)}"

    def allocate(self):
        base_address = self.base_key(self.nab)
        self.frames[base_address] = bytearray()
        self._frame[base_address] = bytearray()
        self.nab += self.F4K
        return self.nab - self.F4K

    def get_allocated_address(self):
        return DataType('F', input=str(self.nab - self.F4K)).to_bytes(Registers.LEN)

    def base_key(self, address):
        address = (address >> self.NIBBLE_3) << self.NIBBLE_3
        return f"{address:08x}"

    def dsp(self, address):
        return address & (self.F4K - 1)

    def extend_frame(self, base_address, length):
        try:
            frame_len = len(self.frames[base_address])
        except KeyError:
            raise KeyError
        if length > frame_len:
            self.frames[base_address].extend(bytearray([self.ZERO] * (length - frame_len)))
            self._frame[base_address].extend(bytearray([self.ONES] * (length - frame_len)))

    def _get_data(self, address, length=None):
        base_address = self.base_key(address)
        start = self.dsp(address)
        end = start + 1 if length is None else start + length
        self.extend_frame(base_address, end)
        return base_address, start, end

    def get_bytes(self, address, length=None):
        base_address, start, end = self._get_data(address, length)
        return self.frames[base_address][start: end]

    def get_value(self, address, length=4):
        return DataType('F', bytes=self.get_bytes(address, length)).value

    def set_bytes(self, byte_array, address, length=None):
        base_address, start, end = self._get_data(address, length)
        for index, byte in enumerate(byte_array[: end - start]):
            self.frames[base_address][index + start] = byte
            self._frame[base_address][index + start] = byte

    def set_value(self, value, address, length=4):
        base_address, start, end = self._get_data(address, length)
        for index, byte in enumerate(DataType('F', input=str(value)).to_bytes(end - start)):
            self.frames[base_address][index + start] = byte
            self._frame[base_address][index + start] = byte

    def is_updated(self, address, length=None):
        # Will return True only if all requested bytes are updated
        base_address, start, end = self._get_data(address, length)
        return self.frames[base_address][start: end] == self._frame[base_address][start: end]

    def all_bits_on(self, address, bits):
        # Will return True only if all requested bits are ON
        base_address, dsp, _ = self._get_data(address)
        return self.frames[base_address][dsp] & bits == bits

    def all_bits_off(self, address, bits):
        # Will return True only if all requested bits are OFF
        base_address, dsp, _ = self._get_data(address)
        return self.frames[base_address][dsp] & bits == 0

    def set_bit_on(self, address, bit):
        base_address, dsp, _ = self._get_data(address)
        self.frames[base_address][dsp] |= bit
        self._frame[base_address][dsp] |= bit

    def set_bit_off(self, address, bit):
        base_address, dsp, _ = self._get_data(address)
        self.frames[base_address][dsp] = self.frames[base_address][dsp] & ~bit
        self._frame[base_address][dsp] = self._frame[base_address][dsp] & ~bit

    def is_updated_bit(self, address, bit):
        # Will return True only if all requested bits are updated
        base_address, dsp, _ = self._get_data(address)
        return self.frames[base_address][dsp] & bit == self._frame[base_address][dsp] & bit


class State:
    def __init__(self, global_program, seg_name=None):
        self.global_program = global_program
        self.seg_name = seg_name                # The name of the current segment that is executing
        self.regs = Registers()
        self.vm = Storage()
        self.errors = list()

    def __repr__(self):
        return f"State:{self.seg_name}:{self.vm}"

    def init_seg(self, seg_name):
        self.global_program.load(seg_name)
        self.regs.R8 = self.vm.allocate()   # Constant TODO Improve re-usability of initializing the same seg twice
        literal = self.vm.allocate()        # Literal is immediately the next frame
        seg = self.global_program.segments[seg_name]
        self.vm.set_bytes(seg.data.constant, self.regs.R8, len(seg.data.constant))
        self.vm.set_bytes(seg.data.literal, literal, len(seg.data.literal))
        return seg

    def run(self):
        self.regs.R9 = Storage.ECB
        seg = self.init_seg(self.seg_name)
        label = seg.root_label
        while label:
            try:
                seg.nodes[label].execute(self)
            except AttributeError:
                self.errors.append(f"{seg.nodes[label]}")
            label = seg.nodes[label].fall_down

    def validate(self, address):
        return address if address else self.vm.allocate()
