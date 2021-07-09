from base64 import b64encode

from p1_utils.data_type import DataType
from p2_assembly.mac2_data_macro import macros
from p3_db.pnr import RCVD_FROM, PHONE, NAME, HEADER
from p3_db.test_data_elements import FixedFile, FileItem
from p8_test.test_local import TestDebug


class ExaaTest(TestDebug):

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

    def _mini_tjr_setup(self, tj2qaa) -> None:
        fixed_file = FixedFile()
        fixed_file.rec_id = DataType("C", input="P9").value
        fixed_file.macro_name = "TJ2TJ"
        fixed_file.fixed_type = macros["SYSEQC"].evaluate("#PR9RI")  # 390
        fixed_file.fixed_ordinal = 0x17F // macros["TJ2TJ"].evaluate("#TJ2MAX")  # 38  0x26
        item = FileItem()
        item.macro_name = "TJ2TJ"
        item.field = "TJ2ITM"
        item.adjust = True
        item.field_data = [
            {
                "field": "TJ2QAA",
                "data": b64encode(DataType("X", input=tj2qaa).to_bytes()).decode()
            },
        ]
        item.repeat = 0x17F % macros["TJ2TJ"].evaluate("#TJ2MAX") + 1  # 4
        fixed_file.file_items.append(item)
        file_dict = fixed_file.doc_to_dict()
        file_dict["file_items"] = [item.doc_to_dict() for item in fixed_file.file_items]
        self.test_data.create_fixed_file(file_dict, persistence=False)
        return

    def test_exaa_npty_family(self) -> None:
        self._setup_output_pnr_header()
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["3ZAVERI/NAYAN/PURVI/SANAY", "4SHAH"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        self._mini_tjr_setup("00")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertIn("OK", self.output.messages[0], self.output.debug)
        self.assertEqual("0007", test_data.get_pnr_field("PR00_20_PTY"))

    def test_exaa_npty_corporate(self) -> None:
        self._setup_output_pnr_header()
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["C/6TOURS", "4SHAH", "I/3BABY"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        self._mini_tjr_setup("00")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertIn("OK", self.output.messages[0], self.output.debug)
        self.assertEqual("0009", test_data.get_pnr_field("PR00_20_PTY"))

    def test_et2_direct(self) -> None:
        self._setup_output_pnr_header()
        self.test_data.set_field("WA0PTY", DataType("X", input="03").to_bytes())
        self.test_data.add_pnr_element(["3ZAVERI/NAYAN/PURVI/SANAY"], NAME)
        test_data = self.tpf_server.run("EWA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertEqual("0003", test_data.get_pnr_field("PR00_20_PTY"))
