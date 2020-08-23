import unittest

from execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS
from utils.data_type import DataType


class Wgu4Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()

    def test_wgu4_new_wgul_path(self):
        self.test_data.output.debug = ['WGU4']
        self.test_data.add_pnr_element(['1ZAVERI/NAYAN'], 'name')
        self.test_data.set_field('MH1BT11', bytes([0x01]))
        self.test_data.set_field('MI0ACC', DataType('C', input='FFAAC416M24').to_bytes())
        test_data = self.tpf_server.run('TS24', self.test_data)
        self.assertEqual('TS24EXIT.1', test_data.output.last_line)
        self.assertEqual(list(), test_data.output.messages)
        self.assertEqual(0, test_data.output.regs['R0'])

    def test_wgu4_old_path(self):
        self.test_data.output.debug = ['WGU4']
        self.test_data.add_pnr_element(['1ZAVERI/NAYAN'], 'name')
        self.test_data.set_field('MI0ACC', DataType('C', input='FFAAC416M24').to_bytes())
        test_data = self.tpf_server.run('TS24', self.test_data)
        self.assertEqual('TS24EXIT.1', test_data.output.last_line)
        self.assertEqual(list(), test_data.output.messages)
        self.assertEqual(1, test_data.output.regs['R0'])
