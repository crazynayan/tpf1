import unittest

from config import config
from v2.errors import Error
from v2.segment import Program


class SegmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.program = Program()
        self.seg = None

    def _common_checks(self, seg_name, accepted_errors_list=None):
        accepted_errors_list = list() if accepted_errors_list is None else accepted_errors_list
        self.program.load(seg_name)
        self.seg = self.program.segments[seg_name]
        self.assertListEqual(accepted_errors_list, self.seg.errors, '\n\n\n' + '\n'.join(list(
            set(self.seg.errors) - set(accepted_errors_list))))
        self.assertTrue(self.seg.assembled)

    def test_subroutine(self):
        seg_name = 'TS09'
        accepted_errors_list = [
            f"{Error.REG_INVALID} TS09E100.1:BAS:R16,TS09S100 {seg_name}",
            f"{Error.REG_INVALID} TS09E100.2:BR:-1 {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # BAS   R4,TS09S100
        node = self.seg.nodes['TS090010.1']
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('TS09S100', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        # JAS   R2,TS09S100
        node = self.seg.nodes['TS090010.2']
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual('TS09S200', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        # LTR   R1,R1 with BZR   R4
        node = self.seg.nodes['TS09S100.1']
        self.assertIsNone(node.goes)
        self.assertEqual({'TS09S100.2'}, node.next_labels)
        self.assertEqual('BZR', node.conditions[0].on)
        self.assertEqual('R4', node.conditions[0].reg.reg)
        self.assertEqual(8, node.conditions[0].mask)
        self.assertIsNone(node.conditions[0].goes)
        # AHI   R2,1
        self.assertEqual('AHI', self.seg.nodes['TS09S100.2'].command)
        # LTR   R1,R1
        self.assertEqual('LTR', self.seg.nodes['TS09S100.3'].command)
        # NOPR  0
        node = self.seg.nodes['TS09S100.4']
        self.assertEqual('NOPR', node.command)
        self.assertIsNone(node.goes)
        self.assertEqual({'TS09S100.5'}, node.next_labels)
        self.assertEqual('NOPR', node.on)
        self.assertEqual('R0', node.reg.reg)
        self.assertEqual(0, node.mask)
        # AHI   R2,1
        self.assertEqual('AHI', self.seg.nodes['TS09S100.5'].command)
        # BR    R4
        node = self.seg.nodes['TS09S100.6']
        self.assertEqual('BR', node.command)
        self.assertIsNone(node.goes)
        self.assertEqual(set(), node.next_labels)
        self.assertEqual('BR', node.on)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual(15, node.mask)
        # BCR   0,R2
        node = self.seg.nodes['TS09S200.1']
        self.assertEqual('NOPR', node.command)
        self.assertIsNone(node.goes)
        self.assertEqual({'TS09S200.2'}, node.next_labels)
        self.assertEqual('NOPR', node.on)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(0, node.mask)
        # BCR   15,R2
        node = self.seg.nodes['TS09S200.2']
        self.assertEqual('BR', node.command)
        self.assertIsNone(node.goes)
        self.assertEqual(set(), node.next_labels)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(15, node.mask)
        # BCR   8,R2
        node = self.seg.nodes['TS09S200.3']
        self.assertIsNone(node.goes)
        self.assertEqual({'TS09S200.4'}, node.next_labels)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual('BER', node.on)
        self.assertEqual(8, node.mask)

    def test_seg_calls(self):
        seg_name = 'TS10'
        accepted_errors_list = [
            f"{Error.SC_INVALID_SEGMENT} TS10E100.1:ENTRC:A000 {seg_name}",
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # ENTRC TS01
        node = self.seg.nodes['$$TS10$$.1']
        seg = self.program.segments[node.seg_name]
        self.assertEqual('ENTRC', node.command)
        self.assertEqual('TS01', node.seg_name)
        self.assertEqual('$$TS01$$', node.branch.name)
        self.assertIn('$$TS01$$', seg.macro.data_map)
        self.assertIn('OI', seg.nodes['$$TS01$$.1'].command)
        self.assertEqual('$$TS01$$', node.goes)
        self.assertSetEqual({'$$TS01$$', '$$TS10$$.2'}, node.next_labels)
        # ENTNC TS02
        node = self.seg.nodes['$$TS10$$.2']
        seg = self.program.segments[node.seg_name]
        self.assertEqual('ENTNC', node.command)
        self.assertEqual('TS02', node.seg_name)
        self.assertEqual('$$TS02$$', node.branch.name)
        self.assertIn('$$TS02$$', seg.macro.data_map)
        self.assertIn('SR', seg.nodes['TS020010'].command)
        self.assertEqual('$$TS02$$', node.goes)
        self.assertSetEqual({'$$TS02$$'}, node.next_labels)
        # ENTDC TS03
        node = self.seg.nodes['$$TS10$$.3']
        seg = self.program.segments[node.seg_name]
        self.assertEqual('ENTDC', node.command)
        self.assertEqual('TS03', node.seg_name)
        self.assertEqual('$$TS03$$', node.branch.name)
        self.assertIn('$$TS03$$', seg.macro.data_map)
        self.assertIn('L', seg.nodes['$$TS03$$.1'].command)
        self.assertEqual('$$TS03$$', node.goes)
        self.assertSetEqual({'$$TS03$$'}, node.next_labels)

    def test_key_value(self):
        seg_name = 'TS11'
        accepted_errors_list = [
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # AAGET BASEREG=R1,GET=CORE,INIT=YES,FILE=NO
        node = self.seg.nodes['TS110010.1']
        self.assertEqual('AAGET', node.command)
        self.assertTrue(node.is_key('BASEREG'))
        self.assertEqual('YES', node.get_value('INIT'))
        self.assertEqual('BASEREG', node.get_key_from_value('R1')[0])
        self.assertSetEqual({'BASEREG', 'GET', 'INIT', 'FILE'}, node.keys)
        self.assertDictEqual({'BASEREG': 'R1', 'GET': 'CORE', 'INIT': 'YES', 'FILE': 'NO'}, node.items)
        self.assertSetEqual({'TS110010.2'}, node.next_labels)
        self.assertIsNone(node.goes)
        # GETCC D5,L4,FILL=00
        node = self.seg.nodes['TS110010.2']
        self.assertEqual('GETCC', node.command)
        self.assertTrue(node.is_key('L4'))
        self.assertIsNone(node.get_value('L4'))
        self.assertListEqual(['FILL'], node.get_key_from_value('00'))
        self.assertSetEqual({'D5', 'L4', 'FILL'}, node.keys)
        self.assertDictEqual({'D5': None, 'L4': None, 'FILL': '00'}, node.items)
        self.assertSetEqual({'TS110010.3'}, node.next_labels)
        self.assertIsNone(node.goes)
        # PNRCC ACTION=CRLON,REG=R4
        node = self.seg.nodes['TS110010.3']
        self.assertEqual('PNRCC', node.command)
        self.assertTrue(node.is_key('REG'))
        self.assertEqual('CRLON', node.get_value('ACTION'))
        self.assertEqual('REG', node.get_key_from_value('R4')[0])
        self.assertSetEqual({'ACTION', 'REG'}, node.keys)
        self.assertEqual(2, len(node.items))
        # MODEC REG=R14,MODE=31
        node = self.seg.nodes['TS110020.1']
        self.assertEqual('MODEC', node.command)
        self.assertTrue(node.is_key('REG'))
        self.assertEqual('31', node.get_value('MODE'))
        self.assertEqual('REG', node.get_key_from_value('R14')[0])
        self.assertSetEqual({'TS110020.2'}, node.next_labels)
        # GLOBZ REGR=R15
        node = self.seg.nodes['TS110020.2']
        self.assertEqual('LHI', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual(config.GLOBAL, node.data)
        self.assertEqual('GLOBAL', self.seg.macro.data_map['@HAALC'].name)
        self.assertEqual('R15', self.seg.macro.get_base('GLOBAL'))
        # DETAC D8,CHECK=NO
        node = self.seg.nodes['TS110020.3']
        self.assertEqual({'D8'}, node.key_only)
        # DBOPN REF=TR1GAA,REG=R4
        node = self.seg.nodes['TS110030.1']
        self.assertTrue(node.is_key('REF'))
        # DBRED REF=TR1GAA,REG=R4,BEGIN,KEY1=(PKY=#TR1GK40), ... several more options
        node = self.seg.nodes['TS110030.2']
        self.assertEqual('DBRED', node.command)
        self.assertTrue(node.is_key('KEY5'))
        self.assertDictEqual({'PKY': '#TR1GK40'}, node.get_value('KEY1'))
        self.assertEqual('ERRORA', node.get_key_from_value('TS110020')[0])
        self.assertSetEqual({'KEY1', 'KEY2', 'KEY3', 'KEY4', 'KEY5'}, node.sub_keys)
        self.assertEqual('TR1G_40_ACSTIERCODE', node.items['KEY3']['R'])
        self.assertEqual('$C_AA', node.items['KEY2']['S'])
        self.assertEqual('LE', node.items['KEY4']['C'])
        self.assertSetEqual({'TS110030.3', 'TS110020'}, node.next_labels)
        self.assertEqual('TS110020', node.goes)
        # PDCLS WORKAREA=(LEV,5)
        node = self.seg.nodes['TS110030.3']
        self.assertSetEqual({'WORKAREA'}, node.sub_keys)
        self.assertIsNone(node.items['WORKAREA']['LEV'])
        self.assertDictEqual({'LEV': None, '5': None}, node.items['WORKAREA'])
        self.assertEqual('WORKAREA', node.get_key_from_value({'LEV': None, '5': None})[0])
        # ATTAC DA
        self.assertTrue(self.seg.nodes['TS110040.1'].is_key('DA'))
        # RELCC D5
        self.assertSetEqual({'D5'}, self.seg.nodes['TS110040.2'].keys)
        # CRUSA S0=5,S1=E
        self.assertSetEqual({'S0', 'S1'}, self.seg.nodes['TS110040.3'].keys)
        self.assertEqual('E', self.seg.nodes['TS110040.3'].items['S1'])
        # PDRED FIELD=NAME,WORKAREA=(LEV,5),NOTFOUND=TS110060,ERROR=TS110070,FORMATOUT=UNPACKED,SEARCH1=ACT
        node = self.seg.nodes['TS110050.1']
        self.assertSetEqual({'FIELD', 'WORKAREA', 'NOTFOUND', 'ERROR', 'FORMATOUT', 'SEARCH1'}, node.keys)
        self.assertSetEqual({'WORKAREA'}, node.sub_keys)
        self.assertTrue(node.is_sub_key('WORKAREA'))
        self.assertFalse(node.is_sub_key('FIELD'))
        self.assertFalse(node.is_sub_key('INVALID_KEY'))
        self.assertIsNone(node.items['WORKAREA']['5'])
        self.assertSetEqual({'TS110050.2', 'TS110060', 'TS110070'}, node.next_labels)
        self.assertEqual('TS110060', node.goes)
        # SYSRA P1=R,P2=021014
        self.assertDictEqual({'P1': 'R', 'P2': '021014'}, self.seg.nodes['TS110050.2'].items)
        # SENDA MSG='MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'
        self.assertEqual("'MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW PNR'",
                         self.seg.nodes['TS110060'].items['MSG'])
        self.assertSetEqual(set(), self.seg.nodes['TS110060'].next_labels)
        # CFCMA ALLOCATE,SREF=TS11PDWK,REG=R4,SIZE=4096,FILL=00,ERROR=TS110050
        node = self.seg.nodes['TS110060.1']
        self.assertEqual('CFCMA', node.command)
        self.assertTrue(node.is_key('ALLOCATE'))
        self.assertEqual('TS11PDWK', node.get_value('SREF'))
        self.assertEqual('SIZE', node.get_key_from_value('4096')[0])
        self.assertSetEqual({'ALLOCATE', 'SREF', 'REG', 'SIZE', 'FILL', 'ERROR'}, node.keys)
        self.assertEqual(6, len(node.items))
        self.assertSetEqual({'TS110050', 'TS110060.2'}, node.next_labels)
        self.assertEqual('TS110050', node.goes)
        # SERRC R,19000
        self.assertEqual({'R', '19000'}, self.seg.nodes['TS110060.2'].key_only)
        self.assertListEqual(list(), self.seg.nodes['TS110060.2'].get_key_from_value('Invalid value'))
        # DBCLS REF=PD0_DF_REFX,FILE=PR001W
        self.assertEqual('PR001W', self.seg.nodes['TS110070.1'].items['FILE'])
        # DBIFB REF=PD0_DF_REF,NEWREF=WPSGPNRF,FILE=PR001W,ERRORA=TS110060
        node = self.seg.nodes['TS110070.2']
        self.assertEqual('DBIFB', node.command)
        self.assertTrue(node.is_key('NEWREF'))
        self.assertEqual('PD0_DF_REF', node.get_value('REF'))
        self.assertEqual(set(), node.key_only)
        self.assertSetEqual({'REF', 'NEWREF', 'FILE', 'ERRORA', }, node.keys)
        self.assertEqual(4, len(node.items))
        self.assertSetEqual({'TS110060'}, node.next_labels)
        self.assertEqual('TS110060', node.goes)

    def test_other_instruction(self):
        seg_name = 'TS12'
        accepted_errors_list = [
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # LH    R1,FNAME(R2)
        node = self.seg.nodes['TS120100.1']
        self.assertEqual('LH', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual('FNAME', node.field.name)
        self.assertEqual('R2', node.field.index.reg)
        self.assertEqual('R3', node.field.base.reg)
        self.assertEqual(0x090, node.field.dsp)
        self.assertEqual(8, self.seg.macro.data_map['FNAME'].length)
        # LPR   R1,R3
        node = self.seg.nodes['TS120100.2']
        self.assertEqual('LPR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # LNR   R2,R2
        node = self.seg.nodes['TS120100.3']
        self.assertEqual('LNR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R2', node.reg2.reg)
        # LCR   R2,R1
        node = self.seg.nodes['TS120100.4']
        self.assertEqual('LCR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        # A     R5,FWDA
        node = self.seg.nodes['TS120200.1']
        self.assertEqual('A', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('FWDA', node.field.name)
        self.assertIsNone(node.field.index)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x000, node.field.dsp)
        self.assertEqual(4, self.seg.macro.data_map['FWDA'].length)
        # AH    R1,HWD
        node = self.seg.nodes['TS120200.2']
        self.assertEqual('AH', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual('HWD', node.field.name)
        self.assertIsNone(node.field.index)
        self.assertEqual('R3', node.field.base.reg)
        self.assertEqual(0x090, node.field.dsp)
        self.assertEqual(2, self.seg.macro.data_map['HWD'].length)
        # S     R5,FWD(R15)
        node = self.seg.nodes['TS120200.3']
        self.assertEqual('S', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R15', node.field.index.reg)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        self.assertEqual(4, self.seg.macro.data_map['FWD'].length)
        # SH    R4,HWDA
        node = self.seg.nodes['TS120200.4']
        self.assertEqual('SH', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('HWDA', node.field.name)
        self.assertIsNone(node.field.index)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x004, node.field.dsp)
        self.assertEqual(4, self.seg.macro.data_map['HWDA'].length)
        # MH    R5,HWDA
        node = self.seg.nodes['TS120200.5']
        self.assertEqual('MH', node.command)
        self.assertEqual('R5', node.reg.reg)
        # MHI   R5,-2
        node = self.seg.nodes['TS120200.6']
        self.assertEqual('MHI', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual(-2, node.data)
        # M     R4,=F'1'
        node = self.seg.nodes['TS120200.7']
        self.assertEqual('M', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('R8', node.field.base.reg)
        self.assertTrue(self.seg.macro.data_map[node.field.name].is_literal)
        self.assertEqual(bytearray([0x00, 0x00, 0x00, 0x01]), self.seg.get_constant_bytes(node.field.name))
        # MR    R4,R15
        node = self.seg.nodes['TS120200.8']
        self.assertEqual('MR', node.command)
        self.assertEqual('R4', node.reg1.reg)
        self.assertEqual('R15', node.reg2.reg)
        # DR    R4,R7
        node = self.seg.nodes['TS120200.9']
        self.assertEqual('DR', node.command)
        self.assertEqual('R4', node.reg1.reg)
        self.assertEqual('R7', node.reg2.reg)
        # D     R4,NUM
        node = self.seg.nodes['TS120200.10']
        self.assertEqual('D', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x00c, node.field.dsp)
        # SLA   R1,1(R2)
        node = self.seg.nodes['TS120200.11']
        self.assertEqual('SLA', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertIsNone(node.field.index)
        self.assertEqual('R2_AREA', node.field.name)
        self.assertEqual('R2', node.field.base.reg)
        self.assertEqual(1, node.field.dsp)
        # SRA   R3,12
        node = self.seg.nodes['TS120200.12']
        self.assertEqual('SRA', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertIsNone(node.field.index)
        self.assertEqual('R0_AREA', node.field.name)
        self.assertEqual('R0', node.field.base.reg)
        self.assertEqual(12, node.field.dsp)
        # SLDA  R2,4
        node = self.seg.nodes['TS120200.13']
        self.assertEqual('SLDA', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(4, node.field.dsp)
        # SRDA  R2,32
        node = self.seg.nodes['TS120200.14']
        self.assertEqual('SRDA', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(32, node.field.dsp)
        # MVCL  R2,R6
        node = self.seg.nodes['TS120300.1']
        self.assertEqual('MVCL', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # MVZ   FLD1,FLD2
        node = self.seg.nodes['TS120300.2']
        self.assertEqual('MVZ', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(4, node.field_len.length)
        self.assertEqual('R8', node.field.base.reg)
        self.assertTrue(self.seg.macro.data_map[node.field.name].is_literal)
        self.assertEqual(bytearray([0xC1, 0xC2, 0xC3, 0x40, 0x40]), self.seg.get_constant_bytes(node.field.name))
        # MVN   FLD1,FLD1+3
        node = self.seg.nodes['TS120300.3']
        self.assertEqual('MVN', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(4, node.field_len.length)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x503, node.field.dsp)
        # MVO   FIELDB,FIELDA
        node = self.seg.nodes['TS120300.4']
        self.assertEqual('MVO', node.command)
        self.assertEqual('FIELDB', node.field_len1.name)
        self.assertEqual('R8', node.field_len1.base.reg)
        self.assertEqual(0x013, node.field_len1.dsp)
        self.assertEqual(3, node.field_len1.length)
        self.assertEqual('FIELDA', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x010, node.field_len2.dsp)
        self.assertEqual(2, node.field_len2.length)
        # BCT   R3,TS120300
        node = self.seg.nodes['TS120300.5']
        self.assertEqual('BCT', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('TS120300', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(70, node.branch.dsp)
        self.assertIsNone(node.branch.index)
        self.assertEqual('TS120300', node.goes)
        self.assertSetEqual({'TS120300', 'TS120300.6'}, node.next_labels)
        # BXH   R1,R4,TS120100
        node = self.seg.nodes['TS120300.6']
        self.assertEqual('BXH', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        self.assertEqual('TS120100', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(8, node.branch.dsp)
        self.assertIsNone(node.branch.index)
        self.assertEqual('TS120100', node.goes)
        self.assertSetEqual({'TS120100', 'TS120300.7'}, node.next_labels)
        # BXLE  R2,R6,TS120200
        node = self.seg.nodes['TS120300.7']
        self.assertEqual('BXLE', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        self.assertEqual('TS120200', node.branch.name)
        self.assertEqual('R8', node.branch.base.reg)
        self.assertEqual(18, node.branch.dsp)
        self.assertIsNone(node.branch.index)
        self.assertEqual('TS120200', node.goes)
        self.assertSetEqual({'TS120200', 'TS120300.8'}, node.next_labels)
        # BASR  R8,R0
        node = self.seg.nodes['TS120300.8']
        self.assertEqual('BASR', node.command)
        self.assertEqual('R8', node.reg1.reg)
        self.assertEqual('R0', node.reg2.reg)
        # CR    R3,R5
        node = self.seg.nodes['TS120400.1']
        self.assertEqual('CR', node.command)
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R5', node.reg2.reg)
        # C     R3,FWDA
        node = self.seg.nodes['TS120400.2']
        self.assertEqual('C', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('FWDA', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x000, node.field.dsp)
        # CHI   R3,-1
        node = self.seg.nodes['TS120400.3']
        self.assertEqual('CHI', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual(-1, node.data)
        # CL    R3,NUM
        node = self.seg.nodes['TS120400.4']
        self.assertEqual('CL', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x00c, node.field.dsp)
        # CLR   R3,R4
        node = self.seg.nodes['TS120400.5']
        self.assertEqual('CLR', node.command)
        self.assertEqual('R3', node.reg1.reg)
        self.assertEqual('R4', node.reg2.reg)
        # CLM   R3,9,FLD1
        node = self.seg.nodes['TS120400.6']
        self.assertEqual('CLM', node.command)
        self.assertEqual('R3', node.reg.reg)
        self.assertEqual(9, node.data)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x500, node.field.dsp)
        # CLCL  R2,R6
        node = self.seg.nodes['TS120400.7']
        self.assertEqual('CLCL', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R6', node.reg2.reg)
        # SLL   R1,7
        node = self.seg.nodes['TS120400.8']
        self.assertEqual('SLL', node.command)
        self.assertEqual('R1', node.reg.reg)
        self.assertEqual(7, node.field.dsp)
        # SRL   R4,10(R5)
        node = self.seg.nodes['TS120400.9']
        self.assertEqual('SRL', node.command)
        self.assertEqual('R4', node.reg.reg)
        self.assertEqual(10, node.field.dsp)
        self.assertEqual('R5', node.field.base.reg)
        # SLDL  R2,4
        node = self.seg.nodes['TS120400.10']
        self.assertEqual('SLDL', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(4, node.field.dsp)
        # SRDL  R2,32
        node = self.seg.nodes['TS120400.11']
        self.assertEqual('SRDL', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual(32, node.field.dsp)
        # ALR   R5,R15
        # BC    3,TS120400
        node = self.seg.nodes['TS120400.12']
        self.assertEqual('ALR', node.command)
        self.assertEqual('R5', node.reg1.reg)
        self.assertEqual('R15', node.reg2.reg)
        self.assertEqual('TS120400', node.goes)
        self.assertEqual('BCRY', node.on)
        # AL    R5,ONE
        node = self.seg.nodes['TS120400.13']
        self.assertEqual('AL', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('ONE', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x008, node.field.dsp)
        # SLR   R1,R3
        # BC    4,TS120400
        node = self.seg.nodes['TS120400.14']
        self.assertEqual('SLR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        self.assertEqual('TS120400', node.goes)
        self.assertEqual('BL', node.on)
        # SL    R5,ZERO
        node = self.seg.nodes['TS120400.15']
        self.assertEqual('SL', node.command)
        self.assertEqual('R5', node.reg.reg)
        self.assertEqual('ZERO', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x018, node.field.dsp)
        # NC    FLD1,FLD1
        node = self.seg.nodes['TS120500.1']
        self.assertEqual('NC', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R4', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(4, node.field_len.length)
        self.assertEqual('FLD1', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x500, node.field.dsp)
        # NR    R2,R3
        node = self.seg.nodes['TS120500.2']
        self.assertEqual('NR', node.command)
        self.assertEqual('R2', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # OR    R0,R3
        node = self.seg.nodes['TS120500.3']
        self.assertEqual('OR', node.command)
        self.assertEqual('R0', node.reg1.reg)
        self.assertEqual('R3', node.reg2.reg)
        # XR    R1,R1
        node = self.seg.nodes['TS120500.4']
        self.assertEqual('XR', node.command)
        self.assertEqual('R1', node.reg1.reg)
        self.assertEqual('R1', node.reg2.reg)
        # O     R2,FWD
        node = self.seg.nodes['TS120500.5']
        self.assertEqual('O', node.command)
        self.assertEqual('R2', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        # X     R0,FWD
        node = self.seg.nodes['TS120500.6']
        self.assertEqual('X', node.command)
        self.assertEqual('R0', node.reg.reg)
        self.assertEqual('FWD', node.field.name)
        self.assertEqual('R4', node.field.base.reg)
        self.assertEqual(0x1c4, node.field.dsp)
        # XI    TEST,X'CA'
        node = self.seg.nodes['TS120500.7']
        self.assertEqual('TEST', node.field.name)
        self.assertEqual('R6', node.field.base.reg)
        self.assertEqual(0x3cc, node.field.dsp)
        self.assertEqual(0xCA, node.bits.value)
        self.assertEqual('#BIT0+#BIT1+#BIT4+#BIT6', node.bits.text)
        # ZAP   FLD1,FLD1+1(2)
        node = self.seg.nodes['TS120600.1']
        self.assertEqual('ZAP', node.command)
        self.assertEqual('FLD1', node.field_len1.name)
        self.assertEqual('R6', node.field_len1.base.reg)
        self.assertEqual(0x500, node.field_len1.dsp)
        self.assertEqual(4, node.field_len1.length)
        self.assertEqual('FLD1', node.field_len2.name)
        self.assertEqual('R6', node.field_len2.base.reg)
        self.assertEqual(0x501, node.field_len2.dsp)
        self.assertEqual(1, node.field_len2.length)
        # AP    WORK,PACKED
        node = self.seg.nodes['TS120600.2']
        self.assertEqual('AP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('R6', node.field_len1.base.reg)
        self.assertEqual(0x3d0, node.field_len1.dsp)
        self.assertEqual(3, node.field_len1.length)
        self.assertEqual('PACKED', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x01f, node.field_len2.dsp)
        self.assertEqual(1, node.field_len2.length)
        # SP    WORK,PACKED
        node = self.seg.nodes['TS120600.3']
        self.assertEqual('SP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('PACKED', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x01f, node.field_len2.dsp)
        self.assertEqual(1, node.field_len2.length)
        # MP    WORK,P2
        node = self.seg.nodes['TS120600.4']
        self.assertEqual('MP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('P2', node.field_len2.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(0x021, node.field_len2.dsp)
        self.assertEqual(1, node.field_len2.length)
        # DP    WORK,P2
        node = self.seg.nodes['TS120600.5']
        self.assertEqual('DP', node.command)
        self.assertEqual('WORK', node.field_len1.name)
        self.assertEqual('R8', node.field_len2.base.reg)
        self.assertEqual(1, node.field_len2.length)
        literal = node.field_len2.name
        self.assertTrue(self.seg.macro.data_map[literal].is_literal)
        self.assertEqual(bytearray([0x03, 0x9D]), self.seg.get_constant_bytes(literal))
        # CP    =P'0',FLD2
        node = self.seg.nodes['TS120600.6']
        self.assertEqual('CP', node.command)
        self.assertEqual('R8', node.field_len1.base.reg)
        self.assertEqual(0, node.field_len1.length)
        literal = node.field_len1.name
        self.assertTrue(self.seg.macro.data_map[literal].is_literal)
        self.assertEqual(bytearray([0x0C]), self.seg.get_constant_bytes(literal))
        self.assertEqual('FLD2', node.field_len2.name)
        self.assertEqual('R6', node.field_len2.base.reg)
        self.assertEqual(0x505, node.field_len2.dsp)
        self.assertEqual(4, node.field_len2.length)
        # TP    NUM
        node = self.seg.nodes['TS120600.7']
        self.assertEqual('TP', node.command)
        self.assertEqual('NUM', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x00c, node.field.dsp)
        self.assertEqual(3, node.field.length)
        # SRP   FLD1,4,0
        node = self.seg.nodes['TS120600.8']
        self.assertEqual('SRP', node.command)
        self.assertEqual('FLD1', node.field_len.name)
        self.assertEqual('R6', node.field_len.base.reg)
        self.assertEqual(0x500, node.field_len.dsp)
        self.assertEqual(4, node.field_len.length)
        self.assertEqual(4, node.field.dsp)
        self.assertEqual('R0', node.field.base.reg)
        self.assertEqual(0, node.data)
        # TR    INPT,TABLE
        node = self.seg.nodes['TS120600.9']
        self.assertEqual('TR', node.command)
        self.assertEqual('INPT', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x023, node.field_len.dsp)
        self.assertEqual(2, node.field_len.length)
        self.assertEqual('TABLE', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x026, node.field.dsp)
        # TRT   SENT,FULLTBL
        node = self.seg.nodes['TS120600.10']
        self.assertEqual('TRT', node.command)
        self.assertEqual('SENT', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x30, node.field_len.dsp)
        self.assertEqual(10, node.field_len.length)
        self.assertEqual('FULLTBL', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x03b, node.field.dsp)
        # ED    PATTERN,PCK1
        node = self.seg.nodes['TS120600.11']
        self.assertEqual('ED', node.command)
        self.assertEqual('PATTERN', node.field_len.name)
        self.assertEqual('R8', node.field_len.base.reg)
        self.assertEqual(0x13b, node.field_len.dsp)
        self.assertEqual(9, node.field_len.length)
        self.assertEqual('PCK1', node.field.name)
        self.assertEqual('R8', node.field.base.reg)
        self.assertEqual(0x01c, node.field.dsp)
        # EDMK  PATTERN,PCK1
        node = self.seg.nodes['TS120600.12']
        self.assertEqual('PATTERN', node.field_len.name)
        self.assertEqual('PCK1', node.field.name)
        # FULLTBL  DC    193X'FF',9X'00',7X'FF',9X'00',8X'FF',8X'00',22X'FF'
        self.assertEqual(bytearray([0xFF] * 193), self.seg.get_constant_bytes('FULLTBL', 193))
        self.assertEqual(bytearray([0x00] * 9), self.seg.get_constant_bytes("FULLTBL+C'A'", 9))
        self.assertEqual(bytearray([0xFF] * 7), self.seg.get_constant_bytes("FULLTBL+C'I'+1", 7))
        self.assertEqual(bytearray([0x00] * 9), self.seg.get_constant_bytes("FULLTBL+C'J'", 9))
        self.assertEqual(bytearray([0xFF] * 8), self.seg.get_constant_bytes("FULLTBL+C'R'+1", 8))
        self.assertEqual(bytearray([0x00] * 8), self.seg.get_constant_bytes("FULLTBL+C'S'", 8))
        self.assertEqual(bytearray([0xFF] * 22), self.seg.get_constant_bytes("FULLTBL+C'Z'+1", 22))

    def test_execute(self):
        seg_name = 'TS13'
        accepted_errors_list = [
            f"{Error.REG_INVALID} TS13E000.1:EX:R16,TS130010 {seg_name}",
            f"{Error.RL_INVALID_LEN} TS13E000.2:EX:R15,*-1 {seg_name}",
            f"{Error.RL_INVALID_LABEL} TS13E000.3:EX:R15,TS13INVALID {seg_name}"
        ]
        self._common_checks(seg_name, accepted_errors_list)
        # TM    EBW000,0
        node = self.seg.nodes['TS130010.1']
        self.assertEqual('TM', node.command)
        self.assertSetEqual({'TS130010.2'}, node.next_labels)
        # EX    R15,*-4 with BNO   TS130010 on TM    EBW000,0
        node = self.seg.nodes['TS130010.2']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130010.1', node.label)
        self.assertEqual('TS130010', node.goes)
        self.assertSetEqual({'TS130020', 'TS130010'}, node.next_labels)
        ex_node = self.seg.nodes[node.label]
        self.assertEqual('TM', ex_node.command)
        self.assertEqual(0, ex_node.bits.value)
        # EX    R15,*-6 on MVC   EBW000,EBT000
        node = self.seg.nodes['TS130020.2']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130020.1', node.label)
        self.assertSetEqual({'TS130020.3'}, node.next_labels)
        ex_node = self.seg.nodes[node.label]
        self.assertEqual('MVC', ex_node.command)
        self.assertEqual(0, ex_node.field_len.length)
        self.assertEqual('EBW000', ex_node.field_len.name)
        self.assertEqual('EBT000', ex_node.field.name)
        # EX    R15,TS130030 on PACK  EBW088(8),4(1,R2)
        node = self.seg.nodes['TS130020.3']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130030', node.label)
        self.assertSetEqual({'TS130030'}, node.next_labels)
        ex_node = self.seg.nodes[node.label]
        self.assertEqual('PACK', ex_node.command)
        self.assertEqual(7, ex_node.field_len1.length)
        self.assertEqual(0, ex_node.field_len2.length)
        self.assertEqual('EBW088', ex_node.field_len1.name)
        self.assertEqual('R2', ex_node.field_len2.base.reg)
        self.assertEqual(4, ex_node.field_len2.dsp)
        # EX    R15,TS130040 with MVC   EBW000,EBT000
        node = self.seg.nodes['TS130030.1']
        self.assertEqual('EX', node.command)
        self.assertEqual('R15', node.reg.reg)
        self.assertEqual('TS130040.1', node.label)
        self.assertSetEqual({'TS130040'}, node.next_labels)
        ex_node = self.seg.nodes[node.label]
        self.assertEqual('MVC', ex_node.command)
        self.assertEqual(0, ex_node.field_len.length)
        self.assertEqual('EBW000', ex_node.field_len.name)
        self.assertEqual('EBT000', ex_node.field.name)


if __name__ == '__main__':
    unittest.main()
