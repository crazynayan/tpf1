import unittest

from d21_backend.config import config
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class NonConditional1(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_all_regs()
        aaa_fields = [("WA0BBR", 2), ("WA0QHR", 6), "WA0TKK", "WA0TY1"]
        self.test_data.add_fields(aaa_fields, "WA0AA")
        ecb_fields = [("EBW001", 6), ("EBW008", 6), "EBW000", "EBW016", "EBW017", "EBW018",
                      ("EBX000", 4), ("EBX004", 4), ("EBX008", 4), ("EBX012", 4), ("EBX016", 4)]
        self.test_data.add_fields(ecb_fields, "EB0EB")

    def test_ts14(self):
        macros = get_macros()
        test_data = self.tpf_server.run("TS14", self.test_data)
        aaa = self.tpf_server.aaa_address
        self.assertEqual(0xFFFFC1C1, test_data.get_unsigned_value("R2"))
        self.assertEqual("C1C1", test_data.get_field("WA0BBR"))
        self.assertEqual("00000000C1C1", test_data.get_field("WA0QHR"))
        self.assertEqual(2, test_data.output.regs["R3"])
        self.assertEqual("02", test_data.get_field("WA0TKK"))
        self.assertEqual(2, test_data.output.regs["R5"])
        self.assertEqual(-2, test_data.output.regs["R6"])
        self.assertEqual(4, test_data.output.regs["R7"])
        self.assertEqual(2, test_data.output.regs["R10"])
        self.assertEqual(0x00000100, test_data.output.regs["R4"])
        self.assertEqual(0x00000000, test_data.output.regs["R11"])
        self.assertEqual(-1, test_data.output.regs["R12"])
        self.assertEqual(aaa + macros["WA0AA"].evaluate("WA0TKK"), test_data.output.regs["R13"])
        self.assertEqual(aaa + macros["WA0AA"].evaluate("WA0DAR") + 1, test_data.output.regs["R14"])
        self.assertEqual(5, test_data.output.regs["R15"])
        self.assertEqual("02", test_data.get_field("EBW000"))
        self.assertEqual("40" * 6, test_data.get_field("EBW001"))
        self.assertEqual("00" * 6, test_data.get_field("EBW008"))
        self.assertTrue(self.tpf_server.vm.is_updated(config.ECB + 16, 6))
        self.assertFalse(self.tpf_server.vm.is_updated(config.ECB + 15, 1))
        self.assertEqual("42", test_data.get_field("EBW016"))
        self.assertEqual("40", test_data.get_field("EBW017"))
        self.assertEqual(f"{macros['WA0AA'].evaluate('#WA0GEN'):02X}", test_data.get_field("WA0TY1"))
        self.assertTrue(self.tpf_server.vm.is_updated_bit(aaa + 0x030, 0x80))
        self.assertFalse(self.tpf_server.vm.is_updated_bit(aaa + 0x030, 0x40))
        self.assertEqual(f"{0xFF - macros['WA0AA'].evaluate('#WA0GEN'):02X}",
                         test_data.get_field("EBW018"))
        self.assertEqual(272, test_data.output.regs["R0"])
        self.assertEqual(5, int(test_data.get_field("EBX000"), 16))
        self.assertEqual(3, int(test_data.get_field("EBX004"), 16))
        self.assertEqual(0, int(test_data.get_field("EBX008"), 16))
        self.assertEqual(6144, int(test_data.get_field("EBX012"), 16))
        self.assertEqual(100, int(test_data.get_field("EBX016"), 16))


if __name__ == "__main__":
    unittest.main()
