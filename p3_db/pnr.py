from typing import List, Dict, Union, Tuple, Optional

from config import config
from p1_utils.data_type import DataType
from p1_utils.domain import get_domain
from p1_utils.errors import PnrElementError, PnrLocatorNotFoundError, NotFoundInSymbolTableError, TestDataError
from p2_assembly.mac0_generic import LabelReference
from p2_assembly.mac2_data_macro import get_macros
from p3_db.stream import Stream

NAME, HFAX, FQTV, ITIN, RCVD_FROM, PHONE, REMARKS = "name", "hfax", "fqtv", "itin", "rcvd_from", "phone", "remarks"
SUBS_CARD_SEG, GROUP_PLAN, RECORD_LOC, PRS_SEATS = "subs_card_seg", "group_plan", "record_loc", "prs_seats"
HEADER, VCR_COUPON, ICE_DATA, GFAX, ADM_CLUB = "header", "vcr_coupon", "ice_data", "gfax", "adm_club"
TKT_TIM_LMT = "tkt_tim_lmt"


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


def load_pdequ():
    pdequ = dict()
    macros = get_macros()
    try:
        macros["PDEQU"].load()
    except KeyError:
        return dict()
    for label, label_ref in macros["PDEQU"].all_labels.items():
        if not label.startswith("#PD_") or label == "#PD_MAX_PD_ITEMS":
            continue
        field = label[:-2] if label.endswith("_K") or label.endswith("_D") else label
        if field not in pdequ:
            pdequ[field] = dict()
        if label.endswith("_K"):
            pdequ[field]["key"] = label_ref.dsp
        elif label.endswith("_D"):
            pdequ[field]["designator"] = label_ref.dsp
        else:
            pdequ[field]["index"] = label_ref.dsp
    return pdequ


class Pnr:
    DB: List[Dict[str, Union[str, List[Dict[str, bytearray]]]]] = [{"id": config.AAAPNR, "doc": list()}]
    STD_PREFIX_BYTES = bytearray([0x00] * 0x14)
    PDEQU: Dict[str, Dict[str, int]] = load_pdequ()
    ATTRIBUTES = [
        PnrAttribute(NAME, "50", std_var=bytearray([0x00, 0x00, 0x02, 0x00])),
        PnrAttribute(HFAX, "84", std_fix=bytearray([0x00] * 0x08), std_var=bytearray([0x02, 0x01])),
        PnrAttribute(GFAX, "88", std_fix=bytearray([0x00] * 0x08), std_var=bytearray([0x02, 0x01])),
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
        PnrAttribute(ADM_CLUB, "82", std_var=bytearray([0x80])),  # Indicate NEW item
        PnrAttribute(TKT_TIM_LMT, "68", std_var=bytearray([0x80])),  # Indicate NEW item
    ]
    DOMAIN = get_domain()

    @classmethod
    def init_pdequ(cls):
        if cls.DOMAIN != get_domain():
            cls.PDEQU = load_pdequ()
            cls.DOMAIN = get_domain()
        return

    @classmethod
    def init_db(cls) -> None:
        cls.DB = [{"id": config.AAAPNR, "doc": list()}]
        cls.add_from_byte_array(byte_array={"PR00_20_SID": bytearray([0x00])}, key=HEADER, locator=config.AAAPNR)

    @classmethod
    def load_macros(cls):
        for attribute in Pnr.ATTRIBUTES:
            get_macros()[attribute.macro_name].load()
        return

    @classmethod
    def get_field(cls, field_name) -> Optional[LabelReference]:
        macros = get_macros()
        pnr_macros: set = {attribute.macro_name for attribute in Pnr.ATTRIBUTES}
        return next((macros[macro].lookup(field_name) for macro in pnr_macros if macros[macro].check(field_name)), None)

    @classmethod
    def is_valid_field(cls, field_name) -> bool:
        return cls.get_field(field_name) is not None

    @classmethod
    def get_field_len(cls, field_name) -> int:
        field: LabelReference = cls.get_field(field_name)
        if not field:
            raise TestDataError
        return field.length

    @classmethod
    def get_field_dsp(cls, field_name) -> int:
        field: LabelReference = cls.get_field(field_name)
        if not field:
            raise TestDataError
        return field.dsp

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
                if packed and attribute.name == RCVD_FROM:
                    data = data[len(attribute.std_var):]
                return data, item_number
            elif data[start: start + len(starts_with)] == starts_with:
                return data, item_number
        return None, item_number

    @staticmethod
    def replace_pnr_data(data: bytearray, pnr_locator: str, key: str, item_number: int, packed: bool = False) -> None:
        # item_number starts from 1 for the 1st item (index 0)
        try:
            pnr_doc: List[Dict[str, bytearray]] = next(pnr["doc"] for pnr in Pnr.DB if pnr["id"] == pnr_locator)
        except StopIteration:
            raise PnrLocatorNotFoundError
        attribute = Pnr.get_attribute_by_key(key)
        if not attribute:
            raise PnrElementError
        new_data = bytearray()
        if not packed:
            new_data.extend(Pnr.STD_PREFIX_BYTES[:])
            new_data.extend(attribute.std_fix)
            new_data.extend(attribute.std_var)
        new_data.extend(data)
        pnr_doc.sort(key=lambda pnr_lrec: pnr_lrec["key"])
        key_index = next(index for index, pnr_lrec in enumerate(pnr_doc) if pnr_lrec["key"] == key)
        index_to_update = key_index + item_number - 1
        pnr_doc[index_to_update]["data"] = new_data
        return

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
        macros = get_macros()
        attribute = Pnr.get_attribute_by_name(key)
        if attribute is None or not attribute.byte_array or attribute.macro_name not in get_macros():
            raise PnrElementError
        pnr_doc: List[Dict[str, bytearray]] = Pnr.get_pnr_doc(locator)
        lrec = PnrLrec(attribute.key)
        if not attribute.packed:
            lrec.data.extend(Pnr.STD_PREFIX_BYTES[:])
            lrec.data.extend(attribute.std_fix)
            lrec.data.extend(attribute.std_var)
        try:
            data_bytes = Stream(macros[attribute.macro_name]).to_bytes(byte_array)
            lrec.data.extend(data_bytes)
        except NotFoundInSymbolTableError:
            data_bytes = Stream(macros["PR001W"]).to_bytes(byte_array)
            lrec.data = data_bytes
        pnr_doc.append(lrec.to_dict())

    @classmethod
    def get_pdequ_label(cls, idk: str, value: int) -> str:
        if idk not in {"index", "designator", "key"}:
            return str()
        return next((label for label, idk_dict in cls.PDEQU.items() if idk_dict[idk] == value), str())


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

    @staticmethod
    def is_valid(locator: str) -> bool:
        return isinstance(locator, str) and (not locator or len(locator) == 6 and locator.isalpha())
