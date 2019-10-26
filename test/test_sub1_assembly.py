import unittest

from test.input_td import TD
from utils.data_type import DataType


class Sub1Test(unittest.TestCase):
    def setUp(self) -> None:
        TD.state.init_run()

    def test_b4t0(self):
        label = TD.state.run('TS22')
        self.assertEqual('TS22EXIT.1', label)
        self.assertEqual(0, TD.state.regs.R0)
        self.assertEqual(0x017F, TD.state.vm.get_value(TD.ebw000 + 8, 3))
        self.assertEqual('B4T', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebw000, 3)).decode)
        self.assertEqual('B4T0 ', DataType('X', bytes=TD.state.vm.get_bytes(TD.ebw000 + 3, 5)).decode)


# noinspection PyPep8Naming
def tearDownModule():
    if 'SUB1' in TD.state.DEBUG.seg_list:
        with open('trace_log.txt', 'w') as trace_log:
            trace_log.write('\n'.join([str(trace) for trace in TD.state.DEBUG.get_no_hit()]))
    return


if __name__ == '__main__':
    unittest.main()
