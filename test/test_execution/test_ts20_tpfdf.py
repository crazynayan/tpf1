import unittest

from db.pnr import Pnr
from db.tpfdf import Tpfdf
from test.input_td import TD


class DbTest(unittest.TestCase):
    def setUp(self) -> None:
        TD.state.init_run()
        Pnr.init_db()

    def test_tpfdf_ts20(self):
        Tpfdf.add(TD.tr1gaa, 'TR1GAA', '40')
        TD.state.run('TS20', aaa=True)
        self.assertEqual(21, TD.state.regs.R0)
        self.assertEqual(0x80, TD.state.vm.get_byte(TD.state.regs.R5 + 5))


if __name__ == '__main__':
    unittest.main()
