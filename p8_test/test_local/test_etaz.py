from p1_utils.data_type import DataType
from p3_db.pnr import RCVD_FROM
from p8_test.test_local import TestDebug


class EtazTest(TestDebug):
    DEBUG_DATA = list()
    SEGMENT = "ETAZ"

    def test_etaz_vanilla(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAZ1950.1", self.output.last_line, self.output.last_node)
        self.assertIn("NEED RECEIVED FROM FIELD - USE 6", self.output.messages)
        self.assertEqual(list(), self.output.dumps)

    def test_etaz_rcvd_from(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("FMSG0100", self.output.last_line, self.output.last_node)
        self.assertIn("NEED PHONE FIELD - USE 9", self.output.messages)
