import os
from base64 import b64encode
from socket import gethostname, gethostbyname


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or b64encode(os.urandom(24)).decode()
    SERVER_URL = os.environ.get("SERVER_URL") or f"http://{gethostbyname(gethostname())}:8000"
    CI_SECURITY = True if os.environ.get("ENVIRONMENT") == "prod" else False
    DOWNLOAD_PATH = os.path.join(os.path.abspath(os.sep), "tmp")
    SESSION_COOKIE_SECURE = CI_SECURITY
    TOKEN_EXPIRY = 3600  # 1 hour = 3600 seconds
    REG_BITS: int = 32
    REG_MAX: int = (1 << REG_BITS) - 1  # 0xFFFFFFFF
    REGISTERS: tuple = ("R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14",
                        "R15")
    ECB_LEVELS: tuple = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F")
    DEFAULT_MACROS: tuple = ("WA0AA", "EB0EB", "MI0MI")
    AAAPNR: str = "AAAAAA"
    PNR_KEYS = [
        ("name", "NAME"),
        ("hfax", "HFAX"),
        ("gfax", "GFAX"),
        ("fqtv", "FQTV"),
        ("itin", "ITIN"),
        ("subs_card_seg", "SUBS_CARD_SEG"),
        ("group_plan", "GROUP_PLAN"),
        ("rcvd_from", "RCVD_FROM"),
        ("phone", "PHONE"),
        ("record_loc", "RECORD_LOC"),
        ("remarks", "REMARKS"),
        ("header", "HEADER"),
        ("prs_seats", "PRS_SEATS"),
        ("vcr_coupon", "VCR_COUPON"),
        ("ice_data", "ICE_DATA"),
    ]
