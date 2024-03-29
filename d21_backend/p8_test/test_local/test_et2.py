from base64 import b64encode

from d21_backend.p1_utils.data_type import DataType
from d21_backend.p3_db.pnr import NAME, HEADER, ITIN
from d21_backend.p8_test.test_local import TestDebug


class Et2Test(TestDebug):

    def setUp(self) -> None:
        super().setUp()
        self.test_data.set_global_record("@APCIB", field_data=str(), seg_name=str())
        pnr_dict: dict = {
            "locator": str(),
            "key": HEADER,
            "field_item_len": "PR00_20_PTY, PR00_20_TIM, PR00_20_DUT",
        }
        heap_body: dict = {
            "heap_name": "TP5TI",
            "hex_data": str(),
            "field_data": str(),
            "seg_name": str(),
            "variation": 0,
            "variation_name": str()
        }
        self.test_data.create_heap(heap_body, persistence=False)
        self.test_data.create_pnr_output(body=pnr_dict, persistence=False)

    def _setup_input_itin(self) -> None:
        itin_input = [
            {
                "WI0SZE": b64encode(DataType("X", input="F0").to_bytes()).decode(),
                "WI0ARC": b64encode(DataType("C", input="BA").to_bytes()).decode(),
                "WI0TYP": b64encode(DataType("X", input="04").to_bytes()).decode(),
            }
        ]
        self.test_data.add_pnr_field_data(itin_input, ITIN)

    def test_without_itin(self) -> None:
        self.test_data.set_field("WA0PTY", DataType("X", input="03").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.add_pnr_element(["3ZAVERI/NAYAN/PURVI/SANAY"], NAME)
        test_data = self.tpf_server.run("EWA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertEqual("0003", test_data.get_pnr_field("PR00_20_PTY"))

    def test_with_itin(self) -> None:
        self.test_data.set_field("WA0PTY", DataType("X", input="03").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.add_pnr_element(["3ZAVERI/NAYAN/PURVI/SANAY"], NAME)
        self._setup_input_itin()
        test_data = self.tpf_server.run("EWA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertEqual("0003", test_data.get_pnr_field("PR00_20_PTY"))
