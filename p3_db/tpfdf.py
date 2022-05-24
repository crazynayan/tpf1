from typing import List, Dict, Union, Tuple, Optional

from p2_assembly.mac2_data_macro import macros
from p3_db.stream import Stream


class Tpfdf:
    DB: List[Dict[str, Union[str, List[Dict[str, bytearray]]]]] = list()
    HDR = bytearray([0x00] * 3)

    @staticmethod
    def get_lrec(ref_name: str, key: str, item_number: int,
                 other_keys: Dict[str, Tuple[str, int]]) -> Tuple[Optional[bytearray], int]:
        # item_number starts from 1 for the 1st item (index 0)
        ref = Tpfdf.get_ref(ref_name)
        lrec_list = [lrec for lrec in ref]
        if not lrec_list or item_number > len(lrec_list):
            return None, item_number
        if item_number != 0 and not other_keys:
            lrec = lrec_list[item_number - 1]
            data = lrec_list[item_number - 1]['data'] if lrec['key'] == key else None
            return data, item_number
        adjusted_number = 0 if not item_number else item_number - 1
        for updated_item in range(adjusted_number, len(lrec_list)):
            lrec = lrec_list[updated_item]
            if lrec['key'] != key:
                continue
            symbol_table = macros[ref_name].all_labels
            if all(eval(f"{lrec['data'][symbol_table[field_name].dsp: symbol_table[field_name].dsp + length]} {exp}")
                   for field_name, (exp, length) in other_keys.items()):
                return lrec['data'], updated_item + 1
        return None, item_number

    @staticmethod
    def get_ref(ref_name: str) -> List[Dict[str, bytearray]]:
        ref = next((df_record['doc'] for df_record in Tpfdf.DB if df_record['id'] == ref_name), None)
        if ref is None:
            ref: List[Dict[str, bytearray]] = list()
            Tpfdf.DB.append({'id': ref_name, 'doc': ref})
        return ref

    @staticmethod
    def add(data: Dict[str, bytearray], key: str, ref_name: str) -> None:
        ref = Tpfdf.get_ref(ref_name)
        macros[ref_name].load()
        lrec = dict()
        lrec['key'] = key
        lrec['data'] = bytearray()
        lrec['data'].extend(Stream(macros[ref_name]).to_bytes(data))
        ref.append(lrec)

    @staticmethod
    def add_bytes(data: bytearray, key: str, ref_name: str) -> None:
        ref = Tpfdf.get_ref(ref_name)
        macros[ref_name].load()
        lrec = dict()
        lrec['key'] = key
        lrec['data'] = data
        ref.append(lrec)

    @staticmethod
    def init_db(ref_name: Optional[str] = None):
        if ref_name is None:
            Tpfdf.DB = list()
        else:
            df_record = next((df_record for df_record in Tpfdf.DB if df_record['id'] == ref_name), None)
            if df_record is not None:
                Tpfdf.DB.remove(df_record)
        return

    @staticmethod
    def delete_lrec(ref_name: str, item_number: int) -> bool:
        # item_number starts from 1 for the 1st item (index 0)
        ref = Tpfdf.get_ref(ref_name)
        delete_item = item_number - 1
        if not 0 <= delete_item < len(ref):
            return False
        ref.remove(ref[delete_item])
        return True
