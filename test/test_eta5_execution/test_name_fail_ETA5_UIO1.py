from test.test_eta5_execution import NameGeneral


class NameFailETA5(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_no_name_ETA5420(self) -> None:
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5420.9', test_data.output.last_line)
        self.assertIn("NEED NAME IN PNR TO COMPLETE TRANSACTION", test_data.output.messages)

    def test_too_many_names_ETA5430(self) -> None:
        self.test_data.add_pnr_element(['45ZAVERI', '55SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5430', test_data.output.last_line)
        self.assertIn("MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR", test_data.output.messages)
        self.assertEqual(100, test_data.output.regs['R15'])
        self.assertEqual(f'{self.ui2098:02X}', test_data.field('UI2CNN'))

    def test_too_many_infants_ETA5430(self) -> None:
        self.test_data.add_pnr_element(['45ZAVERI', 'I/55ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5430', test_data.output.last_line)
        self.assertIn("MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR", test_data.output.messages)
        self.assertEqual(100, test_data.output.regs['R15'])
        self.assertEqual(f'{self.ui2098:02X}', test_data.field('UI2CNN'))


class NameFailUIO1(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_group_overbooking_UIO1(self):
        self.test_data.add_pnr_element(['C/5TOURS', '11ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', test_data.output.last_line)
        self.assertEqual('20', test_data.field('WA0ET4'))
        self.assertEqual(bytes([self.ui2xui + self.ui2can, self.ui2nxt, self.ui2nxt]).hex().upper(),
                         test_data.field('UI2INC'))
        # self.assertTrue(TD.state.vm.all_bits_off(TD.state.regs.R1 + self.wa0et5, 0x02))
        self.assertEqual(f'{self.wa0any:02X}', test_data.field('WA0ET5'))
        self.assertEqual(f'{self.ui2214:02X}', test_data.field('UI2CNN'))
        self.assertEqual('60', test_data.field('EBRS01'))

    def test_multiple_groups_CC_UIO1(self):
        self.test_data.add_pnr_element(['C/25SABRE', 'C/21TOURS', '1SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', test_data.output.last_line)
        self.assertEqual(f'{self.wa0any:02X}', test_data.field('WA0ET5'))
        self.assertEqual(f'{self.ui2097:02X}', test_data.field('UI2CNN'))
        self.assertEqual('C3', test_data.field('EBW014'))

    def test_multiple_groups_ZC_UIO1(self):
        self.test_data.add_pnr_element(['Z/25SABRE', 'C/21TOURS', '1SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', test_data.output.last_line)
        self.assertEqual(f'{self.wa0any:02X}', test_data.field('WA0ET5'))
        self.assertEqual(f'{self.ui2097:02X}', test_data.field('UI2CNN'))
        self.assertEqual('E9', test_data.field('EBW014'))
