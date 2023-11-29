from d21_backend.p1_utils.data_type import DataType
from d21_backend.p8_test.test_local import TestDebug


class EtaxTest(TestDebug):
    SEGMENT = "ETAX"
    DEBUG_DATA = list()

    def test_etax_vanilla(self):
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAX265.6", self.output.last_line, self.output.last_node)
        self.assertIn("UNABLE TO END TRANSACTION - NO PNR PRESENT IN WORK AREA", self.output.messages)
        self.assertEqual(list(), self.output.dumps)

    def test_etax_efp(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="EFP").to_bytes())
        self.test_data.add_fields(["UI2CNN"], "UI2PF", "R7")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("$$UIO1$$.2", self.output.last_line, self.output.last_node)
        self.assertEqual("33", test_data.get_field("UI2CNN"))

    def test_etax_efc(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="EF$").to_bytes())
        self.test_data.add_fields(["UI2CNN"], "UI2PF", "R7")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("$$UIO1$$.2", self.output.last_line, self.output.last_node)
        self.assertEqual("33", test_data.get_field("UI2CNN"))

    def test_etax_efs(self):
        self.test_data.set_field("MI0ACC", DataType("C", input="EF*").to_bytes())
        self.test_data.add_fields(["UI2CNN"], "UI2PF", "R7")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAX265.6", self.output.last_line, self.output.last_node)
        self.assertIn("UNABLE TO END TRANSACTION - NO PNR PRESENT IN WORK AREA", self.output.messages)
