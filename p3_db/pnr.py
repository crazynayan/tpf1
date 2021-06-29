from typing import List, Dict, Union, Tuple, Optional

from config import config
from p1_utils.data_type import DataType
from p1_utils.errors import PnrElementError, PnrLocatorNotFoundError
from p2_assembly.mac2_data_macro import macros
from p3_db.stream import Stream

NAME, HFAX, FQTV, ITIN, RCVD_FROM, PHONE, REMARKS = "name", "hfax", "fqtv", "itin", "rcvd_from", "phone", "remarks"
SUBS_CARD_SEG, GROUP_PLAN, RECORD_LOC, PRS_SEATS = "subs_card_seg", "group_plan", "record_loc", "prs_seats"
HEADER, VCR_COUPON, ICE_DATA = "header", "vcr_coupon", "ice_data"


class PnrAttribute:

    def __init__(self, name: str, key: str, byte_array: bool = False, packed: bool = False, macro_name: str = None,
                 std_fix: bytearray = None, std_var: bytearray = None):
        self.name: str = name
        self.key: str = key
        self.byte_array: bool = byte_array
        self.packed: bool = packed
        self.macro_name: str = macro_name if macro_name else "PR001W"
        self.std_fix = std_fix if std_fix else bytearray()
        self.std_var = std_var if std_var else bytearray()


class PnrLrec:

    def __init__(self, key: str, data: bytearray = None):
        self.key: str = key
        self.data: bytearray = data if data else bytearray()

    def to_dict(self):
        return self.__dict__


