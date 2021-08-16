from base64 import b64encode

from p1_utils.data_type import DataType
from p8_test.test_local.test_eta5_execution import NameGeneral


class Variation(NameGeneral):

    def test_multiple_name(self):
        self.test_data.add_pnr_element(["2ZAVERI", "6SHAH"], "name", variation=0)
        self.test_data.add_pnr_element(["C/21TOURS", "2ZAVERI", "6SHAH"], "name", variation=1)
        self.test_data.add_pnr_element(["2ZAVERI", "6SHAH", "I/3ZAVERI"], "name", variation=2)
        self.test_data.add_pnr_element(["C/21TOURS", "2ZAVERI", "6SHAH", "I/3ZAVERI"], "name", variation=3)
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.assertEqual("F0F0", test_data.get_field("WA0EXT", pnr_variation=0))
        self.assertEqual("F1F3", test_data.get_field("WA0EXT", pnr_variation=1))
        self.assertEqual("F0F0", test_data.get_field("WA0EXT", pnr_variation=2))
        self.assertEqual("F1F3", test_data.get_field("WA0EXT", pnr_variation=3))
        self.assertEqual(f"{8:02X}", test_data.get_field("WA0PTY", pnr_variation=0))
        self.assertEqual(f"{21:02X}", test_data.get_field("WA0PTY", pnr_variation=1))
        self.assertEqual(f"{11:02X}", test_data.get_field("WA0PTY", pnr_variation=2))
        self.assertEqual(f"{24:02X}", test_data.get_field("WA0PTY", pnr_variation=3))
        self.assertEqual(f"{0:02X}", test_data.get_field("WA0PTI", pnr_variation=0))
        self.assertEqual(f"{0:02X}", test_data.get_field("WA0PTI", pnr_variation=1))
        self.assertEqual(f"{3:02X}", test_data.get_field("WA0PTI", pnr_variation=2))
        self.assertEqual(f"{3:02X}", test_data.get_field("WA0PTI", pnr_variation=3))

    def test_WA0PN2_group(self):
        self.test_data.add_pnr_element(["C/99W/TOURS", "3SHAH"], "name", variation=0)
        self.test_data.add_pnr_element(["C/999W/TOURS", "3SHAH"], "name", variation=1)
        self.test_data.add_pnr_element(["Z/99W/TOURS", "3SHAH"], "name", variation=2)
        self.test_data.set_field("WA0UB1", bytes([0x00]), variation=0)
        self.test_data.set_field("WA0UB1", bytes([0x80]), variation=1)
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.assertEqual("F9F6", test_data.get_field("WA0EXT", core_variation=0, pnr_variation=0))
        self.assertEqual("F9F6", test_data.get_field("WA0EXT", core_variation=0, pnr_variation=1))
        self.assertEqual("F9F6", test_data.get_field("WA0EXT", core_variation=0, pnr_variation=2))
        self.assertEqual("F0F6", test_data.get_field("WA0EXT", core_variation=1, pnr_variation=0))
        self.assertEqual("F9F6", test_data.get_field("WA0EXT", core_variation=1, pnr_variation=1))
        self.assertEqual("F9F6", test_data.get_field("WA0EXT", core_variation=1, pnr_variation=2))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY", core_variation=0, pnr_variation=0))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY", core_variation=0, pnr_variation=1))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY", core_variation=0, pnr_variation=2))
        self.assertEqual(f"{9:02X}", test_data.get_field("WA0PTY", core_variation=1, pnr_variation=0))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY", core_variation=1, pnr_variation=1))
        self.assertEqual(f"{99:02X}", test_data.get_field("WA0PTY", core_variation=1, pnr_variation=2))
        # for core_variation, pnr_variation in product(range(2), range(3)):
        #     self.assertIn("OK", test_data.get_output(core_variation, pnr_variation).messages[0])

    def test_tpfdf_variation(self):
        self.test_data.set_field("WA0ET6", bytes([0x10]))
        self.test_data.add_pnr_element(["1ZAVERI"], "name")
        self.test_data.add_pnr_element(["SSRFQTUAA2812Y20OCTDFW  ORD  0510GLD*DGHWCL RR    "], "hfax")
        self.test_data.add_pnr_field_data([{
            "PR00_60_FQT_CXR": b64encode(DataType("C", input="AA").to_bytes()).decode(),
            "PR00_60_FQT_FTN": b64encode(DataType("C", input="NKE9087").to_bytes()).decode(),
            "PR00_60_FQT_TYP": b64encode(DataType("X", input="80").to_bytes()).decode(),
        }], "fqtv", "DGHWCL")
        self.test_data.add_pnr_field_data([{
            "WI0ARC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
            "WI0FNB": b64encode(DataType("H", input="2812").to_bytes()).decode(),
            "WI0DTE": b64encode(DataType("X", input="4E2F").to_bytes()).decode(),
            "WI0BRD": b64encode(DataType("C", input="DFW").to_bytes()).decode(),
            "WI0OFF": b64encode(DataType("C", input="ORD").to_bytes()).decode(),
        }], "itin", "DGHWCL")
        self.test_data.add_pnr_element(["1ZAVERI"], "name", variation=1)
        self.test_data.add_pnr_element(["SSRFQTUAA2812Y20OCTDFW  ORD  0510GLD*DGHWCL RR    "], "hfax", variation=1)
        self.test_data.add_pnr_field_data([{
            "PR00_60_FQT_CXR": b64encode(DataType("C", input="AA").to_bytes()).decode(),
            "PR00_60_FQT_FTN": b64encode(DataType("C", input="NKE9087").to_bytes()).decode(),
            "PR00_60_FQT_TYP": b64encode(DataType("X", input="40").to_bytes()).decode(),
        }], "fqtv", "DGHWCL", variation=1)
        self.test_data.add_tpfdf([{
            "TR1G_40_OCC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
            "TR1G_40_ACSTIERCODE": b64encode(DataType("C", input="GLD").to_bytes()).decode(),
            "TR1G_40_TIER_EFFD": b64encode(DataType("X", input="47D3").to_bytes()).decode(),
            "TR1G_40_TIER_DISD": b64encode(DataType("X", input="7FFF").to_bytes()).decode(),
            "TR1G_40_PTI": b64encode(DataType("X", input="80").to_bytes()).decode(),
        }], "40", "TR1GAA", variation=0)
        self.test_data.add_tpfdf([{
            "TR1G_40_OCC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
            "TR1G_40_ACSTIERCODE": b64encode(DataType("C", input="EXP").to_bytes()).decode(),
            "TR1G_40_TIER_EFFD": b64encode(DataType("X", input="47D3").to_bytes()).decode(),
            "TR1G_40_TIER_DISD": b64encode(DataType("X", input="7FFF").to_bytes()).decode(),
            "TR1G_40_PTI": b64encode(DataType("X", input="40").to_bytes()).decode(),
        }], "40", "TR1GAA", variation=1)
        test_data = self.tpf_server.run("ETA5", self.test_data)
        self.assertEqual(self.ETK2_END, test_data.outputs[0].last_line)
        self.assertEqual(self.IGR1_END, test_data.outputs[1].last_line)
        self.assertEqual(self.ETK2_END, test_data.outputs[2].last_line)
        self.assertEqual(self.IGR1_END, test_data.outputs[3].last_line)
        self.assertEqual("60", test_data.get_field("EBRS01", pnr_variation=0, tpfdf_variation=0))
        self.assertEqual("00", test_data.get_field("EBRS01", pnr_variation=0, tpfdf_variation=1))
        self.assertEqual("60", test_data.get_field("EBRS01", pnr_variation=1, tpfdf_variation=0))
        self.assertEqual("00", test_data.get_field("EBRS01", pnr_variation=1, tpfdf_variation=1))
        self.assertEqual(116, test_data.outputs[0].regs["R6"])
        self.assertEqual(116, test_data.outputs[2].regs["R6"])
        self.assertEqual("00", test_data.get_field("WA0PTY", pnr_variation=0, tpfdf_variation=0))
        self.assertEqual("01", test_data.get_field("WA0PTY", pnr_variation=0, tpfdf_variation=1))
        self.assertEqual("00", test_data.get_field("WA0PTY", pnr_variation=1, tpfdf_variation=0))
        self.assertEqual("01", test_data.get_field("WA0PTY", pnr_variation=1, tpfdf_variation=1))
