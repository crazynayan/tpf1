from d21_backend.p8_test.test_local.test_eta5_execution import NameGeneral, hfax_2812_gld, fqtv_gld, itin_2811_2812, tr1gaa


class Companion(NameGeneral):

    def setUp(self) -> None:
        super().setUp()
        self.test_data.add_pnr_element(["1ZAVERI"], "name")
        self.test_data.add_tpfdf(tr1gaa, "40", "TR1GAA")
        self.test_data.set_field("WA0ET6", bytes([self.wa0hfx]))
        self.fqtv_exp_key = f"""
            PR00_60_FQT_CXR:{bytes("AA", "CP037").hex()}:I1, 
            PR00_60_FQT_FTN:{bytes("NKE9088", "CP037").hex()}:I1,
            PR00_60_FQT_TYP:60:I1 """

    def test_fqtv_itin_match_award_not_exp_key_ETK2(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETK2_END, self.output.last_line, self.output.last_node)
        self.assertEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("60", test_data.get_field("EBRS01"))
        self.assertEqual(116, self.output.regs["R6"])

    def test_fqtv_no_match_award_not_exp_key_ETK2(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.add_pnr_field_data(self.fqtv_exp_key, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETK2_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("60", test_data.get_field("EBRS01"))
        self.assertEqual(116, self.output.regs["R6"])

    def test_itin_no_match_award_not_exp_key_ETK2(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", "DGHWCL")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETK2_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("60", test_data.get_field("EBRS01"))
        self.assertEqual(116, self.output.regs["R6"])

    def test_date_error_ETK2(self) -> None:
        hfax_2812_gld_date_error = ["SSRFQTUAA2811Y32OCTDFW  ORD  0510GLD*DGHWCL RR    "]
        self.test_data.add_pnr_element(hfax_2812_gld_date_error, "hfax")
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", "DGHWCL")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETK2_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("60", test_data.get_field("EBRS01"))
        self.assertEqual(116, self.output.regs["R6"])

    def test_fqtv_itin_match_no_award_exp_ETAW(self) -> None:
        hfax_2811_exp = ["SSRFQTUAA2811Y20OCTDFW  ORD  0510EXP*DGHWCL RR    "]
        self.test_data.add_pnr_element(hfax_2811_exp, "hfax")
        self.test_data.add_pnr_field_data(self.fqtv_exp_key, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_fqtv_itin_match_award_exp_ETAW(self) -> None:
        hfax_2812_exp = ["SSRFQTUAA2812Y20OCTDFW  ORD  0510EXP*DGHWCL RR    "]
        self.test_data.add_pnr_element(hfax_2812_exp, "hfax")
        self.test_data.add_pnr_field_data(self.fqtv_exp_key, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_fqtv_itin_match_award_key_ETAW(self) -> None:
        hfax_2812_key = ["SSRFQTUAA2812Y20OCTDFW  ORD  0510KEY*DGHWCL RR    "]
        self.test_data.add_pnr_element(hfax_2812_key, "hfax")
        self.test_data.add_pnr_field_data(self.fqtv_exp_key, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_no_tr1gaa_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        self.test_data.tpfdf = list()
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_tr1gaa_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.errors.append("ETA92100.1")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_dbifb_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.errors.append("ETA92300.1")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_pnrcc_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.errors.append("ETA92300.10")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_prp1_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.errors.append("PRP1ERR")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_eta9pdwk_allocate_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.errors.append("ETA92300.27")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_fqtv_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.errors.append("ETA92400.1")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_itin_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", "DGHWCL")
        self.test_data.errors.append("ETA92500.1")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_chkaward_allocate_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        self.test_data.errors.append("ETA92500.11")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line, self.output.last_node)
        self.assertNotEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_chkaward_loadadd_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        self.test_data.errors.append("ETA92500.24")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_fqtv_itin_match_award_error_ETAW(self) -> None:
        self.test_data.add_pnr_element(hfax_2812_gld, "hfax")
        self.test_data.add_pnr_field_data(fqtv_gld, "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data(itin_2811_2812, "itin", "DGHWCL")
        self.test_data.errors.append("WP89ERR")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line)
        self.assertEqual("E6D7F8F9", test_data.get_field("EBX000"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))
