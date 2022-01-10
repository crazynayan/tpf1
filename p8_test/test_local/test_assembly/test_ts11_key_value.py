import unittest

from config import config
from p2_assembly.seg3_ins_type import RegisterData
from p2_assembly.seg5_exec_macro import KeyValue
from p2_assembly.seg6_segment import Segment
from p2_assembly.seg9_collection import seg_collection


class KeyValueTest(unittest.TestCase):
    # noinspection SpellCheckingInspection
    def test_key_value(self):
        seg: Segment = seg_collection.get_seg("TS11")
        seg.assemble()
        # AAGET BASEREG=R1,GET=CORE,INIT=YES,FILE=NO
        node: KeyValue = seg.nodes["TS110010.1"]
        self.assertEqual("AAGET", node.command)
        self.assertTrue(node.get_value("BASEREG"))
        self.assertEqual("YES", node.get_value("INIT"))
        self.assertEqual("R1", node.get_value("BASEREG"))
        self.assertListEqual(["BASEREG", "GET", "INIT", "FILE"], node.keys)
        self.assertSetEqual({"TS110010.2"}, node.next_labels)
        self.assertIsNone(node.goes)
        # GETCC D5,L4,FILL=00
        node = seg.nodes["TS110010.2"]
        self.assertEqual("GETCC", node.command)
        self.assertTrue("L4", node.keys[1])
        self.assertIsNone(node.get_value("L4"))
        self.assertEqual("00", node.get_value("FILL"))
        self.assertListEqual(["D5", "L4", "FILL"], node.keys)
        self.assertSetEqual({"TS110010.3"}, node.next_labels)
        self.assertIsNone(node.goes)
        # PNRCC ACTION=CRLON,REG=R4
        node = seg.nodes["TS110010.3"]
        self.assertEqual("PNRCC", node.command)
        self.assertTrue(node.get_value("REG"))
        self.assertEqual("CRLON", node.get_value("ACTION"))
        self.assertEqual("R4", node.get_value("REG"))
        self.assertListEqual(["ACTION", "REG"], node.keys)
        # MODEC REG=R14,MODE=31
        node = seg.nodes["TS110020.1"]
        self.assertEqual("MODEC", node.command)
        self.assertTrue(node.get_value("REG"))
        self.assertEqual("31", node.get_value("MODE"))
        self.assertEqual("R14", node.get_value("REG"))
        self.assertSetEqual({"TS110020.2"}, node.next_labels)
        # # GLOBZ REGR=R15
        node: RegisterData = seg.nodes["TS110020.2"]
        self.assertEqual("LHI", node.command)
        self.assertEqual("R15", node.reg.reg)
        self.assertEqual(config.GLOBAS, node.data)
        self.assertEqual("GLOBAS", seg.lookup("@HAALC").name)
        self.assertEqual("R15", seg.get_base("GLOBAS").reg)
        # DETAC D8,CHECK=NO
        node: KeyValue = seg.nodes["TS110020.3"]
        self.assertEqual("D8", node.keys[0])
        # DBOPN REF=TR1GAA,REG=R4
        node = seg.nodes["TS110030.1"]
        self.assertTrue(node.get_value("REF"))
        # DBRED REF=TR1GAA,REG=R4,BEGIN,KEY1=(PKY=#TR1GK40), ... several more options
        node = seg.nodes["TS110030.2"]
        self.assertEqual("DBRED", node.command)
        self.assertTrue(node.get_value("KEY5"))
        self.assertListEqual([("PKY", "#TR1GK40")], node.get_value("KEY1"))
        self.assertEqual("TS110020", node.get_value("ERRORA"))
        self.assertListEqual(["REF", "REG", "BEGIN", "KEY1", "KEY2", "KEY3", "KEY4", "KEY5", "ERRORA"], node.keys)
        self.assertEqual("TR1G_40_ACSTIERCODE", node.get_sub_value("KEY3", "R"))
        self.assertEqual("$C_AA", node.get_sub_value("KEY2", "S").name)
        self.assertEqual("LE", node.get_sub_value("KEY4", "C"))
        self.assertSetEqual({"TS110030.3", "TS110020"}, node.next_labels)
        self.assertEqual("TS110020", node.goes)
        # PDCLS WORKAREA=(LEV,5)
        node = seg.nodes["TS110030.3"]
        self.assertListEqual(["LEV", "5"], node.get_value("WORKAREA"))
        self.assertIsNone(node.get_sub_value("WORKAREA", "LEV"))
        self.assertListEqual(["LEV", "5"], node.get_value("WORKAREA"))
        # ATTAC DA
        self.assertIsNone(seg.nodes["TS110040.1"].get_value("DA"))
        # RELCC D5
        self.assertListEqual(["D5"], seg.nodes["TS110040.2"].keys)
        # CRUSA S0=5,S1=E
        self.assertListEqual(["S0", "S1"], seg.nodes["TS110040.3"].keys)
        self.assertEqual("E", seg.nodes["TS110040.3"].get_value("S1"))
        # PDRED FIELD=NAME,WORKAREA=(LEV,5),NOTFOUND=TS110060,ERROR=TS110070,FORMATOUT=UNPACKED,SEARCH1=ACT
        node = seg.nodes["TS110050.1"]
        self.assertListEqual(["FIELD", "WORKAREA", "NOTFOUND", "ERROR", "FORMATOUT", "SEARCH1"], node.keys)
        self.assertIsNone(node.get_sub_value("WORKAREA", "5"))
        self.assertSetEqual({"TS110050.2", "TS110060", "TS110070"}, node.next_labels)
        self.assertEqual("TS110060", node.goes)
        # SYSRA P1=R,P2=021014
        self.assertListEqual(["P1", "P2"], seg.nodes["TS110050.2"].keys)
        # SENDA MSG="MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR"
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'",
                         seg.nodes["TS110060"].get_value("MSG"))
        self.assertSetEqual(set(), seg.nodes["TS110060"].next_labels)
        # CFCMA ALLOCATE,SREF=TS11PDWK,REG=R4,SIZE=4096,FILL=00,ERROR=TS110050
        node = seg.nodes["TS110060.1"]
        self.assertEqual("CFCMA", node.command)
        self.assertIsNone(node.get_value("ALLOCATE"))
        self.assertEqual("TS11PDWK", node.get_value("SREF"))
        self.assertEqual("4096", node.get_value("SIZE"))
        self.assertListEqual(["ALLOCATE", "SREF", "REG", "SIZE", "FILL", "ERROR"], node.keys)
        self.assertSetEqual({"TS110050", "TS110060.2"}, node.next_labels)
        self.assertEqual("TS110050", node.goes)
        # SERRC R,19000
        self.assertEqual(["R", "19000"], seg.nodes["TS110060.2"].keys)
        self.assertIsNone(seg.nodes["TS110060.2"].get_value("Invalid value"))
        # DBCLS REF=PD0_DF_REFX,FILE=PR001W
        self.assertEqual("PR001W", seg.nodes["TS110070.1"].get_value("FILE"))
        # DBIFB REF=PD0_DF_REF,NEWREF=WPSGPNRF,FILE=PR001W,ERRORA=TS110060
        node = seg.nodes["TS110070.2"]
        self.assertEqual("DBIFB", node.command)
        self.assertTrue(node.get_value("NEWREF"))
        self.assertEqual("PD0_DF_REF", node.get_value("REF"))
        self.assertEqual("PR001W", node.get_value("FILE"))
        self.assertListEqual(["REF", "NEWREF", "FILE", "ERRORA", ], node.keys)
        self.assertListEqual(list(), node.sub_key_value)
        self.assertSetEqual({"TS110060"}, node.next_labels)
        self.assertEqual("TS110060", node.goes)


if __name__ == "__main__":
    unittest.main()
