from base64 import b64encode

from test.test_eta5_execution import NameGeneral


class NameSuccessETAW(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_single_name_wa0pty_no_match_ETAW(self) -> None:
        self.test_data.add_pnr_element(['1ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F0F0', test_data.field('WA0EXT'))
        self.assertEqual('01', test_data.field('WA0PTY'))
        self.assertEqual('01', test_data.field('EBW015'))
        self.assertEqual(f'{self.ui2214:02X}', test_data.field('UI2CNN'))

    def test_multiple_names_wa0pty_match_ETAW(self) -> None:
        self.test_data.add_pnr_element(['45ZAVERI', '54SHAH'], 'name')
        self.i_aaa['WA0PTY']['data'] = b64encode(bytearray([99])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F0F0', test_data.field('WA0EXT'))
        self.assertEqual(f'{99:02X}', test_data.field('WA0PTY'))
        self.assertEqual(f'{99:02X}', test_data.field('EBW015'))
        self.assertEqual(f'{self.ui2214:02X}', test_data.field('UI2CNN'))

    def test_WA0NAD_ETAW(self) -> None:
        self.test_data.add_pnr_element(['1ZAVERI', '3SHAH'], 'name')
        self.i_aaa['WA0ETG']['data'] = b64encode(bytearray([self.wa0nad])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F0F0', test_data.field('WA0EXT'))
        self.assertEqual('04', test_data.field('WA0PTY'))
        self.assertEqual('04', test_data.field('EBW015'))
        self.assertEqual(f'{self.ui2214:02X}', test_data.field('UI2CNN'))
        self.assertEqual('00', test_data.field('WA0ETG'))  # WA0ETG, #WA0NAD
        self.assertEqual(7,
                         test_data.output.regs['R6'])  # Call to ETK2 with R6=7 will ensure Name association is deleted

    def test_WA0CDI_ETAW(self) -> None:
        self.test_data.add_pnr_element(['33ZAVERI'], 'name')
        self.i_aaa['WA0US4']['data'] = b64encode(bytearray([self.wa0cdi])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F0F0', test_data.field('WA0EXT'))
        self.assertEqual(f'{33:02X}', test_data.field('WA0PTY'))
        self.assertEqual(f'{33:02X}', test_data.field('EBW015'))
        self.assertEqual(60, test_data.output.regs['R6'])

    def test_group_C_ETAW(self) -> None:
        self.test_data.add_pnr_element(['C/21TOURS', '2ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F1F9', test_data.field('WA0EXT'))
        self.assertEqual(f'{21:02X}', test_data.field('WA0PTY'))
        self.assertEqual(f'{21:02X}', test_data.field('EBW015'))
        self.assertEqual('C3', test_data.field('EBW014'))
        self.assertEqual('80', test_data.field('EBW038'))
        self.assertEqual('10', test_data.field('EBSW01'))

    def test_group_Z_ETAW_wa0pyt_no_match(self) -> None:
        self.test_data.add_pnr_element(['Z/25SABRE', '3SHAH'], 'name')
        self.i_aaa['WA0PTY']['data'] = b64encode(bytearray([3])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F2F2', test_data.field('WA0EXT'))
        self.assertEqual(f'{25:02X}', test_data.field('WA0PTY'))
        self.assertEqual(f'{25:02X}', test_data.field('EBW015'))
        self.assertEqual('E9', test_data.field('EBW014'))
        self.assertEqual('80', test_data.field('EBW038'))
        self.assertEqual('10', test_data.field('EBSW01'))

    def test_group_C_not_at_start_wa0pty_history_no_match_ETAW(self):
        self.test_data.add_pnr_element(['10ZAVERI', 'C/21TOURS', '1SHAH'], 'name')
        self.i_aaa['WA0PTY']['data'] = b64encode(bytearray([0xE3])).decode()  # 99 = 0x63 with bit0 on is 0xE3
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F1F0', test_data.field('WA0EXT'))
        self.assertEqual('C3', test_data.field('EBW014'))
        self.assertEqual('95', test_data.field('WA0PTY'))  # 0x15 with bit0 on
        self.assertEqual('15', test_data.field('EBW015'))  # 21 = 0x15

    def test_pn2_on_group_9_C_ETAW(self):
        self.test_data.add_pnr_element(['C/99W/TOURS', '3SHAH'], 'name')
        self.i_aaa['WA0UB1']['data'] = b64encode(bytearray([self.wa0pn2])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertEqual('F0F6', test_data.field('WA0EXT'))
        self.assertEqual('09', test_data.field('WA0PTY'))
        self.assertEqual('09', test_data.field('EBW015'))

    def test_pn2_on_group_99_C_ETAW(self):
        self.test_data.add_pnr_element(['C/999W/TOURS', '3SHAH'], 'name')
        self.i_aaa['WA0UB1']['data'] = b64encode(bytearray([self.wa0pn2])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertEqual('F9F6', test_data.field('WA0EXT'))
        self.assertEqual(f'{99:02X}', test_data.field('WA0PTY'))
        self.assertEqual(f'{99:02X}', test_data.field('EBW015'))

    def test_pn2_on_group_Z_wa0pty_history_match_ETAW(self):
        # T.wa0PN2 OFF behaves the same way
        self.test_data.add_pnr_element(['Z/99W/SABRE', '3SHAH'], 'name')
        self.i_aaa['WA0UB1']['data'] = b64encode(bytearray([self.wa0pn2])).decode()
        self.i_aaa['WA0PTY']['data'] = b64encode(bytearray([0xE3])).decode()  # 99 = 0x63 with bit0 on is 0xE3
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertEqual('F9F6', test_data.field('WA0EXT'))
        self.assertEqual('E3', test_data.field('WA0PTY'))
        self.assertEqual(f'{99:02X}', test_data.field('EBW015'))

    def test_pn2_off_group_wa0pti_ETAW(self):
        self.test_data.add_pnr_element(['C/99W/TOURS', '3SHAH'], 'name')
        self.i_aaa['WA0UB1']['data'] = b64encode(bytearray([0x00])).decode()
        self.i_aaa['WA0PTI']['data'] = b64encode(bytearray([0x03])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertIn('021014', test_data.output.dumps)
        self.assertEqual('F9F6', test_data.field('WA0EXT'))
        self.assertEqual(f'{99:02X}', test_data.field('EBW015'))
        self.assertEqual(f'{99:02X}', test_data.field('WA0PTY'))
        self.assertEqual('00', test_data.field('WA0PTI'))

    def test_infant_with_adults_ETAW(self):
        self.test_data.add_pnr_element(['2ZAVERI', 'I/1ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertIn('021014', test_data.output.dumps)
        self.assertEqual('F0F0', test_data.field('WA0EXT'))
        self.assertEqual('03', test_data.field('EBW015'))
        self.assertEqual('03', test_data.field('WA0PTY'))
        self.assertEqual('01', test_data.field('EBW010'))
        self.assertEqual('01', test_data.field('WA0PTI'))

    def test_infant_only_ETAW(self):
        self.test_data.add_pnr_element(['I/3ZAVERI'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertIn('021014', test_data.output.dumps)
        self.assertEqual('F0F3', test_data.field('WA0EXT'))
        self.assertEqual('03', test_data.field('EBW015'))
        self.assertEqual('03', test_data.field('WA0PTY'))
        self.assertEqual('03', test_data.field('EBW010'))
        self.assertEqual('03', test_data.field('WA0PTI'))

    def test_infant_at_start_with_less_adults_ETAW(self):
        self.test_data.add_pnr_element(['I/33ZAVERI', '44ZAVERI', 'I/22SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertIn('021014', test_data.output.dumps)
        self.assertEqual('F0F0', test_data.field('WA0EXT'))
        self.assertEqual(f'{99:02X}', test_data.field('EBW015'))
        self.assertEqual(f'{99:02X}', test_data.field('WA0PTY'))
        self.assertEqual(f'{55:02X}', test_data.field('EBW010'))
        self.assertEqual(f'{55:02X}', test_data.field('WA0PTI'))

    def test_infant_with_group_wa0pti_ETAW(self):
        self.test_data.add_pnr_element(['Z/21SABRE', '3ZAVERI', 'I/1ZAVERI', '4SHAH', 'I/2SHAH'], 'name')
        self.i_aaa['WA0PTI']['data'] = b64encode(bytearray([0x03])).decode()
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F1F4', test_data.field('WA0EXT'))
        self.assertEqual(f'{24:02X}', test_data.field('EBW015'))
        self.assertEqual(f'{24:02X}', test_data.field('WA0PTY'))
        self.assertEqual('03', test_data.field('EBW010'))
        self.assertEqual('03', test_data.field('WA0PTI'))

    def test_infant_at_start_with_group_ETAW(self):
        self.test_data.add_pnr_element(['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'], 'name')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', test_data.output.last_line)
        self.assertIn('021014', test_data.output.dumps)
        self.assertEqual('F1F6', test_data.field('WA0EXT'))
        self.assertEqual(f'{32:02X}', test_data.field('EBW015'))
        self.assertEqual(f'{32:02X}', test_data.field('WA0PTY'))
        self.assertEqual('07', test_data.field('EBW010'))
        self.assertEqual('07', test_data.field('WA0PTI'))
        self.assertEqual('00', test_data.field('EBW016'))
