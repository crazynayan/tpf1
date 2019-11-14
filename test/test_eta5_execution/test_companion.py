from base64 import b64encode
from typing import List, Dict

from config import config
from firestore.test_data import Tpfdf, Pnr
from test.input_td import TD
from test.test_eta5_execution import NameGeneral


class Companion(NameGeneral):

    def setUp(self) -> None:
        super().setUp()
        self._setup_names(['1ZAVERI'])
        for tr1gaa in TD.tr1gaa:
            tpfdf = Tpfdf()
            tpfdf.macro_name = 'TR1GAA'
            tpfdf.key = '40'
            tpfdf.field_bytes = self._convert_to_field_bytes(tr1gaa)
            self.test_data.tpfdf.append(tpfdf)
        self.i_aaa['WA0ET6'].data = b64encode(bytes([TD.wa0hfx])).decode()

    def _setup_hfax(self, locator: str, hfax_list: List[str]):
        for hfax in hfax_list:
            pnr = Pnr()
            pnr.key = 'hfax'
            pnr.data = hfax
            pnr.locator = locator
            self.test_data.pnr.append(pnr)
        return

    def _setup_itin(self, locator: str, itin_list: List[Dict[str, bytearray]]):
        for itin in itin_list:
            pnr = Pnr()
            pnr.key = 'itin'
            pnr.locator = locator
            pnr.field_bytes = self._convert_to_field_bytes(itin)
            self.test_data.pnr.append(pnr)
        return

    def test_fqtv_itin_match_award_not_exp_key_ETK2(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self._setup_fqtv('DGHWCL', TD.fqtv_gld)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETK20100.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('60', self._o_ecb('EBRS01'))
        self.assertEqual(116, self.output.regs['R6'])

    def test_fqtv_no_match_award_not_exp_key_ETK2(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self._setup_fqtv('DGHWCL', TD.fqtv_exp_key)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETK20100.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('60', self._o_ecb('EBRS01'))
        self.assertEqual(116, self.output.regs['R6'])

    def test_itin_no_match_award_not_exp_key_ETK2(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self._setup_fqtv('DGHWCL', TD.fqtv_gld)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETK20100.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('60', self._o_ecb('EBRS01'))
        self.assertEqual(116, self.output.regs['R6'])

    def test_date_error_ETK2(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld_date_error)
        self._setup_fqtv('DGHWCL', TD.fqtv_gld)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETK20100.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('60', self._o_ecb('EBRS01'))
        self.assertEqual(116, self.output.regs['R6'])

    def test_fqtv_itin_match_no_award_exp_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2811_exp)
        self._setup_fqtv('DGHWCL', TD.fqtv_exp_key)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_fqtv_itin_match_award_exp_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_exp)
        self._setup_fqtv('DGHWCL', TD.fqtv_exp_key)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_fqtv_itin_match_award_key_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_key)
        self._setup_fqtv('DGHWCL', TD.fqtv_exp_key)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_no_tr1gaa_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self._setup_fqtv('DGHWCL', TD.fqtv_gld)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.test_data.tpfdf = list()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_tr1gaa_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self.test_data.errors.append('ETA92100.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_dbifb_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self.test_data.errors.append('ETA92300.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_pnrcc_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self.test_data.errors.append('ETA92300.10')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_prp1_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self.test_data.errors.append('PRP1ERR')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_eta9pdwk_allocate_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self.test_data.errors.append('ETA92300.27')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_fqtv_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self.test_data.errors.append('ETA92400.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_itin_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self._setup_fqtv('DGHWCL', TD.fqtv_gld)
        self.test_data.errors.append('ETA92500.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_chkaward_allocate_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self._setup_fqtv('DGHWCL', TD.fqtv_gld)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.test_data.errors.append('ETA92500.11')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_chkaward_loadadd_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self._setup_fqtv('DGHWCL', TD.fqtv_gld)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.test_data.errors.append('ETA92500.24')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))

    def test_fqtv_itin_match_award_error_ETAW(self) -> None:
        self._setup_hfax(config.AAAPNR, TD.hfax_2812_gld)
        self._setup_fqtv('DGHWCL', TD.fqtv_gld)
        self._setup_itin('DGHWCL', TD.itin_2811_2812)
        self.test_data.errors.append('WP89ERR')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self._o_ecb('EBX000'))
        self.assertEqual('01', self._o_aaa('WA0PTY'))