class Pnr:
    DB: List[Dict[str, Union[str, List[Dict[str, bytearray]]]]] = [{"id": config.AAAPNR, "doc": list()}]
    STD_PREFIX_BYTES = bytearray([0x00] * 0x14)
    ATTRIBUTES = [
        PnrAttribute(NAME, "50", std_var=bytearray([0x00, 0x00, 0x02, 0x00])),
        PnrAttribute(HFAX, "84", std_fix=bytearray([0x00] * 0x08), std_var=bytearray([0x02, 0x01])),
        PnrAttribute(FQTV, "60", byte_array=True, packed=True, std_fix=bytearray([0x00] * 0x16)),
        PnrAttribute(ITIN, "30", byte_array=True, macro_name="WI0BS"),
        PnrAttribute(SUBS_CARD_SEG, "66"),
        PnrAttribute(GROUP_PLAN, "A0", std_var=bytearray([0x02, 0x01])),
        PnrAttribute(RCVD_FROM, "58", std_var=bytearray([0x80])),  # Indicate NEW item
        PnrAttribute(RECORD_LOC, "54", std_var=bytearray([0x00])),
        PnrAttribute(PHONE, "5C", std_var=bytearray([0x80])),  # Indicate NEW item
        PnrAttribute(REMARKS, "B0", std_var=bytearray([0x00, 0x00, 0x00, 0x00, 0x00])),  # Indicate NEW item
        PnrAttribute(PRS_SEATS, "80", std_var=bytearray([0x80])),  # Indicate NEW item
        PnrAttribute(HEADER, "20", byte_array=True, packed=True),
        PnrAttribute(VCR_COUPON, "64", std_var=bytearray([0x80])),  # Indicate NEW item
        PnrAttribute(ICE_DATA, "38", std_var=bytearray([0x80])),  # Indicate NEW item
    ]

    @classmethod
    def init_db(cls) -> None:
        cls.DB = [{"id": config.AAAPNR, "doc": list()}]
        cls.add_from_byte_array(byte_array={"PR00_20_SID": bytearray([0x00])}, key=HEADER, locator=config.AAAPNR)

    @staticmethod
    def get_pnr_data(pnr_locator: str, key: str, item_number: int, packed: bool = False,
                     starts_with: Optional[str] = None) -> Tuple[Optional[bytearray], int]:
        # item_number starts from 1 for the 1st item (index 0)
        try:
            pnr_doc = next(pnr["doc"] for pnr in Pnr.DB if pnr["id"] == pnr_locator)
            data_list = [element["data"] for element in pnr_doc if element["key"] == key]
        except StopIteration:
            raise PnrLocatorNotFoundError
        starts_with = DataType("C", input=starts_with).to_bytes() if starts_with is not None else None
        attribute = Pnr.get_attribute_by_key(key)
        if not attribute:
            raise PnrElementError
        start = (len(Pnr.STD_PREFIX_BYTES) + len(attribute.std_fix) + len(attribute.std_var)) \
            if packed else len(attribute.std_var)
        for item_number in range(item_number, len(data_list) + 1):
            data = data_list[item_number - 1]
            data = data[len(Pnr.STD_PREFIX_BYTES) + len(attribute.std_fix):] if not packed else data
            if starts_with is None:
                return data, item_number
            elif data[start: start + len(starts_with)] == starts_with:
                return data, item_number
        return None, item_number

    @staticmethod
    def get_len(pnr_locator: str, key: str) -> int:
        try:
            pnr_doc = next(pnr["doc"] for pnr in Pnr.DB if pnr["id"] == pnr_locator)
        except StopIteration:
            raise PnrLocatorNotFoundError
        return len([element for element in pnr_doc if element["key"] == key])

    @classmethod
    def get_pnr_doc(cls, pnr_locator: str) -> List[Dict[str, bytearray]]:
        try:
            pnr_doc = next(pnr["doc"] for pnr in cls.DB if pnr["id"] == pnr_locator)
        except StopIteration:
            pnr_doc: List[Dict[str, bytearray]] = list()
            Pnr.DB.append({"id": pnr_locator, "doc": pnr_doc})
        return pnr_doc

    @classmethod
    def get_attribute_by_name(cls, name: str) -> PnrAttribute:
        return next((attribute for attribute in cls.ATTRIBUTES if attribute.name == name), None)

    @classmethod
    def get_attribute_by_key(cls, key: str) -> PnrAttribute:
        return next((attribute for attribute in cls.ATTRIBUTES if attribute.key == key), None)

    @staticmethod
    def add_from_data(data: str, key: str, locator: str):
        attribute = Pnr.get_attribute_by_name(key)
        if attribute is None or attribute.byte_array or attribute.packed:
            raise PnrElementError
        pnr_doc: List[Dict[str, bytearray]] = Pnr.get_pnr_doc(locator)
        lrec = PnrLrec(attribute.key)
        lrec.data.extend(Pnr.STD_PREFIX_BYTES[:])
        lrec.data.extend(attribute.std_fix)
        lrec.data.extend(attribute.std_var)
        lrec.data.extend(DataType("C", input=data).to_bytes())
        pnr_doc.append(lrec.to_dict())

    @staticmethod
    def add_from_byte_array(byte_array: Dict[str, bytearray], key: str, locator: str):
        attribute = Pnr.get_attribute_by_name(key)
        if attribute is None or not attribute.byte_array or attribute.macro_name not in macros:
            raise PnrElementError
        pnr_doc: List[Dict[str, bytearray]] = Pnr.get_pnr_doc(locator)
        lrec = PnrLrec(attribute.key)
        if not attribute.packed:
            lrec.data.extend(Pnr.STD_PREFIX_BYTES[:])
            lrec.data.extend(attribute.std_fix)
            lrec.data.extend(attribute.std_var)
        lrec.data.extend(Stream(macros[attribute.macro_name]).to_bytes(byte_array))
        pnr_doc.append(lrec.to_dict())


class PnrLocator:
    VALID = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    LEN_OF_VALID = len(VALID)

    @staticmethod
    def to_ordinal(locator: str) -> int:
        ordinal = 0
        for character in locator:
            ordinal *= PnrLocator.LEN_OF_VALID
            ordinal += PnrLocator.VALID.index(character)
        return ordinal

    @staticmethod
    def to_locator(ordinal: int) -> str:
        locator = str()
        for _ in range(6):
            locator = PnrLocator.VALID[ordinal % PnrLocator.LEN_OF_VALID] + locator
            ordinal //= PnrLocator.LEN_OF_VALID
        return locator
