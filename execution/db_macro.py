from typing import Optional

from assembly.file_line import SymbolTable
from assembly.instruction_type import KeyValue
from db.pnr import Pnr, PnrLocator
from db.tpfdf import Tpfdf
from execution.state import State
from utils.data_type import Register


class UserDefinedDbMacro(State):
    def _pd0_base(self, node: KeyValue):
        workarea = node.get_value('WORKAREA')
        if workarea[0] == 'LEV':
            level = f"D{workarea[1]}" if len(workarea[1]) == 1 else workarea[1]
            level_address = self.get_ecb_address(level, 'CE1CR')
            pd0_base = self.vm.get_value(level_address)
        elif workarea[0] == 'REG':
            reg = Register(workarea[1])
            if not reg.is_valid():
                raise TypeError
            pd0_base = self.regs.get_value(reg)
        else:
            raise TypeError
        return pd0_base

    def _get_pnr_locator(self):
        aaa_address = self.vm.get_value(self.regs.R9 + self.seg.macro.data_map['CE1CR1'].dsp)
        self.seg.macro.load('WA0AA')
        pnr_ordinal = self.vm.get_value(aaa_address + self.seg.macro.data_map['WA0PWR'].dsp)
        return PnrLocator.to_locator(pnr_ordinal)

    def pdcls(self, node: KeyValue) -> str:
        pd0_base = self._pd0_base(node)
        self.vm.init(pd0_base)
        return node.fall_down

    def pdred(self, node: KeyValue) -> str:
        # Get the base of PD0WRK
        pd0_base = self._pd0_base(node)

        # Get the key from FIELD= or INDEX=
        self.seg.macro.load('PDEQU')
        self.seg.macro.load('PD0WRK')
        key_label = f"#PD_{node.get_value('FIELD')}_K"
        try:
            key = f"{self.seg.macro.data_map[key_label].dsp:2x}"
        except KeyError:
            # TODO Code for INDEX= Not in ETA5
            raise TypeError

        # Get the item number to read (Item numbers start from 1)
        pd0_mc_cin: SymbolTable = self.seg.macro.data_map['PD0_MC_CIN']
        item_number = self.vm.get_value(pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length) + 1

        # SEARCH-n parameters
        starts_with: Optional[str] = None
        for index in range(1, 7):
            search = node.get_value(f'SEARCH{index}')
            if search is None:
                break
            if search[0] == 'START':
                if len(search) != 2 or not search[1].startswith("'") or not search[1].endswith("'"):
                    raise ValueError
                starts_with = search[1][1:-1]

        # Get the data
        pnr_locator = self._get_pnr_locator()
        packed = node.get_value('FORMATOUT') == 'PACKED'
        data, item_number = Pnr.get_pnr_data(pnr_locator, key, item_number, packed=packed, starts_with=starts_with)
        self.vm.set_value(item_number, pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length)

        # NOTFOUND & last item
        if data is None:
            not_found = node.get_value('NOTFOUND')
            if not_found is None:
                raise IndexError
            return not_found
        elif item_number == Pnr.get_len(pnr_locator, key):
            last_item_bit: int = self.seg.macro.data_map['#PD0_RT_LST'].dsp
            pd0_rt_id1: SymbolTable = self.seg.macro.data_map['PD0_RT_ID1']
            self.vm.or_bit(pd0_base + pd0_rt_id1.dsp, last_item_bit)

        # Update the data in PD0WRK
        pd0_itm: SymbolTable = self.seg.macro.data_map['PD0_P_DATA'] if packed else \
            self.seg.macro.data_map['PD0_C_ITM']
        pd0_rt_adr: SymbolTable = self.seg.macro.data_map['PD0_RT_ADR']
        if len(data) > pd0_itm.length:
            raise ValueError
        self.vm.set_bytes(data, pd0_base + pd0_itm.dsp, len(data))
        pd0_rt_adr_value = pd0_base + pd0_itm.dsp
        if node.get_value('POINT') == 'YES':
            if packed:
                pd0_rt_adr_value += (len(Pnr.HEADER) + len(Pnr.HDR[key]['std_fix']))
            pd0_rt_adr_value += len(Pnr.HDR[key]['std_var'])
        self.vm.set_value(pd0_rt_adr_value, pd0_base + pd0_rt_adr.dsp, pd0_rt_adr.length)
        return node.fall_down


class RealTimeDbMacro(State):
    pass


class TpfdfMacro(State):
    C = {'E': '==', 'EQ': '==', 'NE': '!=', 'GE': '>=', 'LE': '<=', 'GT': '>', 'LT': '<', 'H': '>', 'L':  '<',
         'NH': '<=', 'NL': '>='}

    def _base_sw00sr(self) -> None:
        self.regs.R3 = self.vm.valid_address(self.regs.R3)
        self.seg.macro.load('SW00SR')

    def dbopn(self, node: KeyValue) -> str:
        self.tpfdf_ref[node.get_value('REF')] = 0
        return node.fall_down

    def dbcls(self, node: KeyValue) -> str:
        del self.tpfdf_ref[node.get_value('REF')]
        return node.fall_down

    def dbifb(self, node: KeyValue) -> str:
        self._base_sw00sr()
        if node.get_value('REF') not in self.tpfdf_ref:
            self.regs.R3 = 0
            if node.is_key('ERROR'):
                return node.get_value('ERROR')
            if node.is_key('ERRORA'):
                return node.get_value('ERRORA')
        return node.fall_down

    def dbred(self, node: KeyValue) -> str:
        self._base_sw00sr()

        # Setup KEY1 Primary key
        pky = node.get_sub_value('KEY1', 'PKY')
        if pky is not None:
            key = f'{self.seg.macro.data_map[pky].dsp:02X}'
        else:
            key = f"{self.seg.macro.data_map[node.get_sub_value('KEY1', 'S')].dsp:02X}"

        # Set up KEY2 to KEY6
        other_keys = dict()
        for key_number in range(2, 7):
            key_n = f'KEY{key_number}'
            if not node.is_key(key_n):
                break
            df_field_name = node.get_sub_value(key_n, 'R')
            condition = node.get_sub_value(key_n, 'C')
            sign = self.C[condition] if condition is not None else '=='
            field = node.get_sub_value(key_n, 'S')
            if field is None:
                # TODO For M, D, L types
                raise TypeError
            base_address = self.regs.get_value(field.base)
            length = self.seg.macro.data_map[df_field_name].length
            byte_array = self.vm.get_bytes(base_address + field.dsp, length)
            other_keys[df_field_name] = (f'{sign} {byte_array}', length)

        # Get the lrec
        ref_name = node.get_value('REF')
        item_number = 0 if node.is_key('BEGIN') else self.tpfdf_ref[ref_name]
        item_number += 1
        lrec, item_number = Tpfdf.get_lrec(ref_name, key, item_number, other_keys)
        self.tpfdf_ref[ref_name] = item_number

        # Update error_code and REG=
        if lrec is None:
            error_code = self.seg.macro.data_map['#TPFDBER'].dsp
        else:
            error_code = self.seg.macro.data_map['#TPFDBOK'].dsp
            data_address = self.regs.R3 + self.seg.macro.data_map['SW00KL1'].dsp
            self.vm.set_bytes(lrec, data_address, len(lrec))
            reg = Register(node.get_value('REG'))
            if reg.is_valid():
                self.regs.set_value(data_address, reg)
        self.vm.set_byte(error_code, self.regs.R3 + self.seg.macro.data_map['SW00RTN'].dsp)
        return node.fall_down


class DbMacro(UserDefinedDbMacro, RealTimeDbMacro, TpfdfMacro):
    pass
