from test.test_eta5_execution import NameGeneral
from utils.errors import PackExecutionError


class NameFailETA2(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_invalid_name_ETA2(self) -> None:
        # Without number in party at start
        self._setup_names(['ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', self.output.last_line)
        self.assertIn('19000', self.output.dumps)
        self.assertEqual(1, self.output.regs['R1'])

    def test_invalid_name_after_group_ETA2(self):
        self._setup_names(['Z/25SABRE', 'ZAVERI', '1SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', self.output.last_line)
        self.assertIn('19000', self.output.dumps)
        self.assertEqual(1, self.output.regs['R1'])

    def test_invalid_name_high_after_group_ETA2(self):
        self._setup_names(['Z/25SABRE', chr(0xDB) + 'ZAVERI', '1SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', self.output.last_line)
        self.assertIn('19000', self.output.dumps)
        self.assertEqual(1, self.output.regs['R1'])

    def test_invalid_infant_less_ETA2(self) -> None:
        self._setup_names(['I/ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', self.output.last_line)
        self.assertIn('19000', self.output.dumps)
        self.assertEqual(1, self.output.regs['R1'])

    def test_invalid_infant_high_ETA2(self) -> None:
        # Without number in party at start
        self._setup_names(['I/' + chr(0xDB) + 'TOURS'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', self.output.last_line)
        self.assertIn('19000', self.output.dumps)
        self.assertEqual(1, self.output.regs['R1'])

    def test_invalid_infant_after_adult_ETA2(self) -> None:
        self._setup_names(['1ZAVERI', 'I/ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', self.output.last_line)
        self.assertIn('19000', self.output.dumps)
        self.assertEqual(1, self.output.regs['R1'])

    def test_invalid_infant_after_group_ETA2(self) -> None:
        self._setup_names(['C/21TOURS', 'I/ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', self.output.last_line)
        self.assertIn('19000', self.output.dumps)
        self.assertEqual(1, self.output.regs['R1'])


class NameFailETA3(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_name_error_ETA3(self) -> None:
        self._setup_names(['1ZAVERI'])
        self.test_data.errors.append('ETA5090.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA3$$.1', self.output.last_line)


class NameFailException(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_invalid_group_at_start_Exception(self):
        # Both C/ and Z/ will give an exception.
        # I/ will NOT give an exception.
        self._setup_names(['Z/SABRE', '1ZAVERI'])
        self.assertRaises(PackExecutionError, self.tpf_server.run, 'ETA5', self.test_data)

    def test_invalid_group_C_not_at_start_Exception(self):
        # Preceding adult for invalid C/  will give an exception.
        # Preceding adult for invalid Z/ will NOT give an exception.
        self._setup_names(['1ZAVERI', 'C/TOURS'])
        self.assertRaises(PackExecutionError, self.tpf_server.run, 'ETA5', self.test_data)
