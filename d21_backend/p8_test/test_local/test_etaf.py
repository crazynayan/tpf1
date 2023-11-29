from d21_backend.p1_utils.data_type import DataType
from d21_backend.p8_test.test_local import TestDebug


class EtafTest(TestDebug):
    DEBUG_DATA = list()
    SEGMENT = "ETAF"

    def test_etaf_vanilla(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAF1300.1", self.output.last_line, self.output.last_node)
        self.assertIn("ITINERARY REQUIRED TO COMPLETE TRANSACTION", self.output.messages)
        self.assertEqual(list(), self.output.dumps)

    def test_etaf_itinerary(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAZ1950.1", self.output.last_line, self.output.last_node)
        self.assertIn("NEED RECEIVED FROM FIELD - USE 6", self.output.messages)
        self.assertEqual(list(), self.output.dumps)
