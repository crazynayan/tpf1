import unittest

from assembly.mac2_data_macro import macros
from execution.ex5_execute import Execute
from firestore import test_data
from utils.data_type import DataType


# Change 4CC1 to 4E2F to ____ i.e. 20Oct19 to 20Oct20 to 20Oct21 (every year after 20NOV)


class NameGeneral(unittest.TestCase):

    def setUp(self) -> None:
        self.tpf_server = Execute()
        self.test_data = test_data.TestData()
        aaa_fields = ['WA0PTY', 'WA0ETG', 'WA0US4', 'WA0UB1', 'WA0PTI', 'WA0ET3', 'WA0ET4', 'WA0ET6', 'WA0ASC',
                      'WA0USE', 'WA0ET2', 'WA0XX3', 'WA0US3']
        self.i_aaa = self.test_data.add_core(aaa_fields, 'WA0AA')
        # === OUTPUT ====
        self.output = self.test_data.outputs[0]
        # AAA
        aaa_fields = ['WA0EXT', 'WA0PTY', 'WA0ETG', 'WA0PTI', 'WA0ET4', 'WA0ET5']
        self.o_aaa = self.test_data.add_core(aaa_fields, 'WA0AA', output=True)
        # ECB
        ecb_fields = ['EBW015', 'EBW014', 'EBW038', 'EBSW01', 'EBW010', 'EBW016', 'EBRS01']
        self.o_ecb = self.test_data.add_core(ecb_fields, 'EB0EB', output=True)
        ecb_fields = [('EBX000', 4), ('EBX004', 4), ('EBX008', 4), ('EBX012', 4)]
        self.ecb_len = self.test_data.add_core_with_len(ecb_fields, 'EB0EB')
        self.o_ecb = {**self.o_ecb, **self.ecb_len}
        # UI2PF
        ui2_fields = [('UI2CNN', 1), ('UI2INC', 3)]
        self.o_ui2 = self.test_data.add_core_with_len(ui2_fields, 'UI2PF', base_reg='R7')
        # Registers
        self.test_data.output.add_regs(['R6', 'R1', 'R15'])
        # Equates
        self.wa0pn2 = macros['WA0AA'].evaluate('#WA0PN2')
        self.wa0any = macros['WA0AA'].evaluate('#WA0ANY')
        self.wa0tty = macros['WA0AA'].evaluate('#WA0TTY')
        self.wa0hfx = macros['WA0AA'].evaluate('#WA0HFX')
        self.wa0tkv = macros['WA0AA'].evaluate('#WA0TKV')
        self.wa0itn = macros['WA0AA'].evaluate('#WA0ITN')
        self.wa0ftn = macros['WA0AA'].evaluate('#WA0FTN')
        self.wa0ftd = macros['WA0AA'].evaluate('#WA0FTD')
        self.wa0afu = macros['WA0AA'].evaluate('#WA0AFU')
        self.wa0tvl = macros['WA0AA'].evaluate('#WA0TVL')
        self.wa0nad = macros['WA0AA'].evaluate('#WA0NAD')
        self.wa0cdi = macros['WA0AA'].evaluate('#WA0CDI')
        self.ui2097 = macros['UI2PF'].evaluate('#UI2097')
        self.ui2098 = macros['UI2PF'].evaluate('#UI2098')
        self.ui2214 = macros['UI2PF'].evaluate('#UI2214')
        self.ui2xui = macros['UI2PF'].evaluate('#UI2XUI')
        self.ui2can = macros['UI2PF'].evaluate('#UI2CAN')
        self.ui2nxt = macros['AASEQ'].evaluate('#UI2NXT')


hfax_2812_gld = [
    'SSRFQTUBA2811Y20OCTDFW  ORD  0510GLD/DGHWCL RR    ',
    'SSRWCHRAA2814Y20OCT/NN1',
    'SSRFQTUAA2810Y20OCTDFW  ORD  0510GLD/DGHWCL RR    ',
    'SSRFQTUAA2813Y20OCTDFW  ORD  0510GLD*DGHWCL DR    ',
    'SSRWCHRAA2814Y20OCT/NN1',
    'SSRWCHRAA2814Y20OCT/NN1',
    'SSRFQTUAA2812Y20OCTDFW  ORD  0510GLD*DGHWCL RR    ',
]

