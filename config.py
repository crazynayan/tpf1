import os
from base64 import b64encode
from datetime import datetime
from typing import Dict, List, Set


class Config:
    # Used by flask_app.auth
    DEFAULT_PASSWORD = b64encode(os.urandom(24)).decode()
    DEFAULT_TOKEN = b64encode(os.urandom(24)).decode()

    # Used by flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or b64encode(os.urandom(24)).decode()

    # Used by utils
    REG_INVALID: str = '??'
    REG: Dict[str, List[str]] = {
        'R0': ['0', '00', 'R0', 'R00', 'RAC'], 'R1': ['1', '01', 'R1', 'R01', 'RG1'],
        'R2': ['2', '02', 'R2', 'R02', 'RGA'], 'R3': ['3', '03', 'R3', 'R03', 'RGB'],
        'R4': ['4', '04', 'R4', 'R04', 'RGC'], 'R5': ['5', '05', 'R5', 'R05', 'RGD'],
        'R6': ['6', '06', 'R6', 'R06', 'RGE'], 'R7': ['7', '07', 'R7', 'R07', 'RGF'],
        'R8': ['8', '08', 'R8', 'R08', 'RAP'], 'R9': ['9', '09', 'R9', 'R09', 'REB'],
        'R10': ['10', 'R10', 'RLA'], 'R11': ['11', 'R11', 'RLB'],
        'R12': ['12', 'R12', 'RLC'], 'R13': ['13', 'R13', 'RLD'],
        'R14': ['14', 'R14', 'RDA'], 'R15': ['15', 'R15', 'RDB'],
    }
    CHAR_PADDING: int = 0x40
    NUMBER_PADDING: int = 0xF0
    CVS_C2: Set[str] = {'Ch', 'RC', 'VE', '==', '**', 'ng', '/u', '1.'}
    TRIM: Dict[str, int] = {'0': 7, ' ': 1}
    COMMENT_C1: Set[str] = {'*', '.'}
    DIRECTIVE: Set[str] = {'PUSH', 'USING', 'DSECT', 'PGMID', 'LTORG', 'FINIS', 'END', 'ORG', 'POP', 'CSECT',
                           'EQU', 'DS', 'DC', 'EJECT', 'SPACE', 'PRINT', 'BEGIN', 'DROP'}
    DIRECTIVE_SECOND_PASS: tuple = ('PUSH', 'USING', 'POP', 'DROP')
    DIRECTIVE_NODE: Set[str] = {'EQU', 'DS'}
    INSTRUCTION_LEN_DEFAULT: int = 4
    INSTRUCTION_LEN_2: Set[str] = {'BCTR', 'BR', 'LR', 'LTR', 'AR', 'SR', 'BER', 'BNER', 'BHR', 'BNHR', 'BLR', 'BNLR',
                                   'BMR', 'BNMR', 'BPR', 'BNPR', 'BCR', 'BOR', 'BNOR', 'BZR', 'BNZR', 'NOPR', 'LPR',
                                   'LNR', 'LCR', 'MR', 'DR', 'MVCL', 'BASR', 'CR', 'CLR', 'CLCL', 'ALR', 'SLR', 'NR',
                                   'OR', 'XR'}
    INSTRUCTION_LEN_6: Set[str] = {'OC', 'CLC', 'XC', 'UNPK', 'PACK', 'MVC', 'MVZ', 'MVN', 'MVO', 'NC', 'ZAP', 'AP',
                                   'SP', 'MP', 'DP', 'CP', 'TP', 'SRP', 'TR', 'TRT', 'ED', 'EDMK'}
    SW00SR: Set[str] = {'DBOPN', 'DBRED', 'DBCLS', 'DBIFB'}
    NO_FALL_DOWN: Set[str] = {'BR', 'ENTNC', 'B', 'J', 'SENDA', 'ENTDC', 'EXITC', 'BACKC'}

    # Used by assembly
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    MASK: Dict[str, int] = {'BR': 15, 'B': 15, 'J': 15, 'BAS': 15, 'JAS': 15, 'BE': 8, 'BNE': 7, 'BH': 2, 'BNH': 13,
                            'BL': 4, 'BNL': 11, 'BM': 4, 'BNM': 11, 'BP': 2, 'BNP': 13, 'BCRY': 3, 'BO': 1, 'BNO': 14,
                            'BZ': 8, 'BNZ': 7, 'JE': 8, 'JNE': 7, 'JH': 2, 'JNH': 13, 'JL': 4, 'JNL': 11, 'JM': 4,
                            'JNM': 11, 'JP': 2, 'JNP': 13, 'JO': 1, 'JNO': 14, 'JZ': 8, 'JNZ': 7, 'NOP': 0, 'JNOP': 0,
                            'BER': 8, 'BNER': 7, 'BHR': 2, 'BNHR': 13, 'BLR': 4, 'BNLR': 11, 'BMR': 4, 'BNMR': 11,
                            'BPR': 2, 'BNPR': 13, 'BOR': 1, 'BNOR': 14, 'BZR': 8, 'BNZR': 7, 'NOPR': 0}

    # Used by execution
    REGISTERS: tuple = ('R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14',
                        'R15')
    REG_BITS: int = 32
    REG_BYTES: int = REG_BITS // 8
    REG_MAX: int = (1 << REG_BITS) - 1  # 0xFFFFFFFF
    REG_NEG: int = 1 << REG_BITS - 1  # 0x80000000
    NIBBLE: int = 4
    DSP_SHIFT: int = 12
    ZERO: int = 0x00
    ONES: int = 0xFF
    F4K: int = 1 << DSP_SHIFT
    ECB: int = F4K * 1
    GLOBAL: int = F4K * 2
    AAA: int = F4K * 3
    IMG: int = F4K * 4  # 12 more fixed frames are spare
    ECB_LEVELS: tuple = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F')
    BLOCK_SIZE: Dict[str, int] = {'L0': 128, 'L1': 381, 'L2': 1055, 'L4': 4095}
    BLOCK_TYPE: Dict[str, int] = {'L0': 0x11, 'L1': 0x21, 'L2': 0x31, 'L4': 0x41}
    START: datetime = datetime(1966, 1, 2, 0, 0, 0)
    GROSS_DAYS: int = 333
    PARTITION: Dict[str, int] = {'AA': 0x00, 'BA': 0xE0}

    # Used by db
    AAAPNR: str = 'AAAAAA'

    # Used by test_data model and execution
    COPY_SUFFIX: str = ' - Copy'
    DEFAULT_MACROS: dict = {'EB0EB': ECB, 'GLOBAL': GLOBAL, 'WA0AA': AAA, 'MI0MI': IMG}


config = Config()
