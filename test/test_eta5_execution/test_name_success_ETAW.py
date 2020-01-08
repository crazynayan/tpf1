from base64 import b64encode

from test.test_eta5_execution import NameGeneral


class NameSuccessETAW(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_single_name_wa0pty_no_match_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(['1ZAVERI'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual('F0F0', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual('01', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual('01', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual(f'{self.ui2214:02X}', self.test_data.hex(self.o_ui2['UI2CNN']['data']))

    def test_multiple_names_wa0pty_match_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(['45ZAVERI', '54SHAH'], 'name')
        self.i_aaa['WA0PTY']['data'] = b64encode(bytearray([99])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual('F0F0', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual(f'{self.ui2214:02X}', self.test_data.hex(self.o_ui2['UI2CNN']['data']))

    def test_WA0NAD_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(['1ZAVERI', '3SHAH'], 'name')
        self.i_aaa['WA0ETG']['data'] = b64encode(bytearray([self.wa0nad])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual('F0F0', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual('04', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual('04', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual(f'{self.ui2214:02X}', self.test_data.hex(self.o_ui2['UI2CNN']['data']))
        self.assertEqual('00', self.test_data.hex(self.o_aaa['WA0ETG']['data']))  # WA0ETG, #WA0NAD
        self.assertEqual(7, self.output.regs['R6'])  # Call to ETK2 with R6=7 will ensure Name association is deleted

    def test_WA0CDI_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(['33ZAVERI'], 'name')
        self.i_aaa['WA0US4']['data'] = b64encode(bytearray([self.wa0cdi])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual('F0F0', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{33:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual(f'{33:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual(60, self.output.regs['R6'])

    def test_group_C_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(['C/21TOURS', '2ZAVERI'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual('F1F9', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{21:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual(f'{21:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual('C3', self.test_data.hex(self.o_ecb['EBW014']['data']))
        self.assertEqual('80', self.test_data.hex(self.o_ecb['EBW038']['data']))
        self.assertEqual('10', self.test_data.hex(self.o_ecb['EBSW01']['data']))

    def test_group_Z_ETAW_wa0pyt_no_match(self) -> None:
        self.test_data.add_pnr_from_data(['Z/25SABRE', '3SHAH'], 'name')
        self.i_aaa['WA0PTY']['data'] = b64encode(bytearray([3])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual('F2F2', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{25:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual(f'{25:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual('E9', self.test_data.hex(self.o_ecb['EBW014']['data']))
        self.assertEqual('80', self.test_data.hex(self.o_ecb['EBW038']['data']))
        self.assertEqual('10', self.test_data.hex(self.o_ecb['EBSW01']['data']))

    def test_group_C_not_at_start_wa0pty_history_no_match_ETAW(self):
        self.test_data.add_pnr_from_data(['10ZAVERI', 'C/21TOURS', '1SHAH'], 'name')
        self.i_aaa['WA0PTY']['data'] = b64encode(bytearray([0xE3])).decode()  # 99 = 0x63 with bit0 on is 0xE3
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual('F1F0', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual('C3', self.test_data.hex(self.o_ecb['EBW014']['data']))
        self.assertEqual('95', self.test_data.hex(self.o_aaa['WA0PTY']['data']))  # 0x15 with bit0 on
        self.assertEqual('15', self.test_data.hex(self.o_ecb['EBW015']['data']))  # 21 = 0x15

    def test_pn2_on_group_9_C_ETAW(self):
        self.test_data.add_pnr_from_data(['C/99W/TOURS', '3SHAH'], 'name')
        self.i_aaa['WA0UB1']['data'] = b64encode(bytearray([self.wa0pn2])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('F0F6', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual('09', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual('09', self.test_data.hex(self.o_ecb['EBW015']['data']))

    def test_pn2_on_group_99_C_ETAW(self):
        self.test_data.add_pnr_from_data(['C/999W/TOURS', '3SHAH'], 'name')
        self.i_aaa['WA0UB1']['data'] = b64encode(bytearray([self.wa0pn2])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('F9F6', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))

    def test_pn2_on_group_Z_wa0pty_history_match_ETAW(self):
        # T.wa0PN2 OFF behaves the same way
        self.test_data.add_pnr_from_data(['Z/99W/SABRE', '3SHAH'], 'name')
        self.i_aaa['WA0UB1']['data'] = b64encode(bytearray([self.wa0pn2])).decode()
        self.i_aaa['WA0PTY']['data'] = b64encode(bytearray([0xE3])).decode()  # 99 = 0x63 with bit0 on is 0xE3
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('F9F6', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual('E3', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))

    def test_pn2_off_group_wa0pti_ETAW(self):
        self.test_data.add_pnr_from_data(['C/99W/TOURS', '3SHAH'], 'name')
        self.i_aaa['WA0UB1']['data'] = b64encode(bytearray([0x00])).decode()
        self.i_aaa['WA0PTI']['data'] = b64encode(bytearray([0x03])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertIn('021014', self.output.dumps)
        self.assertEqual('F9F6', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual('00', self.test_data.hex(self.o_aaa['WA0PTI']['data']))

    def test_infant_with_adults_ETAW(self):
        self.test_data.add_pnr_from_data(['2ZAVERI', 'I/1ZAVERI'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertIn('021014', self.output.dumps)
        self.assertEqual('F0F0', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual('03', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual('03', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual('01', self.test_data.hex(self.o_ecb['EBW010']['data']))
        self.assertEqual('01', self.test_data.hex(self.o_aaa['WA0PTI']['data']))

    def test_infant_only_ETAW(self):
        self.test_data.add_pnr_from_data(['I/3ZAVERI'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertIn('021014', self.output.dumps)
        self.assertEqual('F0F3', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual('03', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual('03', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual('03', self.test_data.hex(self.o_ecb['EBW010']['data']))
        self.assertEqual('03', self.test_data.hex(self.o_aaa['WA0PTI']['data']))

    def test_infant_at_start_with_less_adults_ETAW(self):
        self.test_data.add_pnr_from_data(['I/33ZAVERI', '44ZAVERI', 'I/22SHAH'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertIn('021014', self.output.dumps)
        self.assertEqual('F0F0', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual(f'{99:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual(f'{55:02X}', self.test_data.hex(self.o_ecb['EBW010']['data']))
        self.assertEqual(f'{55:02X}', self.test_data.hex(self.o_aaa['WA0PTI']['data']))

    def test_infant_with_group_wa0pti_ETAW(self):
        self.test_data.add_pnr_from_data(['Z/21SABRE', '3ZAVERI', 'I/1ZAVERI', '4SHAH', 'I/2SHAH'], 'name')
        self.i_aaa['WA0PTI']['data'] = b64encode(bytearray([0x03])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual('F1F4', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{24:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual(f'{24:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual('03', self.test_data.hex(self.o_ecb['EBW010']['data']))
        self.assertEqual('03', self.test_data.hex(self.o_aaa['WA0PTI']['data']))

    def test_infant_at_start_with_group_ETAW(self):
        self.test_data.add_pnr_from_data(['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'], 'name')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertIn('021014', self.output.dumps)
        self.assertEqual('F1F6', self.test_data.hex(self.o_aaa['WA0EXT']['data']))
        self.assertEqual(f'{32:02X}', self.test_data.hex(self.o_ecb['EBW015']['data']))
        self.assertEqual(f'{32:02X}', self.test_data.hex(self.o_aaa['WA0PTY']['data']))
        self.assertEqual('07', self.test_data.hex(self.o_ecb['EBW010']['data']))
        self.assertEqual('07', self.test_data.hex(self.o_aaa['WA0PTI']['data']))
        self.assertEqual('00', self.test_data.hex(self.o_ecb['EBW016']['data']))
