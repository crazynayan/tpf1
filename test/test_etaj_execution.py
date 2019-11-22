import unittest
from base64 import b64encode

from assembly.mac2_data_macro import macros
from config import config
from execution.ex5_execute import Execute
from firestore.test_data import TestData
from utils.data_type import DataType


class EtajTest(unittest.TestCase):
    tpf_server: Execute = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.tpf_server = Execute()
        # cls.tpf_server.init_debug(['ETAJ'])

    @classmethod
    def tearDownClass(cls) -> None:
        if 'ETAJ' in cls.tpf_server.DEBUG.seg_list:
            with open('trace_log.txt', 'w') as trace_log:
                trace_log.write('\n'.join([str(trace) for trace in cls.tpf_server.DEBUG.get_no_hit()]))
        return

    def setUp(self) -> None:
        self.tpf_server.init_run()
        self.test_data = TestData()
        self.output = self.test_data.output
        # Test data setup
        self.test_data.add_pnr('group_plan', data='BTS-B4T0/108/11-FINANCIAL SERVICES')
        self.aaa = self.test_data.add_core(['WA0POR', 'WA0FNS'], 'WA0AA')
        self.aaa['WA0POR'].data = b64encode(DataType('X', input='006F2F').to_bytes()).decode()
        self.aaa['WA0FNS'].data = b64encode(bytes([macros['WA0AA'].evaluate('#WA0TVL')])).decode()
        self.output.add_regs(['R6'])
        # Item setup
        self.iy_item = dict()
        self.iy_item['IY9AON'] = bytearray([config.ZERO] * 4)
        self.iy_item['IY9AGY'] = bytearray([config.ZERO])

    def _tjr_setup(self, iy_chain_count: int = 0):
        self.test_data.add_file(fixed_rec_id=DataType('C', input='TJ').value,
                                fixed_file_type=macros['SYSEQC'].evaluate('#TJRRI'),
                                fixed_file_ordinal=0x17F,
                                fixed_macro_name='TJ1TJ',
                                pool_rec_id=DataType('C', input='IY').value,
                                pool_macro_name='IY1IY',
                                pool_index_field='TJ1IY1',
                                pool_forward_chain_label='IY1FCH',
                                pool_item_field='IY1ATH',
                                pool_item_count_field='IY1CTR',
                                pool_item_field_bytes=self.iy_item,
                                pool_item_forward_chain_count=iy_chain_count,
                                )
        return

    def test_branch_validation_fail_lok_off(self) -> None:
        self.iy_item['IY9AON'] = DataType('X', input='00006F2F').to_bytes()
        self._tjr_setup(2)
        self.tpf_server.run('TS21', self.test_data)
        self.assertEqual('$$ETK4$$.1', self.output.last_line)
        self.assertEqual(8, self.output.regs['R6'])

    def test_branch_validation_pass_lok_on(self) -> None:
        self.iy_item['IY9AON'] = DataType('X', input='00006F2F').to_bytes()
        self.iy_item['IY9AGY'] = bytearray([macros['IY1IY'].evaluate('#IY1LOK')])
        self._tjr_setup()
        self.tpf_server.run('TS21', self.test_data)
        self.assertEqual('TS21EXIT.1', self.output.last_line)

    def test_finwc_fail(self) -> None:
        self.iy_item['IY9AON'] = DataType('X', input='00006F2F').to_bytes()
        self._tjr_setup()
        self.test_data.errors.append('$$ETAJ$$.35')
        self.tpf_server.run('TS21', self.test_data)
        self.assertEqual('ETAJ500.1', self.output.last_line)
        self.assertIn('0140F1', self.output.dumps)


if __name__ == '__main__':
    unittest.main()
