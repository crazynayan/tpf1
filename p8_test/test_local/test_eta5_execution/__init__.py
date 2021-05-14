import unittest
from base64 import b64encode

from config import config
from p1_utils.data_type import DataType
from p2_assembly.mac2_data_macro import macros
from p4_execution.ex5_execute import TpfServer
from p8_test.test_local import TestDataUTS


class NameGeneral(unittest.TestCase):
    SEGMENT = "ETA5"

    def setUp(self) -> None:
        self.tpf_server = TpfServer()
        self.test_data = TestDataUTS()
        self.test_data.output.debug = [self.SEGMENT] if config.ETA5_TEST_DEBUG else list()
        self.output = None
        # AAA
        aaa_fields = ["WA0EXT", "WA0PTY", "WA0ETG", "WA0PTI", "WA0ET4", "WA0ET5"]
        self.test_data.add_fields(aaa_fields, "WA0AA")
        # ECB
        ecb_fields = [("EBX000", 4), ("EBX004", 4), ("EBX008", 4), ("EBX012", 4), "EBW015", "EBW014", "EBW028",
                      "EBW038", "EBSW01", "EBW010", "EBW016", "EBRS01"]
        self.test_data.add_fields(ecb_fields, "EB0EB")
        # UI2PF
        ui2_fields = ["UI2CNN", ("UI2INC", 3)]
        self.test_data.add_fields(ui2_fields, "UI2PF", base_reg="R7")
        # Registers
        self.test_data.add_all_regs()
        # Equates
        macros["UI2PF"].load()
        self.wa0pn2 = macros["WA0AA"].evaluate("#WA0PN2")
        self.wa0any = macros["WA0AA"].evaluate("#WA0ANY")
        self.wa0tty = macros["WA0AA"].evaluate("#WA0TTY")
        self.wa0hfx = macros["WA0AA"].evaluate("#WA0HFX")
        self.wa0tkv = macros["WA0AA"].evaluate("#WA0TKV")
        self.wa0itn = macros["WA0AA"].evaluate("#WA0ITN")
        self.wa0ftn = macros["WA0AA"].evaluate("#WA0FTN")
        self.wa0ftd = macros["WA0AA"].evaluate("#WA0FTD")
        self.wa0afu = macros["WA0AA"].evaluate("#WA0AFU")
        self.wa0tvl = macros["WA0AA"].evaluate("#WA0TVL")
        self.wa0nad = macros["WA0AA"].evaluate("#WA0NAD")
        self.wa0cdi = macros["WA0AA"].evaluate("#WA0CDI")
        self.ui2097 = macros["UI2PF"].evaluate("#UI2097")
        self.ui2098 = macros["UI2PF"].evaluate("#UI2098")
        self.ui2214 = macros["UI2PF"].evaluate("#UI2214")
        self.ui2xui = macros["UI2PF"].evaluate("#UI2XUI")
        self.ui2can = macros["UI2PF"].evaluate("#UI2CAN")
        self.ui2nxt = macros["AASEQ"].evaluate("#UI2NXT")

    def tearDown(self) -> None:
        if not self.output or not self.output.debug:
            return
        for debug_line in self.output.debug:
            if debug_line in config.ETA5_DEBUG_DATA:
                continue
            config.ETA5_DEBUG_DATA.append(debug_line)

    @classmethod
    def tearDownClass(cls) -> None:
        config.ETA5_CLASS_COUNTER += 1
        if config.ETA5_CLASS_COUNTER < 11:
            return
        loc = len(config.ETA5_DEBUG_DATA)
        if loc == 0:
            return
        print(f"{cls.SEGMENT} LOC = {loc}")


hfax_2812_gld = [
    "SSRFQTUBA2811Y20OCTDFW  ORD  0510GLD/DGHWCL RR    ",
    "SSRWCHRAA2814Y20OCT/NN1",
    "SSRFQTUAA2810Y20OCTDFW  ORD  0510GLD/DGHWCL RR    ",
    "SSRFQTUAA2813Y20OCTDFW  ORD  0510GLD*DGHWCL DR    ",
    "SSRWCHRAA2814Y20OCT/NN1",
    "SSRWCHRAA2814Y20OCT/NN1",
    "SSRFQTUAA2812Y20OCTDFW  ORD  0510GLD*DGHWCL RR    ",
]

