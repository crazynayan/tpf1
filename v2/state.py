class Registers:
    def __init__(self):
        self.R0 = bytearray([0x00] * 4)
        self.R1 = bytearray([0x00] * 4)
        self.R2 = bytearray([0x00] * 4)
        self.R3 = bytearray([0x00] * 4)
        self.R4 = bytearray([0x00] * 4)
        self.R5 = bytearray([0x00] * 4)
        self.R6 = bytearray([0x00] * 4)
        self.R7 = bytearray([0x00] * 4)
        self.R8 = bytearray([0x00] * 4)
        self.R9 = bytearray([0x00] * 4)
        self.R10 = bytearray([0x00] * 4)
        self.R11 = bytearray([0x00] * 4)
        self.R12 = bytearray([0x00] * 4)
        self.R13 = bytearray([0x00] * 4)
        self.R14 = bytearray([0x00] * 4)
        self.R15 = bytearray([0x00] * 4)

    def get_value(self, reg):
        return int.from_bytes(getattr(self, reg), 'big', signed=True)

    def set_value(self, reg, value):
        getattr(self, reg)
        setattr(self, reg, bytearray(value.to_bytes(4, 'big', signed=True)))

