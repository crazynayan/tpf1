from v2.data_type import DataType

pnr_db = [
    {
        'id': 'aaapnr',
        'doc': [
            {
                'key': '50',
                # f"{DataType('C', input='C/21VEENA WORLD').value:X}"
                'data': '00000200C361F2F1E5C5C5D5C140E6D6D9D3C4',
            },
            {
                'key': '50',
                # f"{DataType('C', input='1ZAVERI/NAYAN MR').value:X}"
                'data': '00000201F1E9C1E5C5D9C961D5C1E8C1D540D4D9',
            },
            {
                'key': '50',
                # f"{DataType('C', input='1ZAVERI/PURVI MRS').value:X}"
                'data': '00000202F1E9C1E5C5D9C961D5C1E8C1D540D4D9E2',
            },
            {
                'key': '50',
                # f"{DataType('C', input='I/ZAVERI/S').value:X}"
                'data': '00000203C961E9C1E5C5D9C961E2',
            },
        ],
    },
]


class Pnr:
    @staticmethod
    def get_pnr_data(pnr_locator: str, key: str, item_number: int) -> bytearray:
        try:
            pnr_doc = next(pnr['doc'] for pnr in pnr_db if pnr['id'] == pnr_locator)
            data_list = [element['data'] for element in pnr_doc if element['key'] == key]
            data = data_list[item_number - 1]
        except (StopIteration, IndexError):
            raise IndexError
        data = DataType('X', input=data).to_bytes()
        return data

    @staticmethod
    def get_len(pnr_locator: str, key: str) -> int:
        try:
            pnr_doc = next(pnr['doc'] for pnr in pnr_db if pnr['id'] == pnr_locator)
        except StopIteration:
            raise IndexError
        return len([element for element in pnr_doc if element['key'] == key])
