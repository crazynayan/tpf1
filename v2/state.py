from v2.data_type import DataType


class Registers:
    ORDER = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15']
    LEN = 4

    def __init__(self):
        self.R0 = bytearray([0x00] * self.LEN)
        self.R1 = bytearray([0x00] * self.LEN)
        self.R2 = bytearray([0x00] * self.LEN)
        self.R3 = bytearray([0x00] * self.LEN)
        self.R4 = bytearray([0x00] * self.LEN)
        self.R5 = bytearray([0x00] * self.LEN)
        self.R6 = bytearray([0x00] * self.LEN)
        self.R7 = bytearray([0x00] * self.LEN)
        self.R8 = bytearray([0x00] * self.LEN)
        self.R9 = bytearray([0x00] * self.LEN)
        self.R10 = bytearray([0x00] * self.LEN)
        self.R11 = bytearray([0x00] * self.LEN)
        self.R12 = bytearray([0x00] * self.LEN)
        self.R13 = bytearray([0x00] * self.LEN)
        self.R14 = bytearray([0x00] * self.LEN)
        self.R15 = bytearray([0x00] * self.LEN)

    def get_bytes(self, reg):
        try:
            return getattr(self, reg)
        except AttributeError:
            raise AttributeError

    def get_value(self, reg):
        return DataType('F', bytes=self.get_bytes(reg)).value

    def get_address(self, base, dsp, index=None):
        try:
            return (self.get_value(base.reg) if base.reg != 'R0' else 0) + dsp + \
                   (self.get_value(index.reg) if index and index.reg != 'R0' else 0)
        except AttributeError:
            raise AttributeError

    def next_reg(self, reg):
        self.get_bytes(reg)
        return self.ORDER[0] if reg == self.ORDER[-1] else self.ORDER[self.ORDER.index(reg) + 1]

    def get_bytes_from_mask(self, reg, mask):
        reg_bytes = self.get_bytes(reg)
        try:
            return bytearray([reg_bytes[index] for index, bit in enumerate(bin(mask)[2:]) if bit == '1'])
        except IndexError:
            raise IndexError

    def set_bytes(self, byte_array, reg):
        self.get_bytes(reg)
        if len(byte_array) != self.LEN:
            raise ValueError
        setattr(self, reg, byte_array[:])

    def set_value(self, value, reg):
        self.get_bytes(reg)
        setattr(self, reg, DataType('F', input=str(value)).to_bytes())

    def set_bytes_from_mask(self,  byte_array, reg, mask):
        reg_bytes = self.get_bytes(reg)
        if len(byte_array) < bin(mask).count('1'):
            raise ValueError
        try:
            reg_bytes = [byte_array.pop(0) if bit == '1' else reg_bytes[index]
                         for index, bit in enumerate(bin(mask)[2:])]
        except IndexError:
            raise IndexError
        setattr(self, reg, bytearray(reg_bytes))


class Storage:
    F4K = 4096
    ECB = F4K * 1
    GLOBAL = F4K * 2
    # Space for 14 more fixed frames
    NIBBLE = 4
    NIBBLE_3 = 12

    def __init__(self):
        self.frames = dict()
        self.frames[self.base_key(self.ECB)] = bytearray([0x00] * self.F4K)
        self.frames[self.base_key(self.GLOBAL)] = bytearray([0x00] * self.F4K)
        self.nab = self.F4K << self.NIBBLE

    def allocate(self):
        self.frames[self.base_key(self.nab)] = bytearray()
        self.nab += self.F4K

    def base_key(self, address):
        address = (address >> self.NIBBLE_3) << self.NIBBLE_3
        return f"{address:08x}"

    def dsp(self, address):
        return address & (self.F4K - 1)

    def _get_data(self, address, length=None):
        base_address = self.base_key(address)
        try:
            data = self.frames[base_address]
        except KeyError:
            raise KeyError
        start = self.dsp(address)
        end = start + 1 if length is None else start + length
        if end > len(data):
            data.extend(bytearray([0x00] * (end - len(data))))
        return base_address, start, end

    def get_bytes(self, address, length=None):
        base_address, start, end = self._get_data(address, length)
        return self.frames[base_address][start: end]

    def get_value(self, address, length=None):
        return DataType('X', bytes=self.get_bytes(address, length)).value

    def set_bytes(self, byte_array, address, length=None):
        base_address, start, end = self._get_data(address, length)
        for index, byte in enumerate(byte_array[: end - start]):
            self.frames[base_address][index + start] = byte
