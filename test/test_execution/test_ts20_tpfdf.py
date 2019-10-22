import unittest

from db.pnr import Pnr
from db.tpfdf import Tpfdf
from utils.test_data import T


class DbTest(unittest.TestCase):
    def setUp(self) -> None:
        T.state.init_run()
        Pnr.init_db()

    def test_tpfdf_ts20(self):
        Tpfdf.add(T.tr1gaa, 'TR1GAA', '40')
        T.state.run('TS20', aaa=True)
        self.assertEqual(21, T.state.regs.R0)
        self.assertEqual(0x80, T.state.vm.get_byte(T.state.regs.R5 + 5))


if __name__ == '__main__':
    unittest.main()
