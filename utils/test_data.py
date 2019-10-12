from assembly.program import program
from config import config
from execution.execute import Execute
from utils.data_type import DataType


program.macros['EB0EB'].load()
program.macros['WA0AA'].load()
program.macros['UI2PF'].load()


class T:
    state: Execute = Execute()
    ebsw01 = config.ECB + program.macros['EB0EB'].symbol_table['EBSW01'].dsp
    ebw000 = config.ECB + program.macros['EB0EB'].symbol_table['EBW000'].dsp
    ebrs01 = config.ECB + program.macros['EB0EB'].symbol_table['EBRS01'].dsp
    wa0et4 = program.macros['WA0AA'].symbol_table['WA0ET4'].dsp
    wa0et5 = program.macros['WA0AA'].symbol_table['WA0ET5'].dsp
    wa0etg = program.macros['WA0AA'].symbol_table['WA0ETG'].dsp
    wa0pty = program.macros['WA0AA'].symbol_table['WA0PTY'].dsp
    wa0pti = program.macros['WA0AA'].symbol_table['WA0PTI'].dsp
    wa0ext = program.macros['WA0AA'].symbol_table['WA0EXT'].dsp
    wa0pn2 = program.macros['WA0AA'].symbol_table['#WA0PN2'].dsp
    wa0any = program.macros['WA0AA'].symbol_table['#WA0ANY'].dsp
    wa0tty = program.macros['WA0AA'].symbol_table['#WA0TTY'].dsp
    wa0hfx = program.macros['WA0AA'].symbol_table['#WA0HFX'].dsp
    ui2cnn = program.macros['UI2PF'].symbol_table['UI2CNN'].dsp
    ui2097 = program.macros['UI2PF'].symbol_table['#UI2097'].dsp
    ui2098 = program.macros['UI2PF'].symbol_table['#UI2098'].dsp
    ui2214 = program.macros['UI2PF'].symbol_table['#UI2214'].dsp
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
