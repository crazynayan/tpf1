import unittest

from d21_backend.p4_execution.ex5_execute import TpfServer
from d21_backend.p8_test.test_local import TestDataUTS


class Ts27Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.add_fields(["EBW010", "EBW020", "EBW030"], "EB0EB")
        self.test_data.set_global_field("@FLIFO2", "11")
        self.test_data.set_global_field("@SHPDD", "22")
        self.test_data.set_global_field("@@SWITCH", "33")
        self.test_data.set_global_record("@MH00F", str(), str())

    def test_ts27_assembler_globals(self):
        test_data = self.tpf_server.run("TS27", self.test_data)
        self.assertListEqual(list(), test_data.output.messages)
        self.assertEqual("11", test_data.get_field("EBW010"))
        self.assertEqual("22", test_data.get_field("EBW020"))
        self.assertEqual("33", test_data.get_field("EBW030"))

    def test_ts27_listing_globals(self):
        self.test_data.set_field("EBW000", bytes([0xD3]))  # Set EBW000 = 'L' for listing
        test_data = self.tpf_server.run("TS27", self.test_data)
        self.assertListEqual(list(), test_data.output.messages)
        self.assertEqual("11", test_data.get_field("EBW010"))
        self.assertEqual("22", test_data.get_field("EBW020"))
        self.assertEqual("33", test_data.get_field("EBW030"))


if __name__ == "__main__":
    unittest.main()
