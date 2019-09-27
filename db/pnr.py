from typing import List, Dict, Union, Tuple, Optional

from config import config
from v2.data_type import DataType


class Pnr:
    DB: List[Dict[str, Union[str, List[Dict[str, str]]]]] = [{'id': config.AAAPNR, 'doc': list()}]
    HEADER = '00' * 0x14
    HDR: Dict[str, Dict[str, str]] = {
        '50': {     # NAME
            'std_fix': '',
            'std_var': '00000200',
        },
        '84': {     # HFAX
            'std_fix': '00' * 0x08,
            'std_var': '0201',
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
        start = (len(Pnr.HEADER) + len(Pnr.HDR[key]['std_fix']) + len(Pnr.HDR[key]['std_var'])) >> 1 if packed else \
            len(Pnr.HDR[key]['std_var']) >> 1
        for item_number in range(item_number, len(data_list) + 1):
            data = data_list[item_number - 1]
            data = data[len(Pnr.HEADER) + len(Pnr.HDR[key]['std_fix']):] if not packed else data
            data_bytes = DataType('X', input=data).to_bytes()
            if starts_with is None:
                return data_bytes, item_number
            elif data_bytes[start: start + len(starts_with)] == starts_with:
                return data_bytes, item_number
        return None, item_number

    @staticmethod
    def get_len(pnr_locator: str, key: str) -> int:
        try:
            pnr_doc = next(pnr['doc'] for pnr in Pnr.DB if pnr['id'] == pnr_locator)
        except StopIteration:
            raise IndexError
        return len([element for element in pnr_doc if element['key'] == key])

    @staticmethod
    def get_pnr_doc(pnr_locator: str) -> List[Dict[str, str]]:
        try:
            pnr_doc = next(pnr['doc'] for pnr in Pnr.DB if pnr['id'] == pnr_locator)
        except StopIteration:
            pnr_doc: List[Dict[str, str]] = list()
            Pnr.DB.append({'id': pnr_locator, 'doc': pnr_doc})
        return pnr_doc

    @staticmethod
    def add_elements(pnr_doc: List[Dict[str, str]], elements: List[str], key: str) -> None:
        for element in elements:
            lrec = dict()
            lrec['key'] = key
            lrec['data'] = f"{Pnr.HEADER}{Pnr.HDR[key]['std_fix']}{Pnr.HDR[key]['std_var']}" \
                           f"{DataType('C', input=element).value:X}"
            pnr_doc.append(lrec)

    @staticmethod
    def add_names(pnr_locator: str, names: List[str]) -> None:
        pnr_doc = Pnr.get_pnr_doc(pnr_locator)
        Pnr.add_elements(pnr_doc, names, '50')

    @staticmethod
    def add_hfax(pnr_locator: str, hfax: List[str]) -> None:
        pnr_doc = Pnr.get_pnr_doc(pnr_locator)
        Pnr.add_elements(pnr_doc, hfax, '84')

    @staticmethod
    def init_db() -> None:
        Pnr.DB = [{'id': config.AAAPNR, 'doc': list()}]
