import unittest

from d21_backend.p3_db.flat_file import FlatFile
from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class Ts28Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_fields([("EBW000", 4), ("EBW004", 4)], "EB0EB")
        self.test_data.add_fields(["WA0ET1", "WA0ET2"], "WA0AA")
        self.test_data.add_all_regs()

    def test_ts28_getfc(self):
        test_data = self.tpf_server.run("TS28", self.test_data)
        self.assertListEqual(list(), test_data.output.messages, test_data.output.last_node)
        file_address1 = int(test_data.get_field("EBW000"), 16)
        file_address2 = int(test_data.get_field("EBW004"), 16)
        data1 = FlatFile.get_record(file_address1)
        data2 = FlatFile.get_record(file_address2)
        self.assertIsNotNone(data1)
        self.assertIsNotNone(data2)
        self.assertEqual(bytearray([0xB1, 0xB2, 0x00, 0x00]), data1)
        self.assertEqual(bytearray([0xC1, 0x00, 0x00, 0x00]), data2)
        # SONIC Checks
        self.assertEqual(2, test_data.output.regs["R12"])
        self.assertEqual(3, test_data.output.regs["R14"])
        # AAINT checks
        self.assertEqual("00", test_data.get_field("WA0ET1"))
        self.assertEqual("02", test_data.get_field("WA0ET2"))


if __name__ == "__main__":
    unittest.main()
