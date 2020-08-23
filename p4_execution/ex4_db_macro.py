from typing import Optional

from p1_utils.data_type import Register
from p1_utils.errors import RegisterInvalidError, Pd0BaseError, PdredFieldError, PdredVerifyError, PdredSearchError, \
    PdredNotFoundError, PdredPd0Error, DbredError
from p2_assembly.mac0_generic import LabelReference
from p2_assembly.seg2_ins_operand import FieldBaseDsp
from p2_assembly.seg3_ins_type import InstructionGeneric
from p2_assembly.seg5_exec_macro import KeyValue
from p3_db.flat_file import FlatFile
from p3_db.pnr import Pnr, PnrLocator
from p3_db.tpfdf import Tpfdf
from p4_execution.ex1_state import State


class UserDefinedDbMacro(State):
    def _pd0_base(self, node: KeyValue) -> Optional[int]:
        workarea = node.get_value('WORKAREA')
        if workarea is None:
            raise Pd0BaseError
        if workarea[0] == 'LEV':
            level = f"D{workarea[1]}" if len(workarea[1]) == 1 else workarea[1]
            level_address = self.get_ecb_address(level, 'CE1CR')
            pd0_base = self.vm.get_value(level_address)
        elif workarea[0] == 'REG':
            reg = Register(workarea[1])
            if not reg.is_valid():
                raise RegisterInvalidError
            pd0_base = self.regs.get_value(reg)
        else:
            raise Pd0BaseError
        return pd0_base

    def _get_pnr_locator(self):
        aaa_address = self.vm.get_value(self.regs.R9 + self.seg.evaluate('CE1CR1'))
        self.seg.load_macro('WA0AA')
        pnr_ordinal = self.vm.get_value(aaa_address + self.seg.evaluate('WA0PWR'))
        return PnrLocator.to_locator(pnr_ordinal)

    def pdcls(self, node: KeyValue) -> str:
        pd0_base = self._pd0_base(node)
        self.vm.init(pd0_base)
        return node.fall_down

    def pdred(self, node: KeyValue) -> str:
        # Get the key from FIELD= or INDEX=
        self.seg.load_macro('PDEQU')
        self.seg.load_macro('PD0WRK')
        key_label = f"#PD_{node.get_value('FIELD')}_K"
        try:
            key_number = self.seg.evaluate(key_label)
            key = f"{key_number:2X}"
        except KeyError:
            # TODO Code for INDEX= Not in ETA5
            raise PdredFieldError

        # ERROR=
        error_label = node.get_value('ERROR')
        if error_label and self.is_error(node.label):
            return error_label

        # ACTION=VERIFY
        if node.get_value('ACTION') == 'VERIFY':
            data, _ = Pnr.get_pnr_data(self._get_pnr_locator(), key, item_number=1)
            if data is None:
                not_found = node.get_value('NOTFOUND')
                if not_found is None:
                    raise PdredVerifyError
                return not_found
            else:
                return node.fall_down

        # Get the base of PD0WRK
        pd0_base = self._pd0_base(node)

        # Get the item number to read (Item numbers start from 1)
        pd0_ctl_key: LabelReference = self.seg.lookup('PD0_CTL_KEY')
        pd0_mc_cin: LabelReference = self.seg.lookup('PD0_MC_CIN')
        last_key = self.vm.get_unsigned_value(pd0_base + pd0_ctl_key.dsp, pd0_ctl_key.length)
        item_number = self.vm.get_value(pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length) + 1 \
            if last_key == key_number else 1
        self.vm.set_value(key_number, pd0_base + pd0_ctl_key.dsp, pd0_ctl_key.length)

        # SEARCH-n parameters
        starts_with: Optional[str] = None
        for index in range(1, 7):
            search = node.get_value(f'SEARCH{index}')
            if search is None:
                break
            if search[0] == 'START':
                if len(search) != 2 or not search[1].startswith("'") or not search[1].endswith("'"):
                    raise PdredSearchError
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
                raise PdredNotFoundError
            return not_found
        elif item_number == Pnr.get_len(pnr_locator, key):
            last_item_bit: int = self.seg.evaluate('#PD0_RT_LST')
            pd0_rt_id1: LabelReference = self.seg.lookup('PD0_RT_ID1')
            self.vm.or_bit(pd0_base + pd0_rt_id1.dsp, last_item_bit)

        # Update the data in PD0WRK
        pd0_itm: LabelReference = self.seg.lookup('PD0_P_DATA') if packed else self.seg.lookup('PD0_C_ITM')
        pd0_rt_adr: LabelReference = self.seg.lookup('PD0_RT_ADR')
        if len(data) > pd0_itm.length:
            raise PdredPd0Error
        self.vm.set_bytes(data, pd0_base + pd0_itm.dsp, len(data))
        pd0_rt_adr_value = pd0_base + pd0_itm.dsp
        if node.get_value('POINT') == 'YES':
            attribute = Pnr.get_attribute_by_key(key)
            if packed:
                pd0_rt_adr_value += (len(Pnr.HEADER) + len(attribute.std_fix))
            pd0_rt_adr_value += len(attribute.std_var)
        self.vm.set_value(pd0_rt_adr_value, pd0_base + pd0_rt_adr.dsp, pd0_rt_adr.length)
        return node.fall_down


