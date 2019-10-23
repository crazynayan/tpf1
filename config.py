import os
from datetime import datetime
from typing import Dict


class _Config:
    GAC_KEY_PATH = 'tpf1-key.json'
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    F4K = 4096
    ECB = F4K * 1
    GLOBAL = F4K * 2
    AAA = F4K * 3
    IMG = F4K * 4  # 12 more fixed frames are spare
    NIBBLE = 4
    DSP_SHIFT = 12
    ZERO = 0x00
    ONES = 0xFF
    ECB_LEVELS = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F')
    AAAPNR = 'AAAAAA'
    START = datetime(1966, 1, 2, 0, 0, 0)
    PARTITION: Dict[str, int] = {'AA': 0x00, 'BA': 0xE0}
    DEFAULT_INSTRUCTION_LENGTH = 4
    BLOCK_SIZE = {'L0': 128, 'L1': 381, 'L2': 1055, 'L4': 4095}
    BLOCK_TYPE = {'L0': 0x11, 'L1': 0x21, 'L2': 0x31, 'L4': 0x41}
    GROSS_DAYS = 333


config = _Config()
