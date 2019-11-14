from base64 import b64decode, b64encode

from test.input_td import TD
from test.test_eta5_execution import NameGeneral


class NameSuccessETAW(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_single_name_wa0pty_no_match_ETAW(self) -> None:
        self._setup_names(['1ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual('F0F0', self._o_aaa('WA0EXT'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))
        self.assertEqual('01', self._o_ecb('EBW015'))
        self.assertEqual(f'{TD.ui2214:02X}', b64decode(self.ui2cnn.data).hex().upper())

    def test_multiple_names_wa0pty_match_ETAW(self) -> None:
        self._setup_names(['45ZAVERI', '54SHAH'])
        self.i_aaa['WA0PTY'].data = b64encode(bytearray([99])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual('F0F0', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{99:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual(f'{99:02X}', self._o_ecb('EBW015'))
        self.assertEqual(f'{TD.ui2214:02X}', b64decode(self.ui2cnn.data).hex().upper())

    def test_WA0NAD_ETAW(self) -> None:
        self._setup_names(['1ZAVERI', '3SHAH'])
        self.i_aaa['WA0ETG'].data = b64encode(bytearray([TD.wa0nad])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual('F0F0', self._o_aaa('WA0EXT'))
        self.assertEqual('04', self._o_aaa('WA0PTY'))
        self.assertEqual('04', self._o_ecb('EBW015'))
        self.assertEqual(f'{TD.ui2214:02X}', b64decode(self.ui2cnn.data).hex().upper())
        self.assertEqual('00', self._o_aaa('WA0ETG'))  # WA0ETG, #WA0NAD
        self.assertEqual(7, output.regs['R6'])  # Call to ETK2 with R6=7 will ensure Name association is deleted

    def test_WA0CDI_ETAW(self) -> None:
        self._setup_names(['33ZAVERI'])
        self.i_aaa['WA0US4'].data = b64encode(bytearray([TD.wa0cdi])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual('F0F0', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{33:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual(f'{33:02X}', self._o_ecb('EBW015'))
        self.assertEqual(60, output.regs['R6'])

    def test_group_C_ETAW(self) -> None:
        self._setup_names(['C/21TOURS', '2ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual('F1F9', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{21:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual(f'{21:02X}', self._o_ecb('EBW015'))
        self.assertEqual('C3', self._o_ecb('EBW014'))
        self.assertEqual('80', self._o_ecb('EBW038'))
        self.assertEqual('10', self._o_ecb('EBSW01'))

    def test_group_Z_ETAW_wa0pyt_no_match(self) -> None:
        self._setup_names(['Z/25SABRE', '3SHAH'])
        self.i_aaa['WA0PTY'].data = b64encode(bytearray([3])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual('F2F2', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{25:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual(f'{25:02X}', self._o_ecb('EBW015'))
        self.assertEqual('E9', self._o_ecb('EBW014'))
        self.assertEqual('80', self._o_ecb('EBW038'))
        self.assertEqual('10', self._o_ecb('EBSW01'))

    def test_group_C_not_at_start_wa0pty_history_no_match_ETAW(self):
        self._setup_names(['10ZAVERI', 'C/21TOURS', '1SHAH'])
        self.i_aaa['WA0PTY'].data = b64encode(bytearray([0xE3])).decode()  # 99 = 0x63 with bit0 on is 0xE3
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual('F1F0', self._o_aaa('WA0EXT'))
        self.assertEqual('C3', self._o_ecb('EBW014'))
        self.assertEqual('95', self._o_aaa('WA0PTY'))  # 0x15 with bit0 on
        self.assertEqual('15', self._o_ecb('EBW015'))  # 21 = 0x15

    def test_pn2_on_group_9_C_ETAW(self):
        self._setup_names(['C/99W/TOURS', '3SHAH'])
        self.i_aaa['WA0UB1'].data = b64encode(bytearray([TD.wa0pn2])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertEqual('F0F6', self._o_aaa('WA0EXT'))
        self.assertEqual('09', self._o_aaa('WA0PTY'))
        self.assertEqual('09', self._o_ecb('EBW015'))

    def test_pn2_on_group_99_C_ETAW(self):
        self._setup_names(['C/999W/TOURS', '3SHAH'])
        self.i_aaa['WA0UB1'].data = b64encode(bytearray([TD.wa0pn2])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertEqual('F9F6', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{99:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual(f'{99:02X}', self._o_ecb('EBW015'))

    def test_pn2_on_group_Z_wa0pty_history_match_ETAW(self):
        # T.wa0PN2 OFF behaves the same way
        self._setup_names(['Z/99W/SABRE', '3SHAH'])
        self.i_aaa['WA0UB1'].data = b64encode(bytearray([TD.wa0pn2])).decode()
        self.i_aaa['WA0PTY'].data = b64encode(bytearray([0xE3])).decode()  # 99 = 0x63 with bit0 on is 0xE3
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertEqual('F9F6', self._o_aaa('WA0EXT'))
        self.assertEqual('E3', self._o_aaa('WA0PTY'))
        self.assertEqual(f'{99:02X}', self._o_ecb('EBW015'))

    def test_pn2_off_group_wa0pti_ETAW(self):
        self._setup_names(['C/99W/TOURS', '3SHAH'])
        self.i_aaa['WA0UB1'].data = b64encode(bytearray([0x00])).decode()
        self.i_aaa['WA0PTI'].data = b64encode(bytearray([0x03])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual('F9F6', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{99:02X}', self._o_ecb('EBW015'))
        self.assertEqual(f'{99:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual('00', self._o_aaa('WA0PTI'))

    def test_infant_with_adults_ETAW(self):
        self._setup_names(['2ZAVERI', 'I/1ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual('F0F0', self._o_aaa('WA0EXT'))
        self.assertEqual('03', self._o_ecb('EBW015'))
        self.assertEqual('03', self._o_aaa('WA0PTY'))
        self.assertEqual('01', self._o_ecb('EBW010'))
        self.assertEqual('01', self._o_aaa('WA0PTI'))

    def test_infant_only_ETAW(self):
        self._setup_names(['I/3ZAVERI'])
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual('F0F3', self._o_aaa('WA0EXT'))
        self.assertEqual('03', self._o_ecb('EBW015'))
        self.assertEqual('03', self._o_aaa('WA0PTY'))
        self.assertEqual('03', self._o_ecb('EBW010'))
        self.assertEqual('03', self._o_aaa('WA0PTI'))

    def test_infant_at_start_with_less_adults_ETAW(self):
        self._setup_names(['I/33ZAVERI', '44ZAVERI', 'I/22SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual('F0F0', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{99:02X}', self._o_ecb('EBW015'))
        self.assertEqual(f'{99:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual(f'{55:02X}', self._o_ecb('EBW010'))
        self.assertEqual(f'{55:02X}', self._o_aaa('WA0PTI'))

    def test_infant_with_group_wa0pti_ETAW(self):
        self._setup_names(['Z/21SABRE', '3ZAVERI', 'I/1ZAVERI', '4SHAH', 'I/2SHAH'])
        self.i_aaa['WA0PTI'].data = b64encode(bytearray([0x03])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertListEqual(list(), output.dumps)
        self.assertEqual('F1F4', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{24:02X}', self._o_ecb('EBW015'))
        self.assertEqual(f'{24:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual('03', self._o_ecb('EBW010'))
        self.assertEqual('03', self._o_aaa('WA0PTI'))

    def test_infant_at_start_with_group_ETAW(self):
        self._setup_names(['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'])
        self.tpf_server.run('ETA5', self.test_data)
        output = self.test_data.outputs[0]
        self.assertEqual('$$ETAW$$.1', output.last_line)
        self.assertIn('021014', output.dumps)
        self.assertEqual('F1F6', self._o_aaa('WA0EXT'))
        self.assertEqual(f'{32:02X}', self._o_ecb('EBW015'))
        self.assertEqual(f'{32:02X}', self._o_aaa('WA0PTY'))
        self.assertEqual('07', self._o_ecb('EBW010'))
        self.assertEqual('07', self._o_aaa('WA0PTI'))
        self.assertEqual('00', self._o_ecb('EBW016'))
