from config import config
from db.pnr import Pnr
from execution.state import State
from v2.instruction_type import KeyValue
from v2.data_type import Register
from v2.file_line import SymbolTable


class UserDefinedDbMacro(State):
    def pdred(self, node: KeyValue) -> str:
        # Get the base of PD0WRK
        workarea = node.get_sub_keys('WORKAREA')
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
            # TODO Code for INDEX=
            raise TypeError

        # Get the item number to read (Item numbers start from 1)
        pd0_mc_cin: SymbolTable = self.seg.macro.data_map['PD0_MC_CIN']
        item_number = self.vm.get_value(pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length) + 1
        total_items = Pnr.get_len(config.AAAPNR, key)
        if item_number > total_items:
            not_found = node.get_value('NOTFOUND')
            if not_found is None:
                raise IndexError
            return not_found
        elif item_number == total_items:
            last_item_bit: int = self.seg.macro.data_map['#PD0_RT_LST'].dsp
            pd0_rt_id1: SymbolTable = self.seg.macro.data_map['PD0_RT_ID1']
            self.vm.all_bits_on(pd0_base + pd0_rt_id1.dsp, last_item_bit)

        # Get the data
        data: bytearray = Pnr.get_pnr_data(config.AAAPNR, key, item_number)
        self.vm.set_value(item_number, pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length)

        # Update the data in PD0WRK
        pd0_c_itm: SymbolTable = self.seg.macro.data_map['PD0_C_ITM']
        pd0_p_itm: SymbolTable = self.seg.macro.data_map['PD0_P_ITM']
        pd0_rt_adr: SymbolTable = self.seg.macro.data_map['PD0_RT_ADR']
        if len(data) > pd0_c_itm.length:
            raise ValueError
        self.vm.set_bytes(data, pd0_base + pd0_c_itm.dsp, len(data))
        self.vm.set_bytes(data, pd0_base + pd0_p_itm.dsp, len(data))
        self.vm.set_value(pd0_base + pd0_p_itm.dsp, pd0_base + pd0_rt_adr.dsp, pd0_rt_adr.length)
        return node.fall_down


class RealTimeDbMacro(State):
    pass


class TpfdfMacro(State):
    pass


class DbMacro(UserDefinedDbMacro, RealTimeDbMacro, TpfdfMacro):
    pass
