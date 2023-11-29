from d21_backend.p8_test.test_local.test_eta5_execution import NameGeneral


class NameFailETK1(NameGeneral):
    ETK1_END = "FMSG0100"
    TTY_END = "TIX10000"

    def setUp(self) -> None:
        super().setUp()

    def test_no_name_tty_ETK1_33(self) -> None:
        self.test_data.set_field("WA0ET4", bytes([self.wa0tty]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.TTY_END, self.output.last_line, self.output.last_node)
        self.assertEqual("00", test_data.get_field("UI2CNN"))
        self.assertEqual("60", test_data.get_field("EBRS01"))
        self.assertEqual("18", test_data.get_field("EBW028"))

    def test_too_many_names_tty_ETK1_33(self) -> None:
        self.test_data.add_pnr_element(["45ZAVERI", "55SHAH"], "name")
        self.test_data.set_field("WA0ET4", bytes([self.wa0tty]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.TTY_END, self.output.last_line, self.output.last_node)
        self.assertEqual("18", test_data.get_field("EBW028"))
        self.assertEqual("60", test_data.get_field("EBRS01"))

    def test_group_overbooking_tty_ETK1_33(self):
        self.test_data.add_pnr_element(["Z/15TIGER", "11ZAVERI", "5SHAH"], "name")
        self.test_data.set_field("WA0ET4", bytes([self.wa0tty]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.TTY_END, self.output.last_line)
        self.assertEqual("18", test_data.get_field("EBW028"))
        self.assertEqual("60", test_data.get_field("EBRS01"))

    def test_multiple_groups_CC_tty_ETK1_33(self):
        self.test_data.add_pnr_element(["C/25TOURS", "C/21TOURS", "1SHAH"], "name")
        self.test_data.set_field("WA0ET4", bytes([self.wa0tty]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.TTY_END, self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual("18", test_data.get_field("EBW028"))
        self.assertEqual("60", test_data.get_field("EBRS01"))
        self.assertEqual("C3", test_data.get_field("EBW014"))

    def test_multiple_groups_ZC_tty_ETK1_33(self):
        self.test_data.add_pnr_element(["Z/25TIGER", "C/21TOURS", "1SHAH"], "name")
        self.test_data.set_field("WA0ET4", bytes([self.wa0tty]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.TTY_END, self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual("18", test_data.get_field("EBW028"))
        self.assertEqual("60", test_data.get_field("EBRS01"))
        self.assertEqual("E9", test_data.get_field("EBW014"))

    def test_multiple_groups_CZ_tty_ETK1_16(self):
        self.test_data.add_pnr_element(["C/25TOURS", "Z/21TIGER", "1SHAH"], "name")
        self.test_data.set_field("WA0ET4", bytes([self.wa0tty]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.TTY_END, self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual("18", test_data.get_field("EBW028"))
        self.assertEqual("E0", test_data.get_field("EBRS01"))
        self.assertEqual("C3", test_data.get_field("EBW014"))

    def test_multiple_groups_ZZ_tty_ETK1_16(self):
        self.test_data.add_pnr_element(["Z/25TIGER", "Z/21TIGER", "1SHAH"], "name")
        self.test_data.set_field("WA0ET4", bytes([self.wa0tty]))
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.TTY_END, self.output.last_line)
        self.assertListEqual(list(), self.output.dumps)
        self.assertEqual("18", test_data.get_field("EBW028"))
        self.assertEqual("E0", test_data.get_field("EBRS01"))
        self.assertEqual("E9", test_data.get_field("EBW014"))

    def test_invalid_type_ETK1_16(self):
        self.test_data.add_pnr_element(["K/13TOURS", "1ZAVERI"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETK1_END, self.output.last_line)
        self.assertEqual("E0", test_data.get_field("EBRS01"))
        self.assertEqual("D2", test_data.get_field("EBW014"))
        self.assertIn("INVLD $CPN/SEG ASSOC FAILED ON AIRLINE CODE$", self.output.messages)

    def test_group_Z_not_at_start_ETK1_16(self):
        # It will give the same error if number of party is mentioned in Z/
        self.test_data.add_pnr_element(["3ZAVERI", "Z/TIGER", "1SHAH"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETK1_END, self.output.last_line)
        self.assertIn("INVLD $CPN/SEG ASSOC FAILED ON AIRLINE CODE$", self.output.messages)
        self.assertEqual("E0", test_data.get_field("EBRS01"))
        self.assertEqual("00", test_data.get_field("EBW014"))

    def test_multiple_groups_ZZ_ETK1_16(self):
        self.test_data.add_pnr_element(["Z/25TIGER", "Z/21TOURS", "1FSHAH"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETK1_END, self.output.last_line)
        self.assertIn("INVLD $CPN/SEG ASSOC FAILED ON AIRLINE CODE$", self.output.messages)
        self.assertEqual("E0", test_data.get_field("EBRS01"))
        self.assertEqual("E9", test_data.get_field("EBW014"))

    def test_multiple_groups_CZ_ETK1_16(self):
        self.test_data.add_pnr_element(["C/25TIGER", "Z/21TOURS", "1SHAH"], "name")
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETK1_END, self.output.last_line)
        self.assertIn("INVLD $CPN/SEG ASSOC FAILED ON AIRLINE CODE$", self.output.messages)
        self.assertEqual("E0", test_data.get_field("EBRS01"))
        self.assertEqual("C3", test_data.get_field("EBW014"))
