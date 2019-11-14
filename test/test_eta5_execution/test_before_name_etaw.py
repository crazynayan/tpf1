from base64 import b64encode
from typing import List

from config import config
from firestore.test_data import Pnr
from test.input_td import TD
from test.test_eta5_execution import NameGeneral


class BeforeNameETAW(NameGeneral):

    def setUp(self) -> None:
        super().setUp()
        self._setup_names(['1ZAVERI'])

    def _setup_subs_card_seg(self, locator: str, subs_list: List[str]):
        for card in subs_list:
            pnr = Pnr()
            pnr.key = 'subs_card_seg'
            pnr.data = card
            pnr.locator = locator
            self.test_data.pnr.append(pnr)
        return

    def test_HFX_BA_SRT5(self):
        self.i_aaa['WA0ET6'].data = b64encode(bytes([TD.wa0hfx])).decode()
        TD.state.set_partition('BA')
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('E2D9E3F5', self._o_ecb('EBX004'))  # SRT5

    def test_HFX_AA_TKV_SRT5(self):
        self.i_aaa['WA0ET6'].data = b64encode(bytes([TD.wa0hfx])).decode()
        self.i_aaa['WA0US3'].data = b64encode(bytes([TD.wa0tkv])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('E2D9E3F5', self._o_ecb('EBX004'))  # SRT5

    def test_ASC_ITN_fqtv_ETAS(self):
        self.i_aaa['WA0ASC'].data = b64encode(bytes([0x01])).decode()
        self.i_aaa['WA0ET2'].data = b64encode(bytes([TD.wa0itn])).decode()
        self._setup_fqtv(config.AAAPNR, TD.fqtv_gld)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('C5E3C1E2', self._o_ecb('EBX008'))  # ETAS

    def test_ASC_FTN_ETAS(self):
        self.i_aaa['WA0ASC'].data = b64encode(bytes([0x01])).decode()
        self.i_aaa['WA0XX3'].data = b64encode(bytes([TD.wa0ftn])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('C5E3C1E2', self._o_ecb('EBX008'))  # ETAS

    def test_ASC_fqtv_ETAS(self):
        self.i_aaa['WA0ASC'].data = b64encode(bytes([0x01])).decode()
        self._setup_fqtv(config.AAAPNR, TD.fqtv_gld)
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('C5E3C1E2', self._o_ecb('EBX008'))  # ETAS

    def test_FTD_ETK2(self):
        self.i_aaa['WA0XX3'].data = b64encode(bytes([TD.wa0ftd])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual(13, self.output.regs['R6'])

    def test_AFU_subs_ETGN(self):
        self.i_aaa['WA0USE'].data = b64encode(bytes([TD.wa0afu])).decode()
        self._setup_subs_card_seg(config.AAAPNR, ['TEST'])
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertEqual('C5E3C7D5', self._o_ecb('EBX012'))  # ETGN

    def test_AFU_ETGN(self):
        self.i_aaa['WA0USE'].data = b64encode(bytes([TD.wa0afu])).decode()
        self.tpf_server.run('ETA5', self.test_data)
        self.assertEqual('$$ETAW$$.1', self.output.last_line)
        self.assertNotEqual('C5E3C7D5', self._o_ecb('EBX012'))  # ETGN
