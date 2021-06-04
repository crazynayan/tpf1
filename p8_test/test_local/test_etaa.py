from p1_utils.data_type import DataType
from p3_db.pnr import RCVD_FROM, PHONE, NAME, REMARKS
from p8_test.test_local import TestDebug


class EtaaTest(TestDebug):

    def test_etaa_remarks(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["1ZAVERI/NAYAN"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        self.test_data.add_pnr_element(["SOME REMARKS"], REMARKS)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.ETG1_TJR_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertIn("019005", self.output.dumps)  # TJR Face Error

    def test_etaa_remarks_insurance(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["1ZAVERI/NAYAN"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        self.test_data.add_pnr_element(["I$INSURANCE SEGMENT"], REMARKS)
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("ETAA590.2", self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertIn("5I$ REMARK EXISTS-NEED INS SEGMENT OR REMOVE 5I$ REMARK", self.output.messages)
