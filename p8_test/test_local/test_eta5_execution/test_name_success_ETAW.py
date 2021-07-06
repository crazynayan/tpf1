from p8_test.test_local.test_eta5_execution import NameGeneral


class NameSuccessETAW(NameGeneral):

    def setUp(self) -> None:
        super().setUp()

    def test_single_name_wa0pty_no_match_ETAW(self) -> None:
        self.test_data.add_pnr_element(["1ZAVERI"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("F0F0", test_data.get_field("WA0EXT"))
        self.assertEqual("01", test_data.get_field("WA0PTY"))

    def test_multiple_names_wa0pty_match_ETAW(self) -> None:
        self.test_data.add_pnr_element(["45ZAVERI", "54SHAH"], "name")
        self.test_data.set_field("WA0PTY", bytearray([99]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("F0F0", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY"))

    def test_WA0NAD_ETAW(self) -> None:
        self.test_data.add_pnr_element(["1ZAVERI", "3SHAH"], "name")
        self.test_data.set_field("WA0ETG", bytearray([self.wa0nad]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.FMSG_END, self.output.last_line, self.output.last_node)
        self.assertIn("VERIFY NAME ASSOCIATED DATA", self.output.messages)
        self.assertEqual("F0F0", test_data.get_field("WA0EXT"))
        self.assertEqual("04", test_data.get_field("WA0PTY"))
        self.assertEqual(7, self.output.regs["R6"])  # Call to ETK2 with R6=7 will ensure Name association is deleted
        self.assertEqual("00", test_data.get_field("WA0ETG"))  # WA0ETG, #WA0NAD

    def test_WA0CDI_ETAW(self) -> None:
        self.test_data.add_pnr_element(["33ZAVERI"], "name")
        self.test_data.set_field("WA0US4", bytearray([self.wa0cdi]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.FMSG_END, self.output.last_line)
        self.assertIn("NAME CHANGED - VERIFY VCR EXCHANGED", self.output.messages)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual("F0F0", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{33:02X}", test_data.get_field("WA0PTY"))
        self.assertEqual(60, self.output.regs["R6"])

    def test_group_C_ETAW(self) -> None:
        self.test_data.add_pnr_element(["C/21TOURS", "2ZAVERI"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("F1F9", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{21:02X}", test_data.get_field("WA0PTY"))
        self.assertEqual("80", test_data.get_field("EBW038"))
        self.assertEqual("10", test_data.get_field("EBSW01"))

    def test_group_Z_ETAW_wa0pyt_no_match(self) -> None:
        self.test_data.add_pnr_element(["Z/25SABRE", "3SHAH"], "name")
        self.test_data.set_field("WA0PTY", bytearray([3]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("80", test_data.get_field("EBW038"))
        self.assertEqual("F2F2", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{25:02X}", test_data.get_field("WA0PTY"))
        self.assertEqual("10", test_data.get_field("EBSW01"))

    def test_group_C_not_at_start_wa0pty_history_no_match_ETAW(self):
        self.test_data.add_pnr_element(["10ZAVERI", "C/21TOURS", "1SHAH"], "name")
        self.test_data.set_field("WA0PTY", bytearray([0xE3]))  # 99 = 0x63 with bit0 on is 0xE3
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.EXAA_NPTY_END, self.output.last_line)
        self.assertIn("021018", self.output.dumps)
        self.assertEqual("F1F0", test_data.get_field("WA0EXT"))
        self.assertEqual("95", test_data.get_field("WA0PTY"))  # 0x15 with bit0 on

    def test_pn2_on_group_9_C_ETAW(self):
        self.test_data.add_pnr_element(["C/99W/TOURS", "3SHAH"], "name")
        self.test_data.set_field("WA0UB1", bytearray([self.wa0pn2]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("F0F6", test_data.get_field("WA0EXT"))
        self.assertEqual("09", test_data.get_field("WA0PTY"))

    def test_pn2_on_group_99_C_ETAW(self):
        self.test_data.add_pnr_element(["C/999W/TOURS", "3SHAH"], "name")
        self.test_data.set_field("WA0UB1", bytearray([self.wa0pn2]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("F9F6", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY"))

    def test_pn2_on_group_Z_wa0pty_history_match_ETAW(self):
        # wa0PN2 OFF behaves the same way
        self.test_data.add_pnr_element(["Z/99W/SABRE", "3SHAH"], "name")
        self.test_data.set_field("WA0UB1", bytearray([self.wa0pn2]))
        self.test_data.set_field("WA0PTY", bytearray([0xE3]))  # 99 = 0x63 with bit0 on is 0xE3
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.EXAA_NPTY_END, self.output.last_line)
        self.assertIn("021018", self.output.dumps)
        self.assertEqual("F9F6", test_data.get_field("WA0EXT"))
        self.assertEqual("E3", test_data.get_field("WA0PTY"))

    def test_pn2_off_group_wa0pti_ETAW(self):
        self.test_data.add_pnr_element(["C/99W/TOURS", "3SHAH"], "name")
        self.test_data.set_field("WA0UB1", bytearray([0x00]))
        self.test_data.set_field("WA0PTI", bytearray([0x03]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertIn("021014", self.output.dumps)
        self.assertEqual("F9F6", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY"))
        self.assertEqual("00", test_data.get_field("WA0PTI"))

    def test_infant_with_adults_ETAW(self):
        self.test_data.add_pnr_element(["2ZAVERI", "I/1ZAVERI"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertIn("021014", self.output.dumps)
        self.assertEqual("F0F0", test_data.get_field("WA0EXT"))
        self.assertEqual("03", test_data.get_field("WA0PTY"))
        self.assertEqual("01", test_data.get_field("EBW010"))
        self.assertEqual("01", test_data.get_field("WA0PTI"))

    def test_infant_only_ETAW(self):
        self.test_data.add_pnr_element(["I/3ZAVERI"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertIn("021014", self.output.dumps)
        self.assertEqual("F0F3", test_data.get_field("WA0EXT"))
        self.assertEqual("03", test_data.get_field("WA0PTY"))
        self.assertEqual("03", test_data.get_field("EBW010"))
        self.assertEqual("03", test_data.get_field("WA0PTI"))

    def test_infant_at_start_with_less_adults_ETAW(self):
        self.test_data.add_pnr_element(["I/33ZAVERI", "44ZAVERI", "I/22SHAH"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertIn("021014", self.output.dumps)
        self.assertEqual("F0F0", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY"))
        self.assertEqual(f"{55:02X}", test_data.get_field("EBW010"))
        self.assertEqual(f"{55:02X}", test_data.get_field("WA0PTI"))

    def test_infant_with_group_wa0pti_ETAW(self):
        self.test_data.add_pnr_element(["Z/21SABRE", "3ZAVERI", "I/1ZAVERI", "4SHAH", "I/2SHAH"], "name")
        self.test_data.set_field("WA0PTI", bytearray([0x03]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line)
        self.assertEqual("F1F4", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{24:02X}", test_data.get_field("WA0PTY"))
        self.assertEqual("03", test_data.get_field("EBW010"))
        self.assertEqual("03", test_data.get_field("WA0PTI"))

    def test_infant_at_start_with_group_ETAW(self):
        self.test_data.add_pnr_element(["I/5ZAVERI", "3ZAVERI", "C/25TOURS", "6SHAH", "I/2SHAH"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.EXAA_NPTY_END, self.output.last_line, self.output.last_node)
        self.assertIn("021014", self.output.dumps)
        self.assertIn("021018", self.output.dumps)
        self.assertEqual("F1F6", test_data.get_field("WA0EXT"))
        self.assertEqual(f"{32:02X}", test_data.get_field("WA0PTY"))
        self.assertEqual("07", test_data.get_field("EBW010"))
        self.assertEqual("07", test_data.get_field("WA0PTI"))
        self.assertEqual("00", test_data.get_field("EBW016"))
