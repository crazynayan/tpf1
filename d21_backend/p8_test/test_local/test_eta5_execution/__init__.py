from base64 import b64encode

from d21_backend.config import config
from d21_backend.p1_utils.data_type import DataType
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p8_test.test_local import TestDebug


class NameGeneral(TestDebug):
    ETK2_END = "$$CN_PGM_START.5"  # Do ETK7 later
    IGR1_END = "ETA5340.2"
    FMSG_END = "ETA5340.2"
    EXAA_NPTY_END = "ETA5340.2"

    def setUp(self) -> None:
        super().setUp()
        self.test_data.stop_segments = ["ETAW"]
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
        macros = get_macros()
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


hfax_2812_gld = [
    "SSRFQTUBA2811Y20OCTDFW  ORD  0510GLD/DGHWCL RR    ",
    "SSRWCHRAA2814Y20OCT/NN1",
    "SSRFQTUAA2810Y20OCTDFW  ORD  0510GLD/DGHWCL RR    ",
    "SSRFQTUAA2813Y20OCTDFW  ORD  0510GLD*DGHWCL DR    ",
    "SSRWCHRAA2814Y20OCT/NN1",
    "SSRWCHRAA2814Y20OCT/NN1",
    "SSRFQTUAA2812Y20OCTDFW  ORD  0510GLD*DGHWCL RR    ",
]

fqtv_gld = f"""
    PR00_60_FQT_CXR:{bytes("BA", "CP037").hex()}:I1,
    PR00_60_FQT_FTN:{bytes("NKE9086", "CP037").hex()}:I1,
    PR00_60_FQT_TYP:60:I1,
    PR00_60_FQT_CXR:{bytes("AA", "CP037").hex()}:I2,
    PR00_60_FQT_FTN:{bytes("NKE9087", "CP037").hex()}:I2,
    PR00_60_FQT_TYP:80:I2
"""

itin_2811_2812 = f"""
    WI0ARC:{bytes("BA", "CP037").hex()}:I1, WI0FNB:{2812:04x}:I1, WI0DTE:{config.PARS_DATE}:I1, 
    WI0BRD:{bytes("DFW", "CP037").hex()}:I1, WI0OFF:{bytes("ORZ", "CP037").hex()}:I1,
    
    WI0ARC:{bytes("AA", "CP037").hex()}:I2, WI0FNB:{2811:04x}:I2, WI0DTE:{config.PARS_DATE}:I2, 
    WI0BRD:{bytes("DFW", "CP037").hex()}:I2, WI0OFF:{bytes("ORD", "CP037").hex()}:I2,

    WI0ARC:{bytes("AA", "CP037").hex()}:I3, WI0FNB:{2812:04x}:I3, WI0DTE:4CC0:I3, 
    WI0BRD:{bytes("DFW", "CP037").hex()}:I3, WI0OFF:{bytes("ORB", "CP037").hex()}:I3,

    WI0ARC:{bytes("AA", "CP037").hex()}:I4, WI0FNB:{2812:04x}:I4, WI0DTE:{config.PARS_DATE}:I4, 
    WI0BRD:{bytes("DFX", "CP037").hex()}:I4, WI0OFF:{bytes("ORC", "CP037").hex()}:I4,

    WI0ARC:{bytes("AA", "CP037").hex()}:I5, WI0FNB:{2812:04x}:I5, WI0DTE:{config.PARS_DATE}:I5, 
    WI0BRD:{bytes("DFW", "CP037").hex()}:I5, WI0OFF:{bytes("ORD", "CP037").hex()}:I5
     
"""

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
