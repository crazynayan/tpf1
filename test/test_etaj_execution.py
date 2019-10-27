import unittest

from config import config
from db.pnr import Pnr
from test.input_td import TD
from utils.data_type import DataType


class EtajTest(unittest.TestCase):
    def setUp(self) -> None:
        Pnr.init_db()
        TD.state.init_run()

    def test_branch_validation_fail(self):
        # When no IY records
        Pnr.add_group_plan(config.AAAPNR, ['BTS-B4T0/108/11-FINANCIAL SERVICES'])
        TD.state.setup.aaa['WA0POR'] = DataType('X', input='006F2F').to_bytes()
        TD.state.setup.aaa['WA0FNS'] = bytearray([TD.wa0tvl])
        label = TD.state.run('TS21', aaa=True)
        self.assertEqual('$$ETK4$$.1', label)
        self.assertEqual(8, TD.state.regs.R6)


# noinspection PyPep8Naming
def tearDownModule():
    if 'ETAJ' in TD.state.DEBUG.seg_list:
        with open('trace_log.txt', 'w') as trace_log:
            trace_log.write('\n'.join([str(trace) for trace in TD.state.DEBUG.get_no_hit()]))
    return


if __name__ == '__main__':
    unittest.main()
