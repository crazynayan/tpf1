import unittest

from p3_db.pnr import ITIN
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class Exb1Test(unittest.TestCase):

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.stop_segments = ["EXB2"]
        self.pnr_output_body = {
            "locator": str(),
            "key": ITIN,
            "field_item_len": "PR00_G0_BAS_0_BIT_IND:I1, PR00_G0_BAS_0_BIT_IND:I2"
        }

    def test_exb1_simple(self):
        self.test_data.create_pnr_output(self.pnr_output_body, persistence=False)
        self.test_data.add_pnr_field_data("PR00_G0_TYP:01:I1, PR00_G0_BAS_0_BIT_IND:04:I1, PR00_G0_BAS_0_AAC:E2E2:I1, "
                                          "PR00_G0_TYP:02:I2, PR00_G0_BAS_0_AAC:C8D2:I2", key=ITIN)
        test_data = self.tpf_server.run("EXB1", self.test_data)
        self.assertEqual("EXB1NNSS.5", test_data.output.last_line, test_data.output.last_node)
        self.assertEqual("03", test_data.get_pnr_field("PR00_G0_BAS_0_BIT_IND", item_number=1))
        self.assertEqual("05", test_data.get_pnr_field("PR00_G0_BAS_0_BIT_IND", item_number=2))

    def test_exb1_ox_status_check(self):
        self.test_data.create_pnr_output(self.pnr_output_body, persistence=False)
        self.test_data.add_pnr_field_data("PR00_G0_TYP:01:I1, PR00_G0_BAS_0_AAC:D6E7:I1, PR00_G0_BAS_0_BIT_IND:04:I1,"
                                          "PR00_G0_TYP:02:I2, PR00_G0_BAS_0_AAC:C8D2:I2, PR00_G0_BAS_0_BIT_IND:04:I2",
                                          key=ITIN)
        test_data = self.tpf_server.run("EXB1", self.test_data)
        self.assertEqual("EXB1NNSS.5", test_data.output.last_line, test_data.output.last_node)
        self.assertEqual("03", test_data.get_pnr_field("PR00_G0_BAS_0_BIT_IND", item_number=1))
        self.assertEqual("04", test_data.get_pnr_field("PR00_G0_BAS_0_BIT_IND", item_number=2))

    def test_exb1_double_connection(self):
        self.pnr_output_body["field_item_len"] = "PR00_G0_BAS_0_BIT_IND:I1, PR00_G0_BAS_0_BIT_IND:I2, " \
                                                 "PR00_G0_BAS_0_BIT_IND:I3"
        self.test_data.create_pnr_output(self.pnr_output_body, persistence=False)
        self.test_data.add_pnr_field_data("PR00_G0_BAS_0_AAC:C8D2:I1, PR00_G0_BRD:C1C1C1:I1, PR00_G0_OFF:C2C2C2:I1,"
                                          "PR00_G0_BAS_0_AAC:C8D2:I2, PR00_G0_BRD:C2C2C2:I2, PR00_G0_OFF:C3C3C3:I2,"
                                          "PR00_G0_BAS_0_AAC:C8D2:I3, PR00_G0_BRD:C3C3C3:I3, PR00_G0_OFF:C4C4C4:I3",
                                          key=ITIN)
        test_data = self.tpf_server.run("EXB1", self.test_data)
        self.assertEqual("EXB1NNSS.5", test_data.output.last_line, test_data.output.last_node)
        self.assertEqual("03", test_data.get_pnr_field("PR00_G0_BAS_0_BIT_IND", item_number=1))
        self.assertEqual("07", test_data.get_pnr_field("PR00_G0_BAS_0_BIT_IND", item_number=2))
        self.assertEqual("05", test_data.get_pnr_field("PR00_G0_BAS_0_BIT_IND", item_number=3))