fqtv_gld = [
    {
        'PR00_60_FQT_CXR': DataType('C', input='BA').to_bytes(),
        'PR00_60_FQT_FTN': DataType('C', input='NKE9086').to_bytes(),
        'PR00_60_FQT_TYP': DataType('X', input='60').to_bytes(),
    },
    {
        'PR00_60_FQT_CXR': DataType('C', input='AA').to_bytes(),
        'PR00_60_FQT_FTN': DataType('C', input='NKE9087').to_bytes(),
        'PR00_60_FQT_TYP': DataType('X', input='80').to_bytes(),  # GLD
    },
]

itin_2811_2812 = [
    {
        'WI0ARC': DataType('C', input='BA').to_bytes(),
        'WI0FNB': DataType('H', input='2812').to_bytes(),
        'WI0DTE': DataType('X', input='4E2F').to_bytes(),
        'WI0BRD': DataType('C', input='DFW').to_bytes(),
        'WI0OFF': DataType('C', input='ORZ').to_bytes(),
    },
    {
        'WI0ARC': DataType('C', input='AA').to_bytes(),
        'WI0FNB': DataType('H', input='2811').to_bytes(),
        'WI0DTE': DataType('X', input='4E2F').to_bytes(),
        'WI0BRD': DataType('C', input='DFW').to_bytes(),
        'WI0OFF': DataType('C', input='ORD').to_bytes(),
    },
    {
        'WI0ARC': DataType('C', input='AA').to_bytes(),
        'WI0FNB': DataType('H', input='2812').to_bytes(),
        'WI0DTE': DataType('X', input='4CC0').to_bytes(),
        'WI0BRD': DataType('C', input='DFW').to_bytes(),
        'WI0OFF': DataType('C', input='ORB').to_bytes(),
    },
    {
        'WI0ARC': DataType('C', input='AA').to_bytes(),
        'WI0FNB': DataType('H', input='2812').to_bytes(),
        'WI0DTE': DataType('X', input='4E2F').to_bytes(),
        'WI0BRD': DataType('C', input='DFX').to_bytes(),
        'WI0OFF': DataType('C', input='ORC').to_bytes(),
    },
    {
        'WI0ARC': DataType('C', input='AA').to_bytes(),
        'WI0FNB': DataType('H', input='2812').to_bytes(),
        'WI0DTE': DataType('X', input='4E2F').to_bytes(),
        'WI0BRD': DataType('C', input='DFW').to_bytes(),
        'WI0OFF': DataType('C', input='ORD').to_bytes(),
    },
]

tr1gaa = [
    {
        'TR1G_40_OCC': DataType('C', input='AA').to_bytes(),
        'TR1G_40_ACSTIERCODE': DataType('C', input='GLD').to_bytes(),
        'TR1G_40_TIER_EFFD': DataType('X', input='47D3').to_bytes(),
        'TR1G_40_TIER_DISD': DataType('X', input='7FFF').to_bytes(),
        'TR1G_40_PTI': DataType('X', input='80').to_bytes(),
    },
    {
        'TR1G_40_OCC': DataType('C', input='AA').to_bytes(),
        'TR1G_40_ACSTIERCODE': DataType('C', input='EXP').to_bytes(),
        'TR1G_40_TIER_EFFD': DataType('X', input='47D3').to_bytes(),
        'TR1G_40_TIER_DISD': DataType('X', input='7FFF').to_bytes(),
        'TR1G_40_PTI': DataType('X', input='40').to_bytes(),
    },
    {
        'TR1G_40_OCC': DataType('C', input='AA').to_bytes(),
        'TR1G_40_ACSTIERCODE': DataType('C', input='KEY').to_bytes(),
        'TR1G_40_TIER_EFFD': DataType('X', input='47D3').to_bytes(),
        'TR1G_40_TIER_DISD': DataType('X', input='7FFF').to_bytes(),
        'TR1G_40_PTI': DataType('X', input='20').to_bytes(),
    },
]
