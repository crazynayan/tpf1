from base64 import b64encode

from p1_utils.data_type import DataType
from p2_assembly.mac2_data_macro import macros
from p3_db.pnr import RCVD_FROM, PHONE, NAME
from p3_db.test_data_elements import FixedFile, FileItem
from p8_test.test_local import TestDebug


class Etg1Test(TestDebug):

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

    def _main_tjr_setup(self):
        fixed_file = FixedFile()
        fixed_file.rec_id = DataType("C", input="TJ").value
        fixed_file.macro_name = "TJ0TJ"
        fixed_file.fixed_type = macros["SYSEQC"].evaluate("#TJRRI")
        fixed_file.fixed_ordinal = 0x17F
        fixed_file.field_data = [
            {
                "field": "TJ0BID",
                "data": b64encode(DataType("C", input="TJ").to_bytes()).decode()
            },

        ]
        file_dict = fixed_file.doc_to_dict()
        self.test_data.create_fixed_file(file_dict, persistence=False)

    def test_etg1_tjr(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["1ZAVERI/NAYAN"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        self._mini_tjr_setup("00")
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.SUCCESS_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertEqual(list(), self.output.messages)

    def test_etg1_insurance_no_main_tjr(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["1ZAVERI/NAYAN"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        self._mini_tjr_setup(f"{macros['TJ2TJ'].evaluate('#TJ2IBB'):02X}")  # 20
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual("INS0ER01.2", self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertIn("C9D501", self.output.dumps)

    def test_etg1_insurance_main_tjr(self) -> None:
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0POR", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0ADN", DataType("X", input="00017F").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input="10").to_bytes())
        self.test_data.add_pnr_element(["1ZAVERI/NAYAN"], NAME)
        self.test_data.add_pnr_element(["NAYAN"], RCVD_FROM)
        self.test_data.add_pnr_element(["123456"], PHONE)
        self._mini_tjr_setup(f"{macros['TJ2TJ'].evaluate('#TJ2IBB'):02X}")  # 20
        self._main_tjr_setup()
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(self.FMSG_END, self.output.last_line, f"{self.output.last_node}--{self.output.dumps}")
        self.assertIn("WOULD YOU LIKE TO PURCHASE TRAVEL PROTECTION ENTER INS/  /PSGR NBR TO SELL INSURANCE OR INS"
                      "NO TO DECLINE", self.output.messages, self.output.debug)
        self.assertEqual(list(), self.output.dumps)
