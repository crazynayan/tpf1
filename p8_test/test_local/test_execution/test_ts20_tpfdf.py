import unittest

from p3_db.tpfdf import Tpfdf
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS
from p8_test.test_local.test_eta5_execution import tr1gaa


class DbTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_fields(["EBW000"], "EB0EB")
        self.test_data.add_all_regs()

    def test_ts20_tpfdf(self):
        self.test_data.add_tpfdf(tr1gaa, "40", "TR1GAA")
        test_data = self.tpf_server.run("TS20", self.test_data)
        self.assertEqual(21, test_data.output.regs["R0"])
        self.assertEqual("80", test_data.get_field("EBW000"))
        self.assertEqual(1, len(Tpfdf.DB[0]["doc"]))

    def test_ts20_dbdel_all_keys(self):
        self.test_data.add_tpfdf(tr1gaa, "40", "TR1GAA")
        self.test_data.set_field("EBX000", bytes([0x02]))
        self.tpf_server.run("TS20", self.test_data)
        self.assertEqual(0, len(Tpfdf.DB[0]["doc"]))

    def test_ts20_dbdel_all(self):
        self.test_data.add_tpfdf(tr1gaa, "40", "TR1GAA")
        self.test_data.set_field("EBX000", bytes([0x03]))
        self.tpf_server.run("TS20", self.test_data)
        self.assertEqual(0, len(Tpfdf.DB[0]["doc"]))

    def test_ts20_dbmod(self):
        self.test_data.add_tpfdf(tr1gaa, "40", "TR1GAA")
        self.test_data.set_field("EBX000", bytes([0x04]))
        self.tpf_server.run("TS20", self.test_data)
        self.assertEqual(bytearray([0xC1, 0xC1, 0xC1]), Tpfdf.DB[0]["doc"][0]["data"][116:119])


if __name__ == "__main__":
    unittest.main()
