from typing import Optional

from config import config
from db.pnr import Pnr
from execution.state import State
from v2.instruction_type import KeyValue
from v2.data_type import Register
from v2.file_line import SymbolTable


class UserDefinedDbMacro(State):
    def pdred(self, node: KeyValue) -> str:
        # Get the base of PD0WRK
        workarea = node.get_value('WORKAREA')
        if workarea[0] == 'LEV':
            level = f"D{workarea[1]}"
            level_address = self.get_ecb_address(level, 'CE1CR')
            pd0_base = self.vm.get_value(level_address)
        elif workarea[0] == 'REG':
            reg = Register(workarea[1])
            if not reg.is_valid():
                raise TypeError
            pd0_base = self.regs.get_value(reg)
        else:
            raise TypeError

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
        packed = node.get_value('FORMATOUT') == 'PACKED'
        data, item_number = Pnr.get_pnr_data(config.AAAPNR, key, item_number, packed=packed, starts_with=starts_with)
        self.vm.set_value(item_number, pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length)

        # NOTFOUND & last item
        if data is None:
            not_found = node.get_value('NOTFOUND')
            if not_found is None:
                raise IndexError
            return not_found
        elif item_number == Pnr.get_len(config.AAAPNR, key):
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
        if packed:
            pd0_rt_adr_value += (len(Pnr.HEADER) + len(Pnr.HDR[key]['std_fix']))
        if node.get_value('POINT') == 'YES':
            pd0_rt_adr_value += len(Pnr.HDR[key]['std_var'])
        self.vm.set_value(pd0_rt_adr_value, pd0_base + pd0_rt_adr.dsp, pd0_rt_adr.length)
        return node.fall_down


class RealTimeDbMacro(State):
    pass


class TpfdfMacro(State):
    pass


class DbMacro(UserDefinedDbMacro, RealTimeDbMacro, TpfdfMacro):
    pass
