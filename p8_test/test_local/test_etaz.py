from base64 import b64encode

from p1_utils.data_type import DataType
from p2_assembly.mac2_data_macro import macros
from p3_db.pnr import RCVD_FROM, ITIN
from p3_db.test_data_elements import FixedFile
from p8_test.test_local import TestDebug

macros["WI0BS"].load()
macros["WA0AA"].load()
wi0act = f"{macros['WI0BS'].evaluate('#WI0ACT'):02X}"
wa0tvl = f"{macros['WA0AA'].evaluate('#WA0TVL'):02X}"
wa0sec = f"{macros['WA0AA'].evaluate('#WA0SEC'):02X}"
itin = f"WI0TYP:{wi0act}:I1,WI0AAC:{bytes('GN', 'CP037').hex()}:I1"


class EtazTest(TestDebug):

    def _tjr_setup(self) -> None:
        fixed_file = FixedFile()
        fixed_file.rec_id = DataType("C", input="TJ").value
        fixed_file.macro_name = "TJ0TJ"
        fixed_file.fixed_type = macros["SYSEQC"].evaluate("#TJRRI")
        fixed_file.fixed_ordinal = 0x17F
        fixed_file.field_data = [
            {
                "field": "TJ0PCC",
                "data": b64encode(DataType("C", input="B4T").to_bytes()).decode()
            },
        ]
        file_dict = fixed_file.cascade_to_dict()
        del file_dict["id"]
        self.test_data.create_fixed_file(file_dict, persistence=False)
        return

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

    def test_etaz_wa0lnb(self) -> None:
        self.test_data.add_fields([("EBT060", 3)], "EB0EB")
        self.test_data.set_global_field("@TJORD", "00088EDC")
        self.test_data.set_field("WA0ET5", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0ASC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0TSC", DataType("X", input="01").to_bytes())
        self.test_data.set_field("WA0FNS", DataType("X", input=wa0tvl).to_bytes())
        self.test_data.set_field("WA0LNB", DataType("X", input="02").to_bytes())
        self.test_data.set_field("WA0CM1", DataType("X", input=wa0sec).to_bytes())
        self.test_data.add_pnr_element(["TA/B4T0"], RCVD_FROM)
        self.test_data.add_pnr_field_data(itin, ITIN)
        self._tjr_setup()
        test_data = self.tpf_server.run("ETA1", self.test_data)
        self.output = test_data.output
        self.assertEqual(DataType("C", input="B4T").encode, test_data.get_field("EBT060"))
        self.assertEqual("$$UIO1$$.2", self.output.last_line, self.output.last_node)
        self.assertIn("UNABL", self.output.messages)
