from base64 import b64encode

from config import config
from test.test_eta5_execution import NameGeneral, fqtv_gld


class BeforeNameETAW(NameGeneral):

    def setUp(self) -> None:
        super().setUp()
        self.test_data.add_pnr_from_data(['1ZAVERI'], 'name')

    def test_HFX_BA_TKV_SRT5(self):
        self.i_aaa['WA0ET6']['data'] = b64encode(bytes([self.wa0hfx])).decode()
        self.test_data.partition = 'BA'
        self.i_aaa['WA0US3']['data'] = b64encode(bytes([self.wa0tkv])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E2D9E3F5', self.test_data.hex(self.o_ecb['EBX004']['data']))  # SRT5

    def test_HFX_AA_TKV_SRT5(self):
        self.i_aaa['WA0ET6']['data'] = b64encode(bytes([self.wa0hfx])).decode()
        self.test_data.partition = 'AA'
        self.i_aaa['WA0US3']['data'] = b64encode(bytes([self.wa0tkv])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E2D9E3F5', self.test_data.hex(self.o_ecb['EBX004']['data']))  # SRT5

    def test_ASC_ITN_fqtv_ETAS(self):
        self.i_aaa['WA0ASC']['data'] = b64encode(bytes([0x01])).decode()
        self.i_aaa['WA0ET2']['data'] = b64encode(bytes([self.wa0itn])).decode()
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', config.AAAPNR)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('C5E3C1E2', self.test_data.hex(self.o_ecb['EBX008']['data']))  # ETAS

    def test_ASC_FTN_ETAS(self):
        self.i_aaa['WA0ASC']['data'] = b64encode(bytes([0x01])).decode()
        self.i_aaa['WA0XX3']['data'] = b64encode(bytes([self.wa0ftn])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('C5E3C1E2', self.test_data.hex(self.o_ecb['EBX008']['data']))  # ETAS

    def test_ASC_fqtv_ETAS(self):
        self.i_aaa['WA0ASC']['data'] = b64encode(bytes([0x01])).decode()
        self.test_data.add_pnr_from_byte_array(fqtv_gld, 'fqtv', config.AAAPNR)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('C5E3C1E2', self.test_data.hex(self.o_ecb['EBX008']['data']))  # ETAS

    def test_FTD_ETK2(self):
        self.i_aaa['WA0XX3']['data'] = b64encode(bytes([self.wa0ftd])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual(13, self.output.regs['R6'])

    def test_AFU_subs_ETGN(self):
        self.i_aaa['WA0USE']['data'] = b64encode(bytes([self.wa0afu])).decode()
        self.test_data.add_pnr_from_data(['TEST'], 'subs_card_seg')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('C5E3C7D5', self.test_data.hex(self.o_ecb['EBX012']['data']))  # ETGN

    def test_AFU_ETGN(self):
        self.i_aaa['WA0USE']['data'] = b64encode(bytes([self.wa0afu])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('C5E3C7D5', self.test_data.hex(self.o_ecb['EBX012']['data']))  # ETGN
