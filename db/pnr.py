from typing import List, Dict, Union, Tuple, Optional

from assembly.mac2_data_macro import macros
from config import config
from db.stream import Stream
from utils.data_type import DataType


class Pnr:
    DB: List[Dict[str, Union[str, List[Dict[str, bytearray]]]]] = [{'id': config.AAAPNR, 'doc': list()}]
    HEADER = bytearray([0x00] * 0x14)
    HDR: Dict[str, Dict[str, bytearray]] = {
        '50': {     # NAME
            'std_fix': bytearray(),
            'std_var': bytearray([0x00, 0x00, 0x02, 0x00]),
        },
        '84': {     # HFAX
            'std_fix': bytearray([0x00] * 0x08),
            'std_var': bytearray([0x02, 0x01]),
        },
        '60': {     # FQTV
            'std_fix': bytearray([0x00] * 0x16),
            'std_var': bytearray(),
        },
        '30': {     # ITIN
            'std_fix': bytearray(),
            'std_var': bytearray(),
        },
        '66': {  # SUBS_CARD_SEG
            'std_fix': bytearray(),
            'std_var': bytearray(),
        },
        'A0': {  # GROUP_PLAN
            'std_fix': bytearray(),
            'std_var': bytearray([0x02, 0x01]),
        },
    }

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
        start = (len(Pnr.HEADER) + len(Pnr.HDR[key]['std_fix']) + len(Pnr.HDR[key]['std_var'])) if packed else \
            len(Pnr.HDR[key]['std_var'])
        for item_number in range(item_number, len(data_list) + 1):
            data = data_list[item_number - 1]
            data = data[len(Pnr.HEADER) + len(Pnr.HDR[key]['std_fix']):] if not packed else data
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
    def add_elements(pnr_doc: List[Dict[str, bytearray]], elements: List[bytearray],
                     key: str, packed: bool = False) -> None:
        for element in elements:
            lrec = dict()
            lrec['key'] = key
            lrec['data'] = bytearray()
            if not packed:
                lrec['data'].extend(Pnr.HEADER[:])
                lrec['data'].extend(Pnr.HDR[key]['std_fix'])
                lrec['data'].extend(Pnr.HDR[key]['std_var'])
            lrec['data'].extend(element)
            pnr_doc.append(lrec)

    @staticmethod
    def add_names(pnr_locator: str, names: List[str]) -> None:
        pnr_doc = Pnr.get_pnr_doc(pnr_locator)
        names: List[bytearray] = [DataType('C', input=name).to_bytes() for name in names]
        Pnr.add_elements(pnr_doc, names, '50')

    @staticmethod
    def add_group_plan(pnr_locator: str, group_plans: List[str]) -> None:
        pnr_doc = Pnr.get_pnr_doc(pnr_locator)
        group_plans: List[bytearray] = [DataType('C', input=group_plan).to_bytes() for group_plan in group_plans]
        Pnr.add_elements(pnr_doc, group_plans, 'A0')

    @staticmethod
    def add_hfax(pnr_locator: str, hfax: List[str]) -> None:
        pnr_doc = Pnr.get_pnr_doc(pnr_locator)
        hfax: List[bytearray] = [DataType('C', input=host_fact).to_bytes() for host_fact in hfax]
        Pnr.add_elements(pnr_doc, hfax, '84')

    @staticmethod
    def add_fqtv(pnr_locator: str, frequent_travellers: List[Dict[str, bytearray]]) -> None:
        pnr_doc = Pnr.get_pnr_doc(pnr_locator)
        macros['PR001W'].load()
        frequent_travellers: List[bytearray] = [Stream(macros['PR001W']).to_bytes(fqtv) for fqtv in frequent_travellers]
        Pnr.add_elements(pnr_doc, frequent_travellers, '60', packed=True)

    @staticmethod
    def add_itin(pnr_locator: str, itineraries: List[Dict[str, bytearray]]) -> None:
        pnr_doc = Pnr.get_pnr_doc(pnr_locator)
        macros['WI0BS'].load()
        itineraries: List[bytearray] = [Stream(macros['WI0BS']).to_bytes(itin) for itin in itineraries]
        Pnr.add_elements(pnr_doc, itineraries, '30')

    @staticmethod
    def add_subs_card_seg(pnr_locator: str, subs_card_segs: List[str]) -> None:
        pnr_doc = Pnr.get_pnr_doc(pnr_locator)
        subs_card_segs: List[bytearray] = [DataType('C', input=subs_card_seg).to_bytes()
                                           for subs_card_seg in subs_card_segs]
        Pnr.add_elements(pnr_doc, subs_card_segs, '66')

    @staticmethod
    def init_db() -> None:
        Pnr.DB = [{'id': config.AAAPNR, 'doc': list()}]


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
