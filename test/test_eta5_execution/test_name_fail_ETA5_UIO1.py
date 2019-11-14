from base64 import b64decode

from test.input_td import TD
from test.test_eta5_execution import NameGeneral


class NameFailETA5(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_no_name_ETA5420(self) -> None:
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5420.9', self.output.last_line)
        self.assertEqual("'NEED NAME IN PNR TO COMPLETE TRANSACTION'", self.output.message)

    def test_too_many_names_ETA5430(self) -> None:
        self._setup_names(['45ZAVERI', '55SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5430', self.output.last_line)
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'", self.output.message)
        self.assertEqual(100, self.output.regs['R15'])
        self.assertEqual(f'{TD.ui2098:02X}', b64decode(self.ui2cnn.data).hex().upper())

    def test_too_many_infants_ETA5430(self) -> None:
        self._setup_names(['45ZAVERI', 'I/55ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5430', self.output.last_line)
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'", self.output.message)
        self.assertEqual(100, self.output.regs['R15'])
        self.assertEqual(f'{TD.ui2098:02X}', b64decode(self.ui2cnn.data).hex().upper())


class NameFailUIO1(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_group_overbooking_UIO1(self):
        self._setup_names(['C/5TOURS', '11ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', self.output.last_line)
        self.assertEqual('20', self._o_aaa('WA0ET4'))
        self.assertEqual(bytes([TD.ui2xui + TD.ui2can, TD.ui2nxt, TD.ui2nxt]), b64decode(self.ui2inc.data))
        # self.assertTrue(TD.state.vm.all_bits_off(TD.state.regs.R1 + TD.wa0et5, 0x02))
        self.assertEqual(f'{TD.wa0any:02X}', self._o_aaa('WA0ET5'))
        self.assertEqual(f'{TD.ui2214:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual('60', self._o_ecb('EBRS01'))

    def test_multiple_groups_CC_UIO1(self):
        self._setup_names(['C/25SABRE', 'C/21TOURS', '1SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', self.output.last_line)
        self.assertEqual(f'{TD.wa0any:02X}', self._o_aaa('WA0ET5'))
        self.assertEqual(f'{TD.ui2097:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual('C3', self._o_ecb('EBW014'))

    def test_multiple_groups_ZC_UIO1(self):
        self._setup_names(['Z/25SABRE', 'C/21TOURS', '1SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', self.output.last_line)
        self.assertEqual(f'{TD.wa0any:02X}', self._o_aaa('WA0ET5'))
        self.assertEqual(f'{TD.ui2097:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual('E9', self._o_ecb('EBW014'))
