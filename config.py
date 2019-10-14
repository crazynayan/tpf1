import os
from datetime import datetime


class _Config:
    GAC_KEY_PATH = 'tpf1-key.json'
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    F4K = 4096
    ECB = F4K * 1
    GLOBAL = F4K * 2    # 14 more fixed frames are spare
    NIBBLE = 4
    DSP_SHIFT = 12
    ZERO = 0x00
    ONES = 0xFF
    ECB_LEVELS = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F')
    AAAPNR = 'AAAAAA'
    START = datetime(1966, 1, 2)


config = _Config()
