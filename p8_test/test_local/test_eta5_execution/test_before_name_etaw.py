from config import config
from p8_test.test_local.test_eta5_execution import NameGeneral, fqtv_gld


class BeforeNameETAW(NameGeneral):

    def setUp(self) -> None:
        super().setUp()
        self.test_data.add_pnr_element(["1ZAVERI"], "name")

    def test_HFX_BA_TKV_SRT5(self):
        self.test_data.set_field("WA0ET6", bytes([self.wa0hfx]))
        self.test_data.partition = "VA"
        self.test_data.set_field("WA0US3", bytes([self.wa0tkv]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertNotEqual("E2D9E3F5", test_data.get_field("EBX004"))  # SRT5

    def test_HFX_AA_TKV_SRT5(self):
        self.test_data.set_field("WA0ET6", bytes([self.wa0hfx]))
        self.test_data.partition = "AA"
        self.test_data.set_field("WA0US3", bytes([self.wa0tkv]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("E2D9E3F5", test_data.get_field("EBX004"))  # SRT5

    def test_ASC_ITN_fqtv_ETAS(self):
        self.test_data.set_field("WA0ASC", bytes([0x01]))
        self.test_data.set_field("WA0ET2", bytes([self.wa0itn]))
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", config.AAAPNR)
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.FMSG_END, self.output.last_line)
        self.assertIn("INVLD ITIN", self.output.messages)
        self.assertEqual("C5E3C1E2", test_data.get_field("EBX008"))  # ETAS

    def test_ASC_FTN_ETAS(self):
        self.test_data.set_field("WA0ASC", bytes([0x01]))
        self.test_data.set_field("WA0XX3", bytes([self.wa0ftn]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.FMSG_END, self.output.last_line)
        self.assertIn("INVLD ITIN", self.output.messages)
        self.assertNotEqual("C5E3C1E2", test_data.get_field("EBX008"))  # ETAS

    def test_ASC_fqtv_ETAS(self):
        self.test_data.set_field("WA0ASC", bytes([0x01]))
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", config.AAAPNR)
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.FMSG_END, self.output.last_line)
        self.assertIn("INVLD ITIN", self.output.messages)
        self.assertNotEqual("C5E3C1E2", test_data.get_field("EBX008"))  # ETAS

    def test_FTD_ETK2(self):
        self.test_data.set_field("WA0XX3", bytes([self.wa0ftd]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual(13, self.output.regs["R6"])

    def test_AFU_subs_ETGN(self):
        self.test_data.set_field("WA0USE", bytes([self.wa0afu]))
        self.test_data.add_pnr_element(["TEST"], "subs_card_seg")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("C5E3C7D5", test_data.get_field("EBX012"))  # ETGN

    def test_AFU_ETGN(self):
        self.test_data.set_field("WA0USE", bytes([self.wa0afu]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line, self.output.last_node)
        self.assertNotEqual("C5E3C7D5", test_data.get_field("EBX012"))  # ETGN
