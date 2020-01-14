from base64 import b64encode

from test.test_eta5_execution import NameGeneral


class NameSuccessVarious(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_infant_group_call_from_TOQ1(self) -> None:
        self.test_data.add_pnr_element(['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'], 'name')
        test_data = self.tpf_server.run('TOQ1', self.test_data)
        self.assertEqual('$$TOQ1$$.4', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F1F6', test_data.field('WA0EXT'))  # Group - Adults
        self.assertEqual(f'{32:02X}', test_data.field('EBW015'))  # Group + Infants
        self.assertEqual('09', test_data.field('EBW016'))  # Adults
        self.assertEqual('07', test_data.field('EBW010'))  # Infants
        self.assertEqual('00', test_data.field('WA0PTY'))  # Group + Infants
        self.assertEqual('00', test_data.field('WA0PTI'))  # Infants

    def test_infant_group_with_error_from_itinerary_police_not_file_rec_mode_ETA2(self) -> None:
        self.test_data.add_pnr_element(['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'], 'name')
        self.i_aaa['WA0PTI']['data'] = b64encode(bytes([7])).decode()
        self.i_aaa['WA0PTY']['data'] = b64encode(bytes([32])).decode()
        self.i_aaa['WA0ET3']['data'] = b64encode(bytes([0x00])).decode()
        self.test_data.errors.append('ETC1ERR')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETA2$$.1', test_data.output.last_line)
        self.assertListEqual(list(), test_data.output.dumps)
        self.assertEqual('F1F6', test_data.field('WA0EXT'))  # Group - Adults
        self.assertEqual(f'{32:02X}', test_data.field('EBW015'))  # Group + Infants
        self.assertEqual('00', test_data.field('EBW016'))  # Adults
        self.assertEqual('07', test_data.field('EBW010'))  # Infants
        self.assertEqual(f'{32:02X}', test_data.field('WA0PTY'))  # Group + Infants
        self.assertEqual('07', test_data.field('WA0PTI'))  # Infants

    def test_infant_group_with_error_from_itinerary_police_file_rec_mode_FRD1(self) -> None:
        self.test_data.add_pnr_element(['I/5ZAVERI', '3ZAVERI', 'C/25TOURS', '6SHAH', 'I/2SHAH'], 'name')
        self.i_aaa['WA0PTI']['data'] = b64encode(bytes([0x00])).decode()
        self.i_aaa['WA0PTY']['data'] = b64encode(bytes([0x00])).decode()
        self.i_aaa['WA0ET3']['data'] = b64encode(bytes([0x10])).decode()
        self.test_data.errors.append('ETC1ERR')
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$FRD1$$.1', test_data.output.last_line)
        self.assertIn('021014', test_data.output.dumps)
        self.assertEqual('F1F6', test_data.field('WA0EXT'))  # Group - Adults
        self.assertEqual(f'{32:02X}', test_data.field('EBW015'))  # Group + Infants
        self.assertEqual('00', test_data.field('EBW016'))  # Adults
        self.assertEqual('07', test_data.field('EBW010'))  # Infants
        self.assertEqual(f'{32:02X}', test_data.field('WA0PTY'))  # Group + Infants
        self.assertEqual('07', test_data.field('WA0PTI'))  # Infants
