import unittest

from config import config
from db.pnr import Pnr
from utils.test_data import T


class PdredNames(unittest.TestCase):
    def setUp(self) -> None:
        T.state.init_run()
        Pnr.init_db()

    def test_pdred_ts18(self):
        names = ['C/21TOURS', '2ZAVERI', 'I/2ZAVERI/S']
        Pnr.add_names(config.AAAPNR, names)
        T.state.run('TS18', aaa=True)
        self.assertIsNone(T.state.message)
        self.assertEqual(25, T.state.regs.R1)
        # Check for another corporate
        Pnr.add_names(config.AAAPNR, ['C/21VEENA TOURS'])
        T.state.restart('TS18', aaa=True)
        self.assertEqual("'MORE THAN 1 C/'", T.state.message)
        self.assertEqual(0, T.state.regs.R1)
        # Check for > 99 names
        names = ['55ZAVERI', '45SHAH']
        Pnr.init_db()
        Pnr.add_names(config.AAAPNR, names)
        T.state.restart('TS18', aaa=True)
        self.assertEqual("'MORE THAN 99 NAMES'", T.state.message)
        self.assertEqual(100, T.state.regs.R1)


if __name__ == '__main__':
    unittest.main()
