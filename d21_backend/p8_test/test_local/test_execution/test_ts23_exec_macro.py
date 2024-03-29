import unittest

from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class Ts23Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_fields([("EBW000", 28), "CE1$UID"], "EB0EB")
        self.test_data.add_fields(["@HAALC"], "GLOBAS")
        self.test_data.add_all_regs()

    def test_ts23_alasc_mhinf_div_in_equ(self):
        test_data = self.tpf_server.run("TS23", self.test_data)
        self.assertEqual("00000001000000020000000300000004000000050000000600000007", test_data.get_field("EBW000"))
        self.assertEqual("E5E7", test_data.get_field("@HAALC"))  # Test MHINF
        self.assertEqual("44", test_data.get_field("CE1$UID"))  # Test MHINF
        self.assertEqual(1, test_data.output.regs["R11"])  # Test PRIMA
        self.assertEqual(1, test_data.output.regs["R12"])  # Test MCPCK
        self.assertEqual(2, test_data.output.regs["R13"])  # Test DIVISION IN EQU

    def test_ts23_prima_1f(self):
        self.test_data.set_field("WA0PHA", bytes([0x02]))
        test_data = self.tpf_server.run("TS23", self.test_data)
        self.assertEqual(4, test_data.output.regs["R11"])

    def test_ts23_prima_1b(self):
        self.test_data.set_field("WA0PHA", bytes([0x03]))
        test_data = self.tpf_server.run("TS23", self.test_data)
        self.assertEqual(5, test_data.output.regs["R11"])

    def test_ts23_mcpck(self):
        self.test_data.partition = "LA"
        test_data = self.tpf_server.run("TS23", self.test_data)
        self.assertEqual(2, test_data.output.regs["R12"])

    def test_ts23_date(self):
        self.test_data.set_field("EBX000", bytes([0x01]))
        self.test_data.add_reg({"reg": "R0", "value": 0x5109})
        test_data = self.tpf_server.run("TS23", self.test_data)
        self.assertEqual(bytes("20OCT2022", "cp037").hex().upper(), test_data.get_field("EBW000")[:18])


if __name__ == "__main__":
    unittest.main()