fqtv_gld = [
    {
        "PR00_60_FQT_CXR": b64encode(DataType("C", input="BA").to_bytes()).decode(),
        "PR00_60_FQT_FTN": b64encode(DataType("C", input="NKE9086").to_bytes()).decode(),
        "PR00_60_FQT_TYP": b64encode(DataType("X", input="60").to_bytes()).decode(),
    },
    {
        "PR00_60_FQT_CXR": b64encode(DataType("C", input="AA").to_bytes()).decode(),
        "PR00_60_FQT_FTN": b64encode(DataType("C", input="NKE9087").to_bytes()).decode(),
        "PR00_60_FQT_TYP": b64encode(DataType("X", input="80").to_bytes()).decode(),  # GLD
    },
]

itin_2811_2812 = [
    {
        "WI0ARC": b64encode(DataType("C", input="BA").to_bytes()).decode(),
        "WI0FNB": b64encode(DataType("H", input="2812").to_bytes()).decode(),
        "WI0DTE": b64encode(DataType("X", input=config.PARS_DATE).to_bytes()).decode(),
        "WI0BRD": b64encode(DataType("C", input="DFW").to_bytes()).decode(),
        "WI0OFF": b64encode(DataType("C", input="ORZ").to_bytes()).decode(),
    },
    {
        "WI0ARC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
        "WI0FNB": b64encode(DataType("H", input="2811").to_bytes()).decode(),
        "WI0DTE": b64encode(DataType("X", input=config.PARS_DATE).to_bytes()).decode(),
        "WI0BRD": b64encode(DataType("C", input="DFW").to_bytes()).decode(),
        "WI0OFF": b64encode(DataType("C", input="ORD").to_bytes()).decode(),
    },
    {
        "WI0ARC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
        "WI0FNB": b64encode(DataType("H", input="2812").to_bytes()).decode(),
        "WI0DTE": b64encode(DataType("X", input="4CC0").to_bytes()).decode(),
        "WI0BRD": b64encode(DataType("C", input="DFW").to_bytes()).decode(),
        "WI0OFF": b64encode(DataType("C", input="ORB").to_bytes()).decode(),
    },
    {
        "WI0ARC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
        "WI0FNB": b64encode(DataType("H", input="2812").to_bytes()).decode(),
        "WI0DTE": b64encode(DataType("X", input=config.PARS_DATE).to_bytes()).decode(),
        "WI0BRD": b64encode(DataType("C", input="DFX").to_bytes()).decode(),
        "WI0OFF": b64encode(DataType("C", input="ORC").to_bytes()).decode(),
    },
    {
        "WI0ARC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
        "WI0FNB": b64encode(DataType("H", input="2812").to_bytes()).decode(),
        "WI0DTE": b64encode(DataType("X", input=config.PARS_DATE).to_bytes()).decode(),
        "WI0BRD": b64encode(DataType("C", input="DFW").to_bytes()).decode(),
        "WI0OFF": b64encode(DataType("C", input="ORD").to_bytes()).decode(),
    },
]

tr1gaa = [
    {
        "TR1G_40_OCC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
        "TR1G_40_ACSTIERCODE": b64encode(DataType("C", input="GLD").to_bytes()).decode(),
        "TR1G_40_TIER_EFFD": b64encode(DataType("X", input="47D3").to_bytes()).decode(),
        "TR1G_40_TIER_DISD": b64encode(DataType("X", input="7FFF").to_bytes()).decode(),
        "TR1G_40_PTI": b64encode(DataType("X", input="80").to_bytes()).decode(),
    },
    {
        "TR1G_40_OCC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
        "TR1G_40_ACSTIERCODE": b64encode(DataType("C", input="EXP").to_bytes()).decode(),
        "TR1G_40_TIER_EFFD": b64encode(DataType("X", input="47D3").to_bytes()).decode(),
        "TR1G_40_TIER_DISD": b64encode(DataType("X", input="7FFF").to_bytes()).decode(),
        "TR1G_40_PTI": b64encode(DataType("X", input="40").to_bytes()).decode(),
    },
    {
        "TR1G_40_OCC": b64encode(DataType("C", input="AA").to_bytes()).decode(),
        "TR1G_40_ACSTIERCODE": b64encode(DataType("C", input="KEY").to_bytes()).decode(),
        "TR1G_40_TIER_EFFD": b64encode(DataType("X", input="47D3").to_bytes()).decode(),
        "TR1G_40_TIER_DISD": b64encode(DataType("X", input="7FFF").to_bytes()).decode(),
        "TR1G_40_PTI": b64encode(DataType("X", input="20").to_bytes()).decode(),
    },
]
