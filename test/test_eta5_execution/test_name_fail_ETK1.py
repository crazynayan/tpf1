from base64 import b64encode, b64decode

from test.input_td import TD
from test.test_eta5_execution import NameGeneral


class NameFailETK1(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_no_name_tty_ETK1_33(self) -> None:
        self.i_aaa['WA0ET4'].data = b64encode(bytes([TD.wa0tty])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertEqual('00', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual('60', self._o_ecb('EBRS01'))
        self.assertEqual(33, self.output.regs['R6'])

    def test_too_many_names_tty_ETK1_33(self) -> None:
        self._setup_names(['45ZAVERI', '55SHAH'])
        self.i_aaa['WA0ET4'].data = b64encode(bytes([TD.wa0tty])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertEqual(100, self.output.regs['R15'])
        self.assertEqual(f'{TD.ui2098:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual(33, self.output.regs['R6'])
        self.assertEqual('60', self._o_ecb('EBRS01'))

    def test_group_overbooking_tty_ETK1_33(self):
        self._setup_names(['Z/15SABRE', '11ZAVERI', '5SHAH'])
        self.i_aaa['WA0ET4'].data = b64encode(bytes([TD.wa0tty])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertEqual(33, self.output.regs['R6'])
        self.assertEqual('60', self._o_ecb('EBRS01'))

    def test_multiple_groups_CC_tty_ETK1_33(self):
        self._setup_names(['C/25TOURS', 'C/21TOURS', '1SHAH'])
        self.i_aaa['WA0ET4'].data = b64encode(bytes([TD.wa0tty])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertListEqual(list(), TD.state.dumps)
        self.assertEqual(f'{TD.ui2097:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual(33, self.output.regs['R6'])
        self.assertEqual('60', self._o_ecb('EBRS01'))
        self.assertEqual('C3', self._o_ecb('EBW014'))

    def test_multiple_groups_ZC_tty_ETK1_33(self):
        self._setup_names(['Z/25SABRE', 'C/21TOURS', '1SHAH'])
        self.i_aaa['WA0ET4'].data = b64encode(bytes([TD.wa0tty])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertListEqual(list(), TD.state.dumps)
        self.assertEqual(f'{TD.ui2097:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual(33, self.output.regs['R6'])
        self.assertEqual('60', self._o_ecb('EBRS01'))
        self.assertEqual('E9', self._o_ecb('EBW014'))

    def test_multiple_groups_CZ_tty_ETK1_16(self):
        self._setup_names(['C/25TOURS', 'Z/21SABRE', '1SHAH'])
        self.i_aaa['WA0ET4'].data = b64encode(bytes([TD.wa0tty])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertListEqual(list(), TD.state.dumps)
        self.assertEqual(f'{TD.ui2098:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual(16, self.output.regs['R6'])
        self.assertEqual('E0', self._o_ecb('EBRS01'))
        self.assertEqual('C3', self._o_ecb('EBW014'))

    def test_multiple_groups_ZZ_tty_ETK1_16(self):
        self._setup_names(['Z/25SABRE', 'Z/21SABRE', '1SHAH'])
        self.i_aaa['WA0ET4'].data = b64encode(bytes([TD.wa0tty])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertListEqual(list(), TD.state.dumps)
        self.assertEqual(f'{TD.ui2098:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual(16, self.output.regs['R6'])
        self.assertEqual('E0', self._o_ecb('EBRS01'))
        self.assertEqual('E9', self._o_ecb('EBW014'))

    def test_invalid_type_ETK1_16(self):
        self._setup_names(['K/13TOURS', '1ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertEqual(16, self.output.regs['R6'])
        self.assertEqual('E0', self._o_ecb('EBRS01'))
        self.assertEqual('D2', self._o_ecb('EBW014'))

    def test_group_Z_not_at_start_ETK1_16(self):
        # It will give the same error if number of party is mentioned in Z/
        self._setup_names(['3ZAVERI', 'Z/SABRE', '1SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertEqual(16, self.output.regs['R6'])
        self.assertEqual('E0', self._o_ecb('EBRS01'))
        self.assertEqual('00', self._o_ecb('EBW014'))

    def test_multiple_groups_ZZ_ETK1_16(self):
        self._setup_names(['Z/25SABRE', 'Z/21TOURS', '1SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertEqual(16, self.output.regs['R6'])
        self.assertEqual('E0', self._o_ecb('EBRS01'))
        self.assertEqual('E9', self._o_ecb('EBW014'))

    def test_multiple_groups_CZ_ETK1_16(self):
        self._setup_names(['C/25SABRE', 'Z/21TOURS', '1SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETK1$$.1', self.output.last_line)
        self.assertEqual(16, self.output.regs['R6'])
        self.assertEqual('E0', self._o_ecb('EBRS01'))
        self.assertEqual('C3', self._o_ecb('EBW014'))
