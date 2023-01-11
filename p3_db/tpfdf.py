from typing import List, Dict, Union, Tuple, Optional

from p1_utils.data_type import DataType
from p2_assembly.mac2_data_macro import get_macros
from p3_db.stream import Stream


class Tpfdf:
    DB: List[Dict[str, Union[str, List[Dict[str, bytearray]]]]] = list()

    @staticmethod
    def get_ref(ref_name: str) -> List[Dict[str, bytearray]]:
        ref = next((df_record["doc"] for df_record in Tpfdf.DB if df_record["id"] == ref_name), None)
        if ref is None:
            ref: List[Dict[str, bytearray]] = list()
            Tpfdf.DB.append({"id": ref_name, "doc": ref})
        return ref

    @staticmethod
    def get_lrec_from_item_number(ref_name: str, item_number: int) -> Optional[bytearray]:
        # item_number starts from 1 for the 1st item (index 0)
        ref = Tpfdf.get_ref(ref_name)
        index = item_number - 1
        if not 0 <= index < len(ref):
            return None
        return ref[index]["data"]

    @staticmethod
    def set_lrec_from_item_number(ref_name: str, item_number: int, data: bytearray) -> bool:
        # item_number starts from 1 for the 1st item (index 0)
        ref = Tpfdf.get_ref(ref_name)
        index = item_number - 1
        if not 0 <= index < len(ref):
            return False
        ref[index]["data"] = data
        return True

    @staticmethod
    def get_item_numbers(ref_name: str, key: str, other_keys: Dict[str, Tuple[str, int]], start: int = 0) -> List[int]:
        ref = Tpfdf.get_ref(ref_name)
        start_index = 0 if start == 0 else start - 1
        if not 0 <= start_index < len(ref):
            return list()
        if ref_name not in get_macros():
            return list()
        symbol_table = get_macros()[ref_name].all_labels
        return [index + start_index + 1 for index, lrec in enumerate(ref[start_index:]) if lrec["key"] == key and
                all(eval(f"{lrec['data'][symbol_table[field_name].dsp: symbol_table[field_name].dsp + length]} {exp}")
                    for field_name, (exp, length) in other_keys.items())]

    @staticmethod
    def get_size(ref_name: str):
        return len(Tpfdf.get_ref(ref_name))

    @staticmethod
    def add(data: Dict[str, bytearray], key: str, ref_name: str) -> None:
        ref = Tpfdf.get_ref(ref_name)
        get_macros()[ref_name].load()
        lrec = dict()
        lrec["key"] = key
        input_data: bytearray = Stream(get_macros()[ref_name]).to_bytes(data)
        if len(input_data) >= 3:
            input_data = input_data[3:]
        final_data = DataType("H", input=f"{len(input_data) + 3}").to_bytes()
        final_data.extend(DataType("X", input=key).to_bytes(length=1))
        final_data.extend(input_data)
        lrec["data"] = final_data
        ref.append(lrec)

    @staticmethod
    def add_bytes(data: bytearray, key: str, ref_name: str) -> None:
        ref = Tpfdf.get_ref(ref_name)
        get_macros()[ref_name].load()
        lrec = dict()
        lrec["key"] = key
        lrec["data"] = data
        ref.append(lrec)

    @staticmethod
    def init_db(ref_name: Optional[str] = None):
        if ref_name is None:
            Tpfdf.DB = list()
        else:
            df_record = next((df_record for df_record in Tpfdf.DB if df_record["id"] == ref_name), None)
            if df_record is not None:
                Tpfdf.DB.remove(df_record)
        return

    @staticmethod
    def delete_lrec(ref_name: str, item_numbers: list) -> None:
        # item_number starts from 1 for the 1st item (index 0)
        ref = Tpfdf.get_ref(ref_name)
        indexes = [index - 1 for index in item_numbers if 0 <= index - 1 < len(ref)]
        for index in sorted(indexes, reverse=True):
            del ref[index]
        return
