from base64 import b64encode

from p1_utils.data_type import DataType
from p2_assembly.mac2_data_macro import macros
from p3_db.pnr import RCVD_FROM, PHONE, NAME
from p3_db.test_data_elements import FixedFile, FileItem
from p8_test.test_local import TestDebug


class ExaaTest(TestDebug):

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
        self.test_data.add_fields(fields=["PR00_20_PTY"], macro_name="PR001W", base_reg="R2")
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
        # TODO Fix retrieval from PR001W
        # self.assertEqual("0007", test_data.get_field("PR00_20_PTY"))

    def test_exaa_npty_corporate(self) -> None:
        self.test_data.add_fields(fields=["PR00_20_PTY"], macro_name="PR001W", base_reg="R2")
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
        # self.assertEqual("0009", test_data.get_field("PR00_20_PTY"))
