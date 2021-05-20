from p1_utils.data_type import DataType
from p3_db.pnr import RCVD_FROM, PHONE, NAME
from p8_test.test_local import TestDebug


class EtawTest(TestDebug):

    def test_etaw_vanilla(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.add_pnr_element(["1ZAVERI/NAYAN"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("FMSG0100", self.output.last_line, self.output.last_node)
        self.assertIn("INVLD ITIN", self.output.messages, self.output.get_traces("ETAW"))
