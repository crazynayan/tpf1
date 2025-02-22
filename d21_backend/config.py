import os
from base64 import b64encode
from datetime import datetime
from types import SimpleNamespace
from typing import Dict, List, Set


class Config:
    # Used by test_refactor_api
    TEST_TOKEN = str()

    # Used by api
    DEFAULT_VARIATION_NAME = "Default"

    # Used by flask_app.auth
    DEFAULT_PASSWORD = b64encode(os.urandom(24)).decode()
    DEFAULT_TOKEN = b64encode(os.urandom(24)).decode()
    ADMIN, MEMBER = "admin", "member"
    ROLES = [ADMIN, MEMBER]

    # Used by flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or b64encode(os.urandom(24)).decode()

    # Used by segment
    CI_CLOUD_STORAGE = os.environ.get("CI_CLOUD_STORAGE") == "use"
    ASM, LST, LXP, LOCAL, CLOUD = "asm", "lst", "lxp", "local", "cloud"
    DOWNLOAD_PATH = os.path.join(os.path.abspath(os.sep), "tmp")
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    BUCKETS = SimpleNamespace()
    BUCKETS.GENERAL = "tpf-general"
    BUCKETS.TIGER = "tpf-listings"
    BUCKETS.SML = "tpf-sml"
    DOMAINS = SimpleNamespace()
    DOMAINS.GENERAL = "general"
    DOMAINS.BASE = "base"
    DOMAINS.TIGER = "tiger"
    DOMAINS.SML = "sml"
    DOMAINS.CMFIRST = "cmfirst"
    DOMAIN = os.environ.get("DOMAIN") or DOMAINS.GENERAL
    MAC_FOLDER = "macro"
    # SOURCES_ROOT = os.path.join(os.path.abspath(os.path.dirname("d21_backend")), "d20_source")
    SOURCES_ROOT = "d20_source"

    ASM_EXT = {".asm", ".txt"}
    LXP_EXT = {".lxp"}
    MAC_EXT = {".mac", ".txt"}

    # Used by utils
    REG_INVALID: str = "??"
    REG: Dict[str, List[str]] = {
        "R0": ["0", "00", "R0", "R00", "RAC"], "R1": ["1", "01", "R1", "R01", "RG1"],
        "R2": ["2", "02", "R2", "R02", "RGA", "RG2"], "R3": ["3", "03", "R3", "R03", "RGB", "RG3"],
        "R4": ["4", "04", "R4", "R04", "RGC", "RG4"], "R5": ["5", "05", "R5", "R05", "RGD", "RG5"],
        "R6": ["6", "06", "R6", "R06", "RGE", "RG6"], "R7": ["7", "07", "R7", "R07", "RGF", "RG7"],
        "R8": ["8", "08", "R8", "R08", "RAP","RG8"], "R9": ["9", "09", "R9", "R09", "REB", "RG9"],
        "R10": ["10", "R10", "RLA"], "R11": ["11", "R11", "RLB"],
        "R12": ["12", "R12", "RLC"], "R13": ["13", "R13", "RLD"],
        "R14": ["14", "R14", "RDA"], "R15": ["15", "R15", "RDB"],
    }
    CHAR_PADDING: int = 0x40
    NUMBER_PADDING: int = 0xF0
    CVS_C2: Set[str] = {"Ch", "RC", "VE", "==", "**"}  # , "ng", "/u", "1."}
    TRIM: Dict[str, int] = {"0": 7, " ": 1}
    COMMENT_C1: Set[str] = {"*", "."}
    DIRECTIVE: Set[str] = {"PUSH", "USING", "DSECT", "PGMID", "LTORG", "FINIS", "END", "ORG", "POP", "CSECT",
                           "EQU", "DS", "DC", "EJECT", "SPACE", "PRINT", "BEGIN", "DROP", "DATAS"}
    DIRECTIVE_SECOND_PASS: Set[str] = {"PUSH", "USING", "POP", "DROP", "DATAS"}
    DIRECTIVE_NODE: Set[str] = {"EQU", "DS"}
    DIRECTIVE_IGNORE_LABEL: Set[str] = DIRECTIVE - DIRECTIVE_NODE - {"DC"}
    INSTRUCTION_LEN_DEFAULT: int = 4
    INSTRUCTION_LEN_2: Set[str] = {"BCTR", "BR", "LR", "LTR", "AR", "SR", "BER", "BNER", "BHR", "BNHR", "BLR", "BNLR",
                                   "BMR", "BNMR", "BPR", "BNPR", "BCR", "BOR", "BNOR", "BZR", "BNZR", "NOPR", "LPR",
                                   "LNR", "LCR", "MR", "DR", "MVCL", "BASR", "CR", "CLR", "CLCL", "ALR", "SLR", "NR",
                                   "OR", "XR"}
    INSTRUCTION_LEN_6: Set[str] = {"OC", "CLC", "XC", "UNPK", "PACK", "MVC", "MVZ", "MVN", "MVO", "NC", "ZAP", "AP",
                                   "SP", "MP", "DP", "CP", "TP", "SRP", "TR", "TRT", "ED", "EDMK"}
    SW00SR: Set[str] = {"DBOPN", "DBRED", "DBCLS", "DBIFB"}
    NO_FALL_DOWN: Set[str] = {"BR", "ENTNC", "B", "J", "SENDA", "ENTDC", "EXITC", "BACKC"}
    CALL_AND_RETURN: Set[str] = {"ENTRC", "BAS", "BAL", "JAS", "BRAS"}

    # Used by assembly
    MASK: Dict[str, int] = {"BR": 15, "B": 15, "J": 15, "BAS": 15, "JAS": 15, "BE": 8, "BNE": 7, "BH": 2, "BNH": 13,
                            "BL": 4, "BNL": 11, "BM": 4, "BNM": 11, "BP": 2, "BNP": 13, "BCRY": 3, "BO": 1, "BNO": 14,
                            "BZ": 8, "BNZ": 7, "JE": 8, "JNE": 7, "JH": 2, "JNH": 13, "JL": 4, "JNL": 11, "JM": 4,
                            "JNM": 11, "JP": 2, "JNP": 13, "JO": 1, "JNO": 14, "JZ": 8, "JNZ": 7, "NOP": 0, "JNOP": 0,
                            "BER": 8, "BNER": 7, "BHR": 2, "BNHR": 13, "BLR": 4, "BNLR": 11, "BMR": 4, "BNMR": 11,
                            "BPR": 2, "BNPR": 13, "BOR": 1, "BNOR": 14, "BZR": 8, "BNZR": 7, "NOPR": 0}

    # Used by execution
    REGISTERS: tuple = ("R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14",
                        "R15")
    REGISTERS_EVEN: tuple = ("R0", "R2", "R4", "R6", "R8", "R10", "R12", "R14")
    REG_BITS: int = 32
    REG_BYTES: int = REG_BITS // 8
    REG_MAX: int = (1 << REG_BITS) - 1  # 0xFFFFFFFF
    REG_NEG: int = 1 << REG_BITS - 1  # 0x80000000
    REG_BITS64: int = 64
    REG_MAX64: int = (1 << REG_BITS) - 1  # 0xFFFFFFFFFFFFFFFF
    REG_NEG64: int = 1 << REG_BITS - 1  # 0x8000000000000000
    NIBBLE: int = 4
    DSP_SHIFT: int = 12
    ZERO: int = 0x00
    ONES: int = 0xFF
    F4K: int = 1 << DSP_SHIFT
    ECB: int = F4K * 1
    GL0BS: int = F4K * 2
    IMG: int = F4K * 3
    MULTI_HOST: int = F4K * 4
    GLOBAS: int = F4K * 5
    GLOBYS: int = F4K * 6  # 10 more frames are spare
    ECB_LEVELS: tuple = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F")
    BLOCK_SIZE: Dict[str, int] = {"L0": 128, "L1": 381, "L2": 1055, "L4": 4095}
    BLOCK_TYPE: Dict[str, int] = {"L0": 0x11, "L1": 0x21, "L2": 0x31, "L4": 0x41}
    PARS_DAY_1: datetime = datetime(1966, 1, 2, 0, 0, 0)
    GROSS_DAYS: int = 333
    PARTITION: Dict[str, int] = {"AA": 0x00, "KM": 0x01, "WS": 0x02, "AS": 0x04, "GF": 0x05, "ET": 0x06, "UP": 0x09,
                                 "W1": 0x0B, "AR": 0x0C, "SL": 0x0E, "HA": 0x0F, "ID": 0x10, "7N": 0x11, "6S": 0x14,
                                 "K0": 0x16, "9W": 0x18, "AM": 0x19, "KX": 0x1A, "WY": 0x1B, "B2": 0x1C, "JJ": 0x1E,
                                 "CO": 0x1F, "JT": 0x22, "JU": 0x23, "AZ": 0x24, "YF": 0x25, "7H": 0x26, "ZL": 0x29,
                                 "B6": 0x2A, "R7": 0x2C, "FC": 0x2D, "7F": 0x2F, "5T": 0x30, "PX": 0x31, "K6": 0x32,
                                 "F7": 0x33, "I0": 0x36, "VN": 0x37, "KS": 0x3A, "AX": 0x3F, "T3": 0x41, "VX": 0x44,
                                 "VA": 0x45, "S2": 0x46, "SU": 0x48, "MN": 0x49, "IW": 0x4A, "EY": 0x4B, "9V": 0x4C,
                                 "8U": 0x4D, "3M": 0x4E, "F0": 0x50, "XH": 0x51, "HM": 0x55, "XL": 0x59, "LA": 0x5A,
                                 "4M": 0x5B}

    # Used by db
    AAAPNR: str = "AAAAAA"

    # Used by test_data model and execution
    AAA_MACRO_NAME: str = "WA0AA"
    COPY_SUFFIX: str = " - Copy"
    FIXED_MACROS: dict = {"EB0EB": ECB, "GL0BS": GL0BS, AAA_MACRO_NAME: 0, "MI0MI": IMG, "MH0HM": MULTI_HOST,
                          "GLOBAS": GLOBAS, "GLOBYS": GLOBYS}

    # Used by test
    TEST_DEBUG: bool = False
    # Used by ETA5 test
    ET_DEBUG_DATA: Dict[str, set] = dict()
    ET_DEBUG_DATA_MISSED: Dict[str, set] = dict()
    ET_CLASS_COUNTER: int = 0
    ET_TEST_CLASS_COUNT: int = 22
    # Change 4CC1 to 4E2F to 4F9C to 5109 to 5276 to 53E4 to 5551 to 56BE to 582B
    #        20Oct19 20Oct20 20Oct21 20Oct22 20Oct23 20Oct24 20Oct25 20Oct26 20Oct27 (every year after 20NOV)
    PARS_DATE: str = "53E4"


config = Config()