class RealTimeDbMacro(State):

    def finwc(self, node: KeyValue) -> str:
        level = node.keys[0]
        # GETCC equivalent process
        address = self.vm.allocate()
        self._core_block(address, level)
        # Get file address and record id
        record_id_address = self.get_ecb_address(level, 'CE1FA')
        file_address_address = self.get_ecb_address(level, 'EBCFA')
        record_id = self.vm.get_unsigned_value(record_id_address, 2)
        file_address = self.vm.get_unsigned_value(file_address_address, 4)
        # Move the data in the work block
        data = FlatFile.get_record(record_id, file_address)
        if data is None or self.is_error(node.label):
            return node.keys[1]
        self.vm.set_bytes(data, address, len(data))
        return node.fall_down

    def face(self, node: InstructionGeneric) -> str:
        ordinal = self.regs.R0
        face_type = self.regs.R6
        address = self.regs.R7 + 4
        file_address = int(FlatFile.face(face_type, ordinal), 16)
        self.vm.set_value(file_address, address)
        return node.fall_down


class TpfdfMacro(State):
    C = {'E': '==', 'EQ': '==', 'NE': '!=', 'GE': '>=', 'LE': '<=', 'GT': '>', 'LT': '<', 'H': '>', 'L':  '<',
         'NH': '<=', 'NL': '>='}

    def _base_sw00sr(self) -> None:
        self.regs.R3 = self.vm.valid_address(self.regs.R3)
        self.seg.load_macro('SW00SR')

    def dbopn(self, node: KeyValue) -> str:
        self.tpfdf_ref[node.get_value('REF')] = 0
        return node.fall_down

    def dbcls(self, node: KeyValue) -> str:
        if node.get_value('FILE') == 'PR001W':
            return node.fall_down
        del self.tpfdf_ref[node.get_value('REF')]
        return node.fall_down

    def dbifb(self, node: KeyValue) -> str:
        self._base_sw00sr()
        error_label = node.get_value('ERRORA')
        if node.get_value('FILE') == 'PR001W':
            if error_label and self.is_error(node.label):
                self.regs.R3 = 0
                return error_label
            return node.fall_down
        if node.get_value('REF') not in self.tpfdf_ref:
            self.regs.R3 = 0
            if error_label:
                return error_label
        return node.fall_down

    def dbred(self, node: KeyValue) -> str:
        self._base_sw00sr()

        # Setup KEY1 Primary key
        pky = node.get_sub_value('KEY1', 'PKY')
        if pky is not None:
            key = f'{self.seg.evaluate(pky):02X}'
        else:
            key = f"{self.seg.evaluate(node.get_sub_value('KEY1', 'S')):02X}"

        # Set up KEY2 to KEY6
        other_keys = dict()
        for key_number in range(2, 7):
            key_n = f'KEY{key_number}'
            if node.get_value(key_n) is None:
                break
            df_field_name = node.get_sub_value(key_n, 'R')
            condition = node.get_sub_value(key_n, 'C')
            sign = self.C[condition] if condition is not None else '=='
            field: FieldBaseDsp = node.get_sub_value(key_n, 'S')
            if field is None:
                # TODO For M, D, L types
                raise DbredError
            base_address = self.regs.get_value(field.base)
            length = self.seg.lookup(df_field_name).length
            byte_array = self.vm.get_bytes(base_address + field.dsp, length)
            other_keys[df_field_name] = (f'{sign} {byte_array}', length)

        # Get the lrec
        ref_name = node.get_value('REF')
        item_number = 0 if node.get_value('BEGIN') else self.tpfdf_ref[ref_name]
        item_number += 1
        lrec, item_number = Tpfdf.get_lrec(ref_name, key, item_number, other_keys)
        self.tpfdf_ref[ref_name] = item_number

        # Update error_code and REG=
        if lrec is None or self.is_error(node.label):
            error_code = self.seg.evaluate('#TPFDBER')
        else:
            error_code = self.seg.evaluate('#TPFDBOK')
            data_address = self.regs.R3 + self.seg.evaluate('SW00KL1')
            self.vm.set_bytes(lrec, data_address, len(lrec))
            reg = Register(node.get_value('REG'))
            if reg.is_valid():
                self.regs.set_value(data_address, reg)
        self.vm.set_byte(error_code, self.regs.R3 + self.seg.evaluate('SW00RTN'))

        # ERROR=
        error_label = node.get_value('ERRORA')
        if error_label and self.is_error(node.label):
            return error_label

        return node.fall_down


class DbMacro(UserDefinedDbMacro, RealTimeDbMacro, TpfdfMacro):
    pass
