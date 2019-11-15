from typing import List, Dict, Union, Tuple, Optional

from assembly.mac2_data_macro import macros
from config import config
from db.stream import Stream
from utils.data_type import DataType
from utils.errors import PnrElementError


class PnrAttribute:

    def __init__(self, name: str, key: str, byte_array: bool = False, packed: bool = False, macro_name: str = None,
                 std_fix: bytearray = None, std_var: bytearray = None):
        self.name: str = name
        self.key: str = key
        self.byte_array: bool = byte_array
        self.packed: bool = packed
        self.macro_name: str = macro_name if macro_name else 'PR001W'
        self.std_fix = std_fix if std_fix else bytearray()
        self.std_var = std_var if std_var else bytearray()


class PnrLrec:

    def __init__(self, key: str, data: bytearray = None):
        self.key: str = key
        self.data: bytearray = data if data else bytearray()

    def to_dict(self):
        return self.__dict__


class Pnr:
    DB: List[Dict[str, Union[str, List[Dict[str, bytearray]]]]] = [{'id': config.AAAPNR, 'doc': list()}]
    HEADER = bytearray([0x00] * 0x14)
    ATTRIBUTES = [
        PnrAttribute('name', '50', std_var=bytearray([0x00, 0x00, 0x02, 0x00])),
        PnrAttribute('hfax', '84', std_fix=bytearray([0x00] * 0x08), std_var=bytearray([0x02, 0x01])),
        PnrAttribute('fqtv', '60', byte_array=True, packed=True, std_fix=bytearray([0x00] * 0x16)),
        PnrAttribute('itin', '30', byte_array=True, macro_name='WI0BS'),
        PnrAttribute('subs_card_seg', '66'),
        PnrAttribute('group_plan', 'A0', std_var=bytearray([0x02, 0x01])),
    ]

    @staticmethod
    def init_db() -> None:
        Pnr.DB = [{'id': config.AAAPNR, 'doc': list()}]

    @staticmethod
    def get_pnr_data(pnr_locator: str, key: str, item_number: int, packed: bool = False,
                     starts_with: Optional[str] = None) -> Tuple[Optional[bytearray], int]:
        # item_number starts from 1 for the 1st item (index 0)
        try:
            pnr_doc = next(pnr['doc'] for pnr in Pnr.DB if pnr['id'] == pnr_locator)
            data_list = [element['data'] for element in pnr_doc if element['key'] == key]
        except StopIteration:
            raise IndexError
        starts_with = DataType('C', input=starts_with).to_bytes() if starts_with is not None else None
        attribute = Pnr.get_attribute_by_key(key)
        start = (len(Pnr.HEADER) + len(attribute.std_fix) + len(attribute.std_var)) \
            if packed else len(attribute.std_var)
        for item_number in range(item_number, len(data_list) + 1):
            data = data_list[item_number - 1]
            data = data[len(Pnr.HEADER) + len(attribute.std_fix):] if not packed else data
            if starts_with is None:
                return data, item_number
            elif data[start: start + len(starts_with)] == starts_with:
                return data, item_number
        return None, item_number

    @staticmethod
    def get_len(pnr_locator: str, key: str) -> int:
        try:
            pnr_doc = next(pnr['doc'] for pnr in Pnr.DB if pnr['id'] == pnr_locator)
        except StopIteration:
            raise IndexError
        return len([element for element in pnr_doc if element['key'] == key])

    @staticmethod
    def get_pnr_doc(pnr_locator: str) -> List[Dict[str, bytearray]]:
        try:
            pnr_doc = next(pnr['doc'] for pnr in Pnr.DB if pnr['id'] == pnr_locator)
        except StopIteration:
            pnr_doc: List[Dict[str, bytearray]] = list()
            Pnr.DB.append({'id': pnr_locator, 'doc': pnr_doc})
        return pnr_doc

    @staticmethod
    def get_attribute_by_name(name: str) -> PnrAttribute:
        return next((attribute for attribute in Pnr.ATTRIBUTES if attribute.name == name), None)

    @staticmethod
    def get_attribute_by_key(key: str) -> PnrAttribute:
        return next((attribute for attribute in Pnr.ATTRIBUTES if attribute.key == key), None)

    @staticmethod
    def add_from_data(data: str, key: str, locator: str):
        attribute = Pnr.get_attribute_by_name(key)
        if attribute is None or attribute.byte_array or attribute.packed:
            raise PnrElementError
        pnr_doc: List[Dict[str, bytearray]] = Pnr.get_pnr_doc(locator)
        lrec = PnrLrec(attribute.key)
        lrec.data.extend(Pnr.HEADER[:])
        lrec.data.extend(attribute.std_fix)
        lrec.data.extend(attribute.std_var)
        lrec.data.extend(DataType('C', input=data).to_bytes())
        pnr_doc.append(lrec.to_dict())

    @staticmethod
    def add_from_byte_array(byte_array: Dict[str, bytearray], key: str, locator: str):
        attribute = Pnr.get_attribute_by_name(key)
        if attribute is None or not attribute.byte_array or attribute.macro_name not in macros:
            raise PnrElementError
        pnr_doc: List[Dict[str, bytearray]] = Pnr.get_pnr_doc(locator)
        lrec = PnrLrec(attribute.key)
        if not attribute.packed:
            lrec.data.extend(Pnr.HEADER[:])
            lrec.data.extend(attribute.std_fix)
            lrec.data.extend(attribute.std_var)
        lrec.data.extend(Stream(macros[attribute.macro_name]).to_bytes(byte_array))
        pnr_doc.append(lrec.to_dict())


class PnrLocator:
    VALID = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
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
