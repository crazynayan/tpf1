from typing import List, Dict, Union, Tuple, Optional

from assembly.program import program
from db.stream import Stream


class Tpfdf:
    DB: List[Dict[str, Union[str, List[Dict[str, bytearray]]]]] = list()
    HDR = bytearray([0x00] * 3)

    @staticmethod
    def get_lrec(ref_name: str, key: str, item_number: int,
                 other_keys: Dict[str, Tuple[str, int]]) -> Tuple[Optional[bytearray], int]:
        # item_number starts from 1 for the 1st item (index 0)
        ref = Tpfdf.get_ref(ref_name)
        lrec_list = [lrec['data'] for lrec in ref if lrec['key'] == key]
        if not lrec_list:
            return None, item_number
        for item_number in range(item_number, len(lrec_list) + 1):
            lrec = lrec_list[item_number - 1]
            symbol_table = program.macros[ref_name].symbol_table
            if all(eval(f'{lrec[symbol_table[field_name].dsp: symbol_table[field_name].dsp + length]} {expression}')
                   for field_name, (expression, length) in other_keys.items()):
                return lrec, item_number
        return None, item_number

    @staticmethod
    def get_ref(ref_name: str) -> List[Dict[str, bytearray]]:
        ref = next((df_record['doc'] for df_record in Tpfdf.DB if df_record['id'] == ref_name), None)
        if ref is None:
            ref: List[Dict[str, bytearray]] = list()
            Tpfdf.DB.append({'id': ref_name, 'doc': ref})
        return ref

    @staticmethod
    def add(dict_lrecs: List[Dict[str, bytearray]], ref_name: str, key: str) -> None:
        ref = Tpfdf.get_ref(ref_name)
        program.macros[ref_name].load()
        for lrec_dict in dict_lrecs:
            lrec = dict()
            lrec['key'] = key
            lrec['data'] = bytearray()
            lrec['data'].extend(Stream.to_bytes(lrec_dict, program.macros[ref_name]))
            ref.append(lrec)
