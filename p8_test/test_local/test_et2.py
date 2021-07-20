from p1_utils.data_type import DataType
from p3_db.pnr import NAME, HEADER
from p8_test.test_local import TestDebug


class Et2Test(TestDebug):

    def _setup_output_pnr_header(self) -> None:
        pnr_dict: dict = {
            "key": HEADER,
            "field_len": {
                "PR00_20_PTY": 0,
                "PR00_20_TIM": 0,
                "PR00_20_DUT": 0,
            },
        }
        self.test_data.create_pnr_output(pnr_output_dict=pnr_dict, persistence=False)

    def test_et2_direct(self) -> None:
        self._setup_output_pnr_header()
        self.test_data.set_field("WA0PTY", DataType("X", input="03").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.add_pnr_element(["3ZAVERI/NAYAN/PURVI/SANAY"], NAME)
        test_data = self.tpf_server.run("EWA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.IGR1_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertEqual("0003", test_data.get_pnr_field("PR00_20_PTY"))
