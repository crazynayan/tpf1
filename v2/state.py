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

    def get_value(self, reg):
        return int.from_bytes(getattr(self, reg), 'big', signed=True)

    def set_value(self, reg, value):
        getattr(self, reg)
        setattr(self, reg, bytearray(value.to_bytes(4, 'big', signed=True)))

    def next_reg(self, reg):
        getattr(self, reg)
        return self.ORDER[0] if reg == self.ORDER[-1] else self.ORDER[self.ORDER.index(reg) + 1]

    def get_bytes(self, reg):
        return getattr(self, reg)

    def get_bytes_from_mask(self, reg, mask):
        reg_bytes = getattr(self, reg)
        return bytearray([reg_bytes[index] for index, bit in enumerate(bin(mask)[2:]) if bit == '1'])

    def set_bytes(self, reg, byte_array):
        getattr(self, reg)
        setattr(self, reg, byte_array[:self.LEN])

    def set_bytes_from_mask(self, reg, byte_array, mask):
        reg_bytes = getattr(self, reg)
        reg_bytes = [byte_array.pop(0) if bit == '1' else reg_bytes[index] for index, bit in enumerate(bin(mask)[2:])]
        setattr(self, reg, bytearray(reg_bytes))
