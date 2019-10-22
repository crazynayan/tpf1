from assembly.mac2_data_macro import macros
from config import config
from execution.execute import Execute
from utils.data_type import DataType

macros['EB0EB'].load()
macros['WA0AA'].load()
macros['UI2PF'].load()


class T:
    state: Execute = Execute()
    state.init_debug(['ETA5'])
    ebsw01 = config.ECB + macros['EB0EB'].evaluate('EBSW01')
    ebw000 = config.ECB + macros['EB0EB'].evaluate('EBW000')
    ebx000 = config.ECB + macros['EB0EB'].evaluate('EBX000')
    ebrs01 = config.ECB + macros['EB0EB'].evaluate('EBRS01')
    wa0et4 = macros['WA0AA'].evaluate('WA0ET4')
    wa0et5 = macros['WA0AA'].evaluate('WA0ET5')
    wa0etg = macros['WA0AA'].evaluate('WA0ETG')
    wa0pty = macros['WA0AA'].evaluate('WA0PTY')
    wa0pti = macros['WA0AA'].evaluate('WA0PTI')
    wa0ext = macros['WA0AA'].evaluate('WA0EXT')
    wa0pn2 = macros['WA0AA'].evaluate('#WA0PN2')
    wa0any = macros['WA0AA'].evaluate('#WA0ANY')
    wa0tty = macros['WA0AA'].evaluate('#WA0TTY')
    wa0hfx = macros['WA0AA'].evaluate('#WA0HFX')
    wa0tkv = macros['WA0AA'].evaluate('#WA0TKV')
    wa0itn = macros['WA0AA'].evaluate('#WA0ITN')
    wa0ftn = macros['WA0AA'].evaluate('#WA0FTN')
    wa0ftd = macros['WA0AA'].evaluate('#WA0FTD')
    wa0afu = macros['WA0AA'].evaluate('#WA0AFU')
    ui2cnn = macros['UI2PF'].evaluate('UI2CNN')
    ui2097 = macros['UI2PF'].evaluate('#UI2097')
    ui2098 = macros['UI2PF'].evaluate('#UI2098')
    ui2214 = macros['UI2PF'].evaluate('#UI2214')
    # Database
    hfax_2812_gld = [
        'SSRFQTUBA2811Y20OCTDFW  ORD  0510GLD/DGHWCL RR    ',
        'SSRWCHRAA2814Y20OCT/NN1',
        'SSRFQTUAA2810Y20OCTDFW  ORD  0510GLD/DGHWCL RR    ',
        'SSRFQTUAA2813Y20OCTDFW  ORD  0510GLD*DGHWCL DR    ',
        'SSRWCHRAA2814Y20OCT/NN1',
        'SSRWCHRAA2814Y20OCT/NN1',
        'SSRFQTUAA2812Y20OCTDFW  ORD  0510GLD*DGHWCL RR    ',
    ]
    hfax_2812_gld_date_error = ['SSRFQTUAA2811Y32OCTDFW  ORD  0510GLD*DGHWCL RR    ']
    hfax_2811_exp = ['SSRFQTUAA2811Y20OCTDFW  ORD  0510EXP*DGHWCL RR    ']
    hfax_2812_exp = ['SSRFQTUAA2812Y20OCTDFW  ORD  0510EXP*DGHWCL RR    ']
    hfax_2812_key = ['SSRFQTUAA2812Y20OCTDFW  ORD  0510KEY*DGHWCL RR    ']
    fqtv_gld = [
        {
            'PR00_60_FQT_CXR': DataType('C', input='BA').to_bytes(),
            'PR00_60_FQT_FTN': DataType('C', input='NKE9086').to_bytes(),
            'PR00_60_FQT_TYP': DataType('X', input='60').to_bytes(),
        },
        {
            'PR00_60_FQT_CXR': DataType('C', input='AA').to_bytes(),
            'PR00_60_FQT_FTN': DataType('C', input='NKE9087').to_bytes(),
            'PR00_60_FQT_TYP': DataType('X', input='80').to_bytes(),    # GLD
        },
    ]
    fqtv_exp_key = [
        {
            'PR00_60_FQT_CXR': DataType('C', input='AA').to_bytes(),
            'PR00_60_FQT_FTN': DataType('C', input='NKE9088').to_bytes(),
            'PR00_60_FQT_TYP': DataType('X', input='60').to_bytes(),  # EXP and # KEY
        },
    ]
    itin_2811_2812 = [
        {
            'WI0ARC': DataType('C', input='BA').to_bytes(),
            'WI0FNB': DataType('H', input='2812').to_bytes(),
            'WI0DTE': DataType('X', input='4CC1').to_bytes(),
            'WI0BRD': DataType('C', input='DFW').to_bytes(),
            'WI0OFF': DataType('C', input='ORZ').to_bytes(),
        },
        {
            'WI0ARC': DataType('C', input='AA').to_bytes(),
            'WI0FNB': DataType('H', input='2811').to_bytes(),
            'WI0DTE': DataType('X', input='4CC1').to_bytes(),
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
            'WI0DTE': DataType('X', input='4CC1').to_bytes(),
            'WI0BRD': DataType('C', input='DFX').to_bytes(),
            'WI0OFF': DataType('C', input='ORC').to_bytes(),
        },
        {
            'WI0ARC': DataType('C', input='AA').to_bytes(),
            'WI0FNB': DataType('H', input='2812').to_bytes(),
            'WI0DTE': DataType('X', input='4CC1').to_bytes(),
            'WI0BRD': DataType('C', input='DFW').to_bytes(),
            'WI0OFF': DataType('C', input='ORD').to_bytes(),
        },
    ]
    itin2811 = [
        {
            'WI0ARC': DataType('C', input='AA').to_bytes(),
            'WI0FNB': DataType('H', input='2811').to_bytes(),
            'WI0DTE': DataType('X', input='4CC1').to_bytes(),
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
