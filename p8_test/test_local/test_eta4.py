from p1_utils.data_type import DataType
from p3_db.pnr import RCVD_FROM, PHONE
from p8_test.test_local import TestDebug


class Eta4Test(TestDebug):
    DEBUG_DATA = list()
    SEGMENT = "ETA4"

    def test_eta4_vanilla(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETA5420.9", self.output.last_line, self.output.last_node)
        self.assertIn("NEED NAME IN PNR TO COMPLETE TRANSACTION", self.output.messages)

    def test_eta4_tvl(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETA5420.9", self.output.last_line, self.output.last_node)
        self.assertIn("NEED NAME IN PNR TO COMPLETE TRANSACTION", self.output.messages)
