from base64 import b64encode

from test.test_eta5_execution import NameGeneral, hfax_2812_gld, fqtv_gld, itin_2811_2812, tr1gaa
from utils.data_type import DataType


class Companion(NameGeneral):

    def setUp(self) -> None:
        super().setUp()
        self.test_data.add_pnr_from_data(['1ZAVERI'], 'name')
        self.test_data.add_tpfdf(tr1gaa, '40', 'TR1GAA')
        self.i_aaa['WA0ET6'].data = b64encode(bytes([self.wa0hfx])).decode()
        self.fqtv_exp_key = [
            {
                'PR00_60_FQT_CXR': DataType('C', input='AA').to_bytes(),
                'PR00_60_FQT_FTN': DataType('C', input='NKE9088').to_bytes(),
                'PR00_60_FQT_TYP': DataType('X', input='60').to_bytes(),  # EXP and # KEY
            },
        ]

    def test_fqtv_itin_match_award_not_exp_key_ETK2(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETK20100.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('60', self.o_ecb['EBRS01'].hex)
        self.assertEqual(116, self.output.regs['R6'])

    def test_fqtv_no_match_award_not_exp_key_ETK2(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(self.fqtv_exp_key, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETK20100.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('60', self.o_ecb['EBRS01'].hex)
        self.assertEqual(116, self.output.regs['R6'])

    def test_itin_no_match_award_not_exp_key_ETK2(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETK20100.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('60', self.o_ecb['EBRS01'].hex)
        self.assertEqual(116, self.output.regs['R6'])

    def test_date_error_ETK2(self) -> None:
        hfax_2812_gld_date_error = ['SSRFQTUAA2811Y32OCTDFW  ORD  0510GLD*DGHWCL RR    ']
        self.test_data.add_pnr_from_data(hfax_2812_gld_date_error, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('ETK20100.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('60', self.o_ecb['EBRS01'].hex)
        self.assertEqual(116, self.output.regs['R6'])

    def test_fqtv_itin_match_no_award_exp_ETAW(self) -> None:
        hfax_2811_exp = ['SSRFQTUAA2811Y20OCTDFW  ORD  0510EXP*DGHWCL RR    ']
        self.test_data.add_pnr_from_data(hfax_2811_exp, 'hfax')
        self.test_data.add_pnr_from_byte_array(self.fqtv_exp_key, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_fqtv_itin_match_award_exp_ETAW(self) -> None:
        hfax_2812_exp = ['SSRFQTUAA2812Y20OCTDFW  ORD  0510EXP*DGHWCL RR    ']
        self.test_data.add_pnr_from_data(hfax_2812_exp, 'hfax')
        self.test_data.add_pnr_from_byte_array(self.fqtv_exp_key, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_fqtv_itin_match_award_key_ETAW(self) -> None:
        hfax_2812_key = ['SSRFQTUAA2812Y20OCTDFW  ORD  0510KEY*DGHWCL RR    ']
        self.test_data.add_pnr_from_data(hfax_2812_key, 'hfax')
        self.test_data.add_pnr_from_byte_array(self.fqtv_exp_key, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_no_tr1gaa_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.test_data.tpfdf = list()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_tr1gaa_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.errors.append('ETA92100.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_dbifb_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.errors.append('ETA92300.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_pnrcc_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.errors.append('ETA92300.10')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_prp1_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.errors.append('PRP1ERR')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_eta9pdwk_allocate_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.errors.append('ETA92300.27')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_fqtv_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.errors.append('ETA92400.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_itin_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.test_data.errors.append('ETA92500.1')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_chkaward_allocate_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.test_data.errors.append('ETA92500.11')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_chkaward_loadadd_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.test_data.errors.append('ETA92500.24')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)

    def test_fqtv_itin_match_award_error_ETAW(self) -> None:
        self.test_data.add_pnr_from_data(hfax_2812_gld, 'hfax')
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', 'DGHWCL')
        self.test_data.add_pnr_from_byte_array(itin_2811_2812, 'itin', 'DGHWCL')
        self.test_data.errors.append('WP89ERR')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E6D7F8F9', self.o_ecb['EBX000'].hex)
        self.assertEqual('01', self.o_aaa['WA0PTY'].hex)
