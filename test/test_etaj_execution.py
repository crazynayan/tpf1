import unittest

from assembly.mac2_data_macro import macros
from config import config
from db.flat_file import FlatFile
from db.pnr import Pnr
from db.stream import Stream
from test.input_td import TD
from utils.data_type import DataType


class EtajTest(unittest.TestCase):
    def setUp(self) -> None:
        Pnr.init_db()
        TD.state.init_run()
        Pnr.add_group_plan(config.AAAPNR, ['BTS-B4T0/108/11-FINANCIAL SERVICES'])
        TD.state.setup.aaa['WA0POR'] = DataType('X', input='006F2F').to_bytes()
        TD.state.setup.aaa['WA0FNS'] = bytearray([TD.wa0tvl])
        self.tj_id = DataType('C', input='TJ').value
        self.iy_id = DataType('C', input='IY').value
        self.iy1lok = macros['IY1IY'].evaluate('#IY1LOK')

    def tjr_setup(self, iy9aon: bytearray, pool: int = 1, iy1lok: bool = False) -> None:
        iy_item = dict()
        iy_item['IY9AON'] = iy9aon
        empty_item = iy_item.copy()
        empty_item['IY9AON'] = bytearray([config.ZERO])
        if iy1lok:
            iy_item['IY9AGY'] = bytearray([self.iy1lok])
        iy_bytes = Stream(macros['IY1IY']).item_to_bytes([iy_item], 'IY1ATH', count='IY1CTR')
        iy_address = FlatFile.add_pool(iy_bytes, self.iy_id)
        for _ in range(pool - 1):
            data = dict()
            data['IY1FCH'] = DataType('F', input=str(iy_address)).to_bytes()
            iy_bytes = Stream(macros['IY1IY']).item_to_bytes([empty_item], 'IY1ATH', count='IY1CTR', data=data)
            iy_address = FlatFile.add_pool(iy_bytes, self.iy_id)
        tj_bytes = bytearray([config.ZERO] * 404)
        tj_bytes.extend(DataType('F', input=str(iy_address)).to_bytes())
        FlatFile.add_fixed(tj_bytes, self.tj_id, macros['SYSEQC'].evaluate('#TJRRI'), 0x17F)

    def test_branch_validation_fail_lok_off(self) -> None:
        iy9aon = DataType('X', input='00006F2F').to_bytes()
        self.tjr_setup(iy9aon, pool=3)
        label = TD.state.run('TS21', aaa=True)
        self.assertEqual('$$ETK4$$.1', label)
        self.assertEqual(8, TD.state.regs.R6)

    def test_branch_validation_pass_lok_on(self) -> None:
        iy9aon = DataType('X', input='00006F2F').to_bytes()
        self.tjr_setup(iy9aon, iy1lok=True)
        label = TD.state.run('TS21', aaa=True)
        self.assertEqual('TS21EXIT.1', label)

    def test_finwc_fail(self) -> None:
        iy9aon = DataType('X', input='00006F2F').to_bytes()
        self.tjr_setup(iy9aon)
        TD.state.setup.errors.add('$$ETAJ$$.35')
        label = TD.state.run('TS21', aaa=True)
        self.assertEqual('ETAJ500.1', label)
        self.assertIn('0140F1', TD.state.dumps)


# noinspection PyPep8Naming
def tearDownModule():
    if 'ETAJ' in TD.state.DEBUG.seg_list:
        with open('trace_log.txt', 'w') as trace_log:
            trace_log.write('\n'.join([str(trace) for trace in TD.state.DEBUG.get_no_hit()]))
    return


if __name__ == '__main__':
    unittest.main()
