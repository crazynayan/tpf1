from p1_utils.data_type import DataType
from p8_test.test_local import TestDebug


class Eta1Test(TestDebug):
    DEBUG_DATA = list()
    SEGMENT = "ETA1"

    def test_eta1_vanilla(self):
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAX265.6", self.output.last_line, self.output.last_node)
        self.assertIn("UNABLE TO END TRANSACTION - NO PNR PRESENT IN WORK AREA", self.output.messages)
        self.assertEqual(list(), self.output.dumps)

    def test_eta1_el_restricted(self):
        self.test_data.add_fields([("EBW000", 10)], "EB0EB")
        self.test_data.set_field("MI0ACC", DataType("C", input="EL").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.set_field("WA0UB4", DataType("X", input="08").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("$$UIO1$$.2", self.output.last_line, self.output.last_node)
        self.assertIn("RESTRICTED" + 40 * " ", self.output.messages)

    def test_eta1_e_no_error(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="E").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.set_field("WA0UB4", DataType("X", input="08").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAX265.6", self.output.last_line, self.output.last_node)
        self.assertIn("UNABLE TO END TRANSACTION - NO PNR PRESENT IN WORK AREA", self.output.messages)

    def test_eta1_el_plus_off_queue(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="EL+").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("$$UIO1$$.2", self.output.last_line, self.output.last_node)
        off_queue = "CANNOT DO THIS IF OFF QUEUE"
        self.assertIn(off_queue + (50 - len(off_queue)) * " ", self.output.messages)

    def test_eta1_el_off_queue(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="EL").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAX265.6", self.output.last_line, self.output.last_node)
        self.assertIn("UNABLE TO END TRANSACTION - NO PNR PRESENT IN WORK AREA", self.output.messages)
