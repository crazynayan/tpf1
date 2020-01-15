from test.test_eta5_execution import NameGeneral


class NameVariation(NameGeneral):

    def test_multiple_name(self):
        self.test_data.add_pnr_element(['2ZAVERI', '6SHAH'], 'name', variation=0)
        self.test_data.add_pnr_element(['C/21TOURS', '2ZAVERI', '6SHAH'], 'name', variation=1)
        self.test_data.add_pnr_element(['2ZAVERI', '6SHAH', 'I/3ZAVERI'], 'name', variation=2)
        self.test_data.add_pnr_element(['C/21TOURS', '2ZAVERI', '6SHAH', 'I/3ZAVERI'], 'name', variation=3)
        test_data = self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('F0F0', test_data.get_field('WA0EXT', pnr_variation=0))
        self.assertEqual('F1F3', test_data.get_field('WA0EXT', pnr_variation=1))
        self.assertEqual('F0F0', test_data.get_field('WA0EXT', pnr_variation=2))
        self.assertEqual('F1F3', test_data.get_field('WA0EXT', pnr_variation=3))
        self.assertEqual(f"{8:02X}", test_data.get_field('WA0PTY', pnr_variation=0))
        self.assertEqual(f"{21:02X}", test_data.get_field('WA0PTY', pnr_variation=1))
        self.assertEqual(f"{11:02X}", test_data.get_field('WA0PTY', pnr_variation=2))
        self.assertEqual(f"{24:02X}", test_data.get_field('WA0PTY', pnr_variation=3))
        self.assertEqual(f"{0:02X}", test_data.get_field('WA0PTI', pnr_variation=0))
        self.assertEqual(f"{0:02X}", test_data.get_field('WA0PTI', pnr_variation=1))
        self.assertEqual(f"{3:02X}", test_data.get_field('WA0PTI', pnr_variation=2))
        self.assertEqual(f"{3:02X}", test_data.get_field('WA0PTI', pnr_variation=3))
