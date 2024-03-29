from d21_backend.p1_utils.data_type import DataType
from d21_backend.p3_db.pnr import RCVD_FROM, PHONE, NAME
from d21_backend.p8_test.test_local import TestDebug


class Eta6Test(TestDebug):

    def test_eta6_vanilla(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["1ZAVERI/NAYAN"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETG1_TJR_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertIn("019005", self.output.dumps)  # TJR Face Error
        self.assertEqual(list(), self.output.messages, self.output.get_traces("ETAW"))

    def test_eta6_abacus(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.set_field("WA0PHA", DataType("X", input="03").to_bytes())
        self.test_data.add_pnr_element(["1ZAVERI/NAYAN"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        self.test_data.create_ecb_level({"variation": 0, "variation_name": str(), "ecb_level": "2", "hex_data": str(),
                                         "field_data": str(), "seg_name": str()}, persistence=False)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.FMSG_END, self.output.last_line, self.output.messages)
        self.assertIn("INVALID REQUEST FOR RECORD IN TTK4", self.output.messages, self.output.get_traces("ETAW"))
