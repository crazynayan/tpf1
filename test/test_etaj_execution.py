import unittest

from db.pnr import Pnr
from test.input_td import TD


class EtajTest(unittest.TestCase):
    def setUp(self) -> None:
        Pnr.init_db()
        TD.state.init_run()

    def test_branch_validation_fail(self):
        # Pnr.add_group_plan(config.AAAPNR, ['BTS-B4T0/108/11-FINANCIAL SERVICES'])
        label = TD.state.run('TS21', aaa=True)
        self.assertEqual('TS21EXIT.1', label)


# noinspection PyPep8Naming
def tearDownModule():
    if 'ETAJ' in TD.state.DEBUG.seg_list:
        with open('trace_log.txt', 'w') as trace_log:
            trace_log.write('\n'.join([str(trace) for trace in TD.state.DEBUG.get_no_hit()]))
    return


if __name__ == '__main__':
    unittest.main()
