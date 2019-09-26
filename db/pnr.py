from typing import List, Dict, Union, Tuple, Optional

from v2.data_type import DataType
from config import config


class Pnr:
    PNR_DB: List[Dict[str, Union[str, List[Dict[str, str]]]]] = [{'id': config.AAAPNR, 'doc': list()}]
    NAME_KEY = '50'
    FQTV_KEY = '60'
    ITIN_KEY = '30'
    HFAX_KEY = '84'
    NAME_PREFIX = '00000200'

    @staticmethod
    def get_pnr_data(pnr_locator: str, key: str, item_number: int,
                     starts_with: Optional[str] = None) -> Tuple[Optional[bytearray], int]:
        try:
            pnr_doc = next(pnr['doc'] for pnr in Pnr.PNR_DB if pnr['id'] == pnr_locator)
            data_list = [element['data'] for element in pnr_doc if element['key'] == key]
        except StopIteration:
            raise IndexError
        starts_with = DataType('C', input=starts_with).to_bytes() if starts_with is not None else None
        while True:
            if item_number > len(data_list):
                return None, item_number
            data = data_list[item_number - 1]
            data = DataType('X', input=data).to_bytes()
            if starts_with is None:
                return data, item_number
            elif data[:len(starts_with)] == starts_with:
                return data, item_number
            item_number += 1

    @staticmethod
    def get_len(pnr_locator: str, key: str) -> int:
        try:
            pnr_doc = next(pnr['doc'] for pnr in Pnr.PNR_DB if pnr['id'] == pnr_locator)
        except StopIteration:
            raise IndexError
        return len([element for element in pnr_doc if element['key'] == key])

    @staticmethod
    def add_names(pnr_locator: str, names: List[str]) -> None:
        try:
            pnr_doc = next(pnr['doc'] for pnr in Pnr.PNR_DB if pnr['id'] == pnr_locator)
        except StopIteration:
            pnr_doc: List[Dict[str, str]] = list()
            Pnr.PNR_DB.append({'id': pnr_locator, 'doc': pnr_doc})
        for name in names:
            lrec = dict()
            lrec['key'] = Pnr.NAME_KEY
            lrec['data'] = f"{Pnr.NAME_PREFIX}{DataType('C', input=name).value:X}"
            pnr_doc.append(lrec)

    @staticmethod
    def init_db() -> None:
        Pnr.PNR_DB = [{'id': config.AAAPNR, 'doc': list()}]
