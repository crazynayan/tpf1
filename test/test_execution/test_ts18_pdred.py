import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS


class PdredNames(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()

    def test_multiple_names(self):
        self.test_data.add_pnr_element(['C/21TOURS', '2ZAVERI', 'I/2ZAVERI/S'], 'name')
        test_data = self.tpf_server.run('TS18', self.test_data)
        self.assertEqual(list(), test_data.output.messages)
        self.assertEqual(25, test_data.output.regs['R1'])

    def test_multiple_corporate(self):
        self.test_data.add_pnr_element(['C/21TOURS', '2ZAVERI', 'I/2ZAVERI/S', 'C/21VEENA TOURS'], 'name')
        test_data = self.tpf_server.run('TS18', self.test_data)
        self.assertIn("MORE THAN 1 C/", test_data.output.messages)
        self.assertEqual(0, test_data.output.regs['R1'])

    def test_100_names(self):
        # Check for > 99 names
        self.test_data.add_pnr_element(['55ZAVERI', '45SHAH'], 'name')
        test_data = self.tpf_server.run('TS18', self.test_data)
        self.assertIn("MORE THAN 99 NAMES", test_data.output.messages)
        self.assertEqual(100, test_data.output.regs['R1'])


if __name__ == '__main__':
    unittest.main()
