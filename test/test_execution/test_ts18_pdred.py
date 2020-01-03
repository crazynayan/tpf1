import unittest

from execution.ex5_execute import Execute
from test import TestDataUTS


class PdredNames(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = TestDataUTS()
        self.output = self.test_data.output
        self.output.add_regs(['R1'])

    def test_multiple_names(self):
        self.test_data.add_pnr_from_data(['C/21TOURS', '2ZAVERI', 'I/2ZAVERI/S'], 'name')
        self.tpf_server.run('TS18', self.test_data)
        self.assertEqual(list(), self.output.messages)
        self.assertEqual(25, self.output.regs['R1'])

    def test_multiple_corporate(self):
        self.test_data.add_pnr_from_data(['C/21TOURS', '2ZAVERI', 'I/2ZAVERI/S', 'C/21VEENA TOURS'], 'name')
        self.tpf_server.run('TS18', self.test_data)
        self.assertIn("MORE THAN 1 C/", self.output.messages)
        self.assertEqual(0, self.output.regs['R1'])

    def test_100_names(self):
        # Check for > 99 names
        self.test_data.add_pnr_from_data(['55ZAVERI', '45SHAH'], 'name')
        self.tpf_server.run('TS18', self.test_data)
        self.assertIn("MORE THAN 99 NAMES", self.output.messages)
        self.assertEqual(100, self.output.regs['R1'])


if __name__ == '__main__':
    unittest.main()
