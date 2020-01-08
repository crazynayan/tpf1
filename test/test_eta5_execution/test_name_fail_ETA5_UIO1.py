from test.test_eta5_execution import NameGeneral


class NameFailETA5(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_no_name_ETA5420(self) -> None:
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5420.9', self.output.last_line)
        self.assertIn("NEED NAME IN PNR TO COMPLETE TRANSACTION", self.output.messages)

    def test_too_many_names_ETA5430(self) -> None:
        self.test_data.add_pnr_from_data(['45ZAVERI', '55SHAH'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5430', self.output.last_line)
        self.assertIn("MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR", self.output.messages)
        self.assertEqual(100, self.output.regs['R15'])
        self.assertEqual(f'{self.ui2098:02X}', self.test_data.hex(self.o_ui2['UI2CNN']['data']))

    def test_too_many_infants_ETA5430(self) -> None:
        self.test_data.add_pnr_from_data(['45ZAVERI', 'I/55ZAVERI'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETA5430', self.output.last_line)
        self.assertIn("MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR", self.output.messages)
        self.assertEqual(100, self.output.regs['R15'])
        self.assertEqual(f'{self.ui2098:02X}', self.test_data.hex(self.o_ui2['UI2CNN']['data']))


class NameFailUIO1(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_group_overbooking_UIO1(self):
        self.test_data.add_pnr_from_data(['C/5TOURS', '11ZAVERI'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', self.output.last_line)
        self.assertEqual('20', self.test_data.hex(self.o_aaa['WA0ET4']['data']))
        self.assertEqual(bytes([self.ui2xui + self.ui2can, self.ui2nxt, self.ui2nxt]).hex().upper(),
                         self.test_data.hex(self.o_ui2['UI2INC']['data']))
        # self.assertTrue(TD.state.vm.all_bits_off(TD.state.regs.R1 + self.wa0et5, 0x02))
        self.assertEqual(f'{self.wa0any:02X}', self.test_data.hex(self.o_aaa['WA0ET5']['data']))
        self.assertEqual(f'{self.ui2214:02X}', self.test_data.hex(self.o_ui2['UI2CNN']['data']))
        self.assertEqual('60', self.test_data.hex(self.o_ecb['EBRS01']['data']))

    def test_multiple_groups_CC_UIO1(self):
        self.test_data.add_pnr_from_data(['C/25SABRE', 'C/21TOURS', '1SHAH'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', self.output.last_line)
        self.assertEqual(f'{self.wa0any:02X}', self.test_data.hex(self.o_aaa['WA0ET5']['data']))
        self.assertEqual(f'{self.ui2097:02X}', self.test_data.hex(self.o_ui2['UI2CNN']['data']))
        self.assertEqual('C3', self.test_data.hex(self.o_ecb['EBW014']['data']))

    def test_multiple_groups_ZC_UIO1(self):
        self.test_data.add_pnr_from_data(['Z/25SABRE', 'C/21TOURS', '1SHAH'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$UIO1$$.1', self.output.last_line)
        self.assertEqual(f'{self.wa0any:02X}', self.test_data.hex(self.o_aaa['WA0ET5']['data']))
        self.assertEqual(f'{self.ui2097:02X}', self.test_data.hex(self.o_ui2['UI2CNN']['data']))
        self.assertEqual('E9', self.test_data.hex(self.o_ecb['EBW014']['data']))
