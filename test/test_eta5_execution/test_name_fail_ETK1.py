from base64 import b64encode

from test.test_eta5_execution import NameGeneral


class NameFailETK1(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_no_name_tty_ETK1_33(self) -> None:
        self.i_aaa['WA0ET4']['data'] = b64encode(bytes([self.wa0tty])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertEqual('00', test_data.field('UI2CNN'))
        self.assertEqual('60', test_data.field('EBRS01'))
        self.assertEqual(33, test_data.output.regs['R6'])

    def test_too_many_names_tty_ETK1_33(self) -> None:
        self.test_data.add_pnr_element(['45ZAVERI', '55SHAH'], 'name')
        self.i_aaa['WA0ET4']['data'] = b64encode(bytes([self.wa0tty])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertEqual(100, test_data.output.regs['R15'])
        self.assertEqual(f'{self.ui2098:02X}', test_data.field('UI2CNN'))
        self.assertEqual(33, test_data.output.regs['R6'])
        self.assertEqual('60', test_data.field('EBRS01'))

    def test_group_overbooking_tty_ETK1_33(self):
        self.test_data.add_pnr_element(['Z/15SABRE', '11ZAVERI', '5SHAH'], 'name')
        self.i_aaa['WA0ET4']['data'] = b64encode(bytes([self.wa0tty])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertEqual(33, test_data.output.regs['R6'])
        self.assertEqual('60', test_data.field('EBRS01'))

    def test_multiple_groups_CC_tty_ETK1_33(self):
        self.test_data.add_pnr_element(['C/25TOURS', 'C/21TOURS', '1SHAH'], 'name')
        self.i_aaa['WA0ET4']['data'] = b64encode(bytes([self.wa0tty])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual(f'{self.ui2097:02X}', test_data.field('UI2CNN'))
        self.assertEqual(33, test_data.output.regs['R6'])
        self.assertEqual('60', test_data.field('EBRS01'))
        self.assertEqual('C3', test_data.field('EBW014'))

    def test_multiple_groups_ZC_tty_ETK1_33(self):
        self.test_data.add_pnr_element(['Z/25SABRE', 'C/21TOURS', '1SHAH'], 'name')
        self.i_aaa['WA0ET4']['data'] = b64encode(bytes([self.wa0tty])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual(f'{self.ui2097:02X}', test_data.field('UI2CNN'))
        self.assertEqual(33, test_data.output.regs['R6'])
        self.assertEqual('60', test_data.field('EBRS01'))
        self.assertEqual('E9', test_data.field('EBW014'))

    def test_multiple_groups_CZ_tty_ETK1_16(self):
        self.test_data.add_pnr_element(['C/25TOURS', 'Z/21SABRE', '1SHAH'], 'name')
        self.i_aaa['WA0ET4']['data'] = b64encode(bytes([self.wa0tty])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual(f'{self.ui2098:02X}', test_data.field('UI2CNN'))
        self.assertEqual(16, test_data.output.regs['R6'])
        self.assertEqual('E0', test_data.field('EBRS01'))
        self.assertEqual('C3', test_data.field('EBW014'))

    def test_multiple_groups_ZZ_tty_ETK1_16(self):
        self.test_data.add_pnr_element(['Z/25SABRE', 'Z/21SABRE', '1SHAH'], 'name')
        self.i_aaa['WA0ET4']['data'] = b64encode(bytes([self.wa0tty])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual(f'{self.ui2098:02X}', test_data.field('UI2CNN'))
        self.assertEqual(16, test_data.output.regs['R6'])
        self.assertEqual('E0', test_data.field('EBRS01'))
        self.assertEqual('E9', test_data.field('EBW014'))

    def test_invalid_type_ETK1_16(self):
        self.test_data.add_pnr_element(['K/13TOURS', '1ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertEqual(16, test_data.output.regs['R6'])
        self.assertEqual('E0', test_data.field('EBRS01'))
        self.assertEqual('D2', test_data.field('EBW014'))

    def test_group_Z_not_at_start_ETK1_16(self):
        # It will give the same error if number of party is mentioned in Z/
        self.test_data.add_pnr_element(['3ZAVERI', 'Z/SABRE', '1SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertEqual(16, test_data.output.regs['R6'])
        self.assertEqual('E0', test_data.field('EBRS01'))
        self.assertEqual('00', test_data.field('EBW014'))

    def test_multiple_groups_ZZ_ETK1_16(self):
        self.test_data.add_pnr_element(['Z/25SABRE', 'Z/21TOURS', '1SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertEqual(16, test_data.output.regs['R6'])
        self.assertEqual('E0', test_data.field('EBRS01'))
        self.assertEqual('E9', test_data.field('EBW014'))

    def test_multiple_groups_CZ_ETK1_16(self):
        self.test_data.add_pnr_element(['C/25SABRE', 'Z/21TOURS', '1SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', test_data.output.last_line)
        self.assertEqual(16, test_data.output.regs['R6'])
        self.assertEqual('E0', test_data.field('EBRS01'))
        self.assertEqual('C3', test_data.field('EBW014'))
