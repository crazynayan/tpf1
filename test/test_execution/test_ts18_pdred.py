import unittest

from config import config
from db.pnr import Pnr
from test.input_td import TD


class PdredNames(unittest.TestCase):
    def setUp(self) -> None:
        TD.state.init_run()
        Pnr.init_db()

    def test_pdred_ts18(self):
        names = ['C/21TOURS', '2ZAVERI', 'I/2ZAVERI/S']
        Pnr.add_names(config.AAAPNR, names)
        TD.state.run('TS18', aaa=True)
        self.assertIsNone(TD.state.message)
        self.assertEqual(25, TD.state.regs.R1)
        # Check for another corporate
        Pnr.add_names(config.AAAPNR, ['C/21VEENA TOURS'])
        TD.state.restart('TS18', aaa=True)
        self.assertEqual("'MORE THAN 1 C/'", TD.state.message)
        self.assertEqual(0, TD.state.regs.R1)
        # Check for > 99 names
        names = ['55ZAVERI', '45SHAH']
        Pnr.init_db()
        Pnr.add_names(config.AAAPNR, names)
        TD.state.restart('TS18', aaa=True)
        self.assertEqual("'MORE THAN 99 NAMES'", TD.state.message)
        self.assertEqual(100, TD.state.regs.R1)


if __name__ == '__main__':
    unittest.main()
