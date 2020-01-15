from test.test_eta5_execution import NameGeneral


class NameFailETA2(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_invalid_name_ETA2(self) -> None:
        # Without number in party at start
        self.test_data.add_pnr_element(['ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', test_data.output.last_line)
        self.assertIn('19000', test_data.output.dumps)
        self.assertEqual(1, test_data.output.regs['R1'])

    def test_invalid_name_after_group_ETA2(self):
        self.test_data.add_pnr_element(['Z/25SABRE', 'ZAVERI', '1SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', test_data.output.last_line)
        self.assertIn('19000', test_data.output.dumps)
        self.assertEqual(1, test_data.output.regs['R1'])

    def test_invalid_name_high_after_group_ETA2(self):
        self.test_data.add_pnr_element(['Z/25SABRE', chr(0xDB) + 'ZAVERI', '1SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', test_data.output.last_line)
        self.assertIn('19000', test_data.output.dumps)
        self.assertEqual(1, test_data.output.regs['R1'])

    def test_invalid_infant_less_ETA2(self) -> None:
        self.test_data.add_pnr_element(['I/ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', test_data.output.last_line)
        self.assertIn('19000', test_data.output.dumps)
        self.assertEqual(1, test_data.output.regs['R1'])

    def test_invalid_infant_high_ETA2(self) -> None:
        # Without number in party at start
        self.test_data.add_pnr_element(['I/' + chr(0xDB) + 'TOURS'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', test_data.output.last_line)
        self.assertIn('19000', test_data.output.dumps)
        self.assertEqual(1, test_data.output.regs['R1'])

    def test_invalid_infant_after_adult_ETA2(self) -> None:
        self.test_data.add_pnr_element(['1ZAVERI', 'I/ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', test_data.output.last_line)
        self.assertIn('19000', test_data.output.dumps)
        self.assertEqual(1, test_data.output.regs['R1'])

    def test_invalid_infant_after_group_ETA2(self) -> None:
        self.test_data.add_pnr_element(['C/21TOURS', 'I/ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', test_data.output.last_line)
        self.assertIn('19000', test_data.output.dumps)
        self.assertEqual(1, test_data.output.regs['R1'])


class NameFailETA3(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_name_error_ETA3(self) -> None:
        self.test_data.add_pnr_element(['1ZAVERI'], 'name')
        self.test_data.errors.append('ETA5090.1')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA3$$.1', test_data.output.last_line)


class NameFailException(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_invalid_group_at_start_Exception(self):
        # Both C/ and Z/ will give an exception.
        # I/ will NOT give an exception.
        self.test_data.add_pnr_element(['Z/SABRE', '1ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertIn('000003', test_data.output.dumps)
        self.assertIn('EXECUTION ERROR', test_data.output.messages)

    def test_invalid_group_C_not_at_start_Exception(self):
        # Preceding adult for invalid C/  will give an exception.
        # Preceding adult for invalid Z/ will NOT give an exception.
        self.test_data.add_pnr_element(['1ZAVERI', 'C/TOURS'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertIn('000003', test_data.output.dumps)
        self.assertIn('EXECUTION ERROR', test_data.output.messages)
