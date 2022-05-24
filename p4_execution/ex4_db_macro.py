from copy import copy
from typing import Optional, Tuple

from p1_utils.data_type import Register, DataType
from p1_utils.errors import RegisterInvalidError, Pd0BaseError, PdredFieldError, PdredSearchError, \
    PdredNotFoundError, PdredPd0Error, DbredError, TpfdfExecutionError, TPFServerMemoryError, \
    NotFoundInSymbolTableError, FileError
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
        workarea = node.get_value("WORKAREA")
        if workarea is None:
            raise Pd0BaseError
        if workarea[0] == "LEV":
            lev_parameter = workarea[1]
            level = lev_parameter[1] if len(lev_parameter) == 2 and lev_parameter[0] == "D" else lev_parameter
            if not self._is_level_present(level):
                self._core_block(self.vm.allocate(), level)
            level = f"D{level}"
            level_address = self.get_ecb_address(level, "CE1CR")
            pd0_base = self.vm.get_value(level_address)
        elif workarea[0] == "REG":
            reg = Register(workarea[1])
            if not reg.is_valid():
                raise RegisterInvalidError
            pd0_base = self.regs.get_value(reg)
        else:
            raise Pd0BaseError
        return pd0_base

    def _get_pnr_locator(self):
        aaa_address = self.vm.get_value(self.regs.R9 + self.seg.evaluate("CE1CR1"))
        self.seg.load_macro("WA0AA")
        pnr_ordinal = self.vm.get_value(aaa_address + self.seg.evaluate("WA0PWR"))
        return PnrLocator.to_locator(pnr_ordinal)

    def _get_key(self, node: KeyValue) -> Tuple[str, int]:
        self.seg.load_macro("PDEQU")
        field_value = node.get_value("FIELD")
        if isinstance(field_value, list):
            if field_value[0] != "INDEX":
                raise PdredFieldError(node)
            index_reg = Register(field_value[1])
            if not index_reg.is_valid():
                raise PdredFieldError(node)
            index_value = self.regs.get_unsigned_value(index_reg)
            key_label = Pnr.get_pdequ_label("index", index_value)
            if not key_label:
                raise PdredFieldError(node)
        elif isinstance(field_value, str):
            key_label = f"#PD_{field_value}"
        elif field_value is None:
            return str(), 0
        else:
            raise PdredFieldError(node)
        try:
            key_number = Pnr.PDEQU[key_label]["key"]
            key = f"{key_number:2X}"
        except NotFoundInSymbolTableError:
            raise PdredFieldError(node)
        return key, key_number

    def _get_item_number(self, node: KeyValue) -> int:
        item_number = 0
        for index in range(1, 7):
            search = node.get_value(f"SEARCH{index}")
            if search is None:
                break
            if search[0] != "ITMNBR":
                continue
            if len(search) != 2:
                raise PdredSearchError
            if isinstance(search[1], FieldBaseDsp):
                # noinspection PyTypeChecker
                field: FieldBaseDsp = search[1]
                item_number = self.vm.get_value(self.regs.get_unsigned_value(field.base) + field.dsp,
                                                self.seg.lookup(field.name).length)
        return item_number

    def pdcls(self, node: KeyValue) -> str:
        pd0_base = self._pd0_base(node)
        self.vm.init(pd0_base)
        return node.fall_down

    def pdred(self, node: KeyValue, locaa=False) -> str:
        self.seg.load_macro("PD0WRK")
        key, key_number = self._get_key(node)
        if not key:
            raise PdredFieldError(node)

        # ERROR=
        error_label = node.get_value("ERROR")
        if error_label and self.is_error(node.label):
            return error_label

        # ACTION=VERIFY
        if node.get_value("ACTION") == "VERIFY":
            not_found_label = node.get_value("NOTFOUND") if node.get_value("NOTFOUND") else node.fall_down
            found_label = node.get_value("FOUND") if node.get_value("FOUND") else node.fall_down
            data, _ = Pnr.get_pnr_data(self._get_pnr_locator(), key, item_number=1)
            return not_found_label if data is None else found_label

        # Get the base of PD0WRK
        pd0_base = self._pd0_base(node)
        if pd0_base == 0:
            raise TPFServerMemoryError

        # Save the key number
        pd0_in_dfkey: LabelReference = self.seg.lookup("PD0_IN_DFKEY")
        self.vm.set_byte(key_number, pd0_base + pd0_in_dfkey.dsp)

        # Get the item number to read (Item numbers start from 1)
        pd0_ctl_key: LabelReference = self.seg.lookup("PD0_CTL_KEY")
        pd0_mc_cin: LabelReference = self.seg.lookup("PD0_MC_CIN")
        last_key = self.vm.get_unsigned_value(pd0_base + pd0_ctl_key.dsp, pd0_ctl_key.length)
        item_number = self.vm.get_value(pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length) + 1 \
            if last_key == key_number else 1
        self.vm.set_value(key_number, pd0_base + pd0_ctl_key.dsp, pd0_ctl_key.length)

        # SEARCH-n parameters
        starts_with: Optional[str] = None
        for index in range(1, 7):
            search = node.get_value(f"SEARCH{index}")
            if search is None:
                break
            if search[0] == "START":
                if len(search) != 2:
                    raise PdredSearchError
                if search[1].startswith("'") and search[1].endswith("'"):
                    starts_with = search[1][1:-1]
                elif search[1].startswith("(") and search[1].endswith(")"):
                    reg = search[1][1:-1]
                    base_address = self.regs.get_unsigned_value(reg)
                    length = self.vm.get_unsigned_value(base_address, 1)
                    char_bytes = self.vm.get_bytes(base_address + 1, length)
                    starts_with = DataType("X", bytes=char_bytes).decode

        # Get the item number from SEARCH-n
        item_number = self._get_item_number(node) or item_number

        # Get the data
        pnr_locator = self._get_pnr_locator()
        packed = node.get_value("FORMATOUT") == "PACKED"
        if key == "20":  # PNR Header
            data, item_number = Pnr.get_pnr_data(pnr_locator, "20", 1, packed=True)
        else:
            data, item_number = Pnr.get_pnr_data(pnr_locator, key, item_number, packed=packed, starts_with=starts_with)
            self.vm.set_value(item_number, pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length)
            pd0_c_inum: LabelReference = self.seg.lookup("PD0_C_INUM")
            self.vm.set_value(item_number, pd0_base + pd0_c_inum.dsp, pd0_c_inum.length)

        # NOTFOUND & last item
        if data is None:
            not_found = node.get_value("NOTFOUND")
            if not_found is None:
                raise PdredNotFoundError
            return not_found
        elif item_number == Pnr.get_len(pnr_locator, key):
            last_item_bit: int = self.seg.evaluate("#PD0_RT_LST")
            pd0_rt_id1: LabelReference = self.seg.lookup("PD0_RT_ID1")
            self.vm.or_bit(pd0_base + pd0_rt_id1.dsp, last_item_bit)

        # Update the data in PD0WRK
        if locaa and self.seg.check("ITMLOC"):
            self.vm.set_bytes(data, pd0_base + self.seg.evaluate("ITMLOC"), len(data))
            return node.fall_down
        pd0_itm: LabelReference = self.seg.lookup("PD0_P_DATA") if packed else self.seg.lookup("PD0_C_ITM")
        pd0_rt_adr: LabelReference = self.seg.lookup("PD0_RT_ADR")
        if len(data) > pd0_itm.length:
            raise PdredPd0Error

        self.vm.set_bytes(data, pd0_base + pd0_itm.dsp, len(data))
        if packed:  # Only packed is coded. For unpacked the PD0_C_ILEN overwrites the fix header.
            pd0_len: LabelReference = self.seg.lookup("PD0_P_LLEN")
            self.vm.set_bytes(byte_array=DataType("H", input=len(data)).to_bytes(pd0_len.length),
                              address=pd0_base + pd0_len.dsp, length=pd0_len.length)
        pd0_rt_adr_value = pd0_base + pd0_itm.dsp
        if node.get_value("POINT") == "YES":
            attribute = Pnr.get_attribute_by_key(key)
            if packed:
                pd0_rt_adr_value += (len(Pnr.STD_PREFIX_BYTES) + len(attribute.std_fix))
            pd0_rt_adr_value += len(attribute.std_var)
        self.vm.set_value(pd0_rt_adr_value, pd0_base + pd0_rt_adr.dsp, pd0_rt_adr.length)
        return node.fall_down

    def locaa(self, node: KeyValue) -> str:
        designator: int = self.regs.get_bytes_from_mask("R0", 0b1000)[0]
        field_label: str = Pnr.get_pdequ_label("designator", designator)
        if not field_label:
            raise PdredFieldError(node)
        field = field_label[4:]
        node.add_key("FIELD", field)
        level: str = node.get_value("LEVEL")
        node.add_key("WORKAREA", ["LEV", level])
        start: str = node.get_value("START")
        node.add_key("SEARCH1", ["START", f"'{start}'"])
        return self.pdred(node, locaa=True)

    def pdmod(self, node: KeyValue) -> str:
        # Skip PDMOD functions for Renumbering Itin segments
        if node.get_value("FIELD") == "ITINERARY" and node.get_value("ACTION") == "RENUM":
            return node.fall_down
        # Get the base of PD0WRK
        pd0_base = self._pd0_base(node)
        if pd0_base == 0:
            raise TPFServerMemoryError

        # Get the key and pnr locator
        self.seg.load_macro("PR001W")
        self.seg.load_macro("PD0WRK")
        pd0_in_dfkey: int = self.seg.evaluate("PD0_IN_DFKEY")
        key_number: int = self.vm.get_byte(pd0_base + pd0_in_dfkey)
        key = f"{key_number:02X}"
        pdmod_key, pdmod_key_number = self._get_key(node)
        if pdmod_key:
            key, key_number = pdmod_key, pdmod_key_number
        pnr_locator = self._get_pnr_locator()

        # Get the data
        packed = node.get_value("FORMATIN") == "PACKED"
        if packed:
            override = node.get_value("OVERRIDE")
            override = override if isinstance(override, list) else list()
            input_label = "PD0_IN_DATA" if "MODIFY" in override else "PD0_P_DATA"
        else:
            input_label = "PD0_C_ITM"
        pd0_itm: int = self.seg.evaluate(input_label)
        data = self.vm.get_bytes(pd0_base + pd0_itm, 300)

        # Get the item number
        if key == "20":
            item_number = 1
        else:
            pd0_mc_cin: LabelReference = self.seg.lookup("PD0_MC_CIN")
            item_number = self.vm.get_value(pd0_base + pd0_mc_cin.dsp, pd0_mc_cin.length)
        item_number = self._get_item_number(node) or item_number

        # Replace
        Pnr.replace_pnr_data(data=data, pnr_locator=pnr_locator, key=key, item_number=item_number, packed=packed)
        return node.fall_down

    def pdctl(self, node: KeyValue) -> str:
        # Get the base of PD0WRK
        pd0_base: int = self._pd0_base(node)
        if pd0_base == 0:
            raise TPFServerMemoryError
        # Init ctl heap
        heap: int = self.vm.allocate()
        pd0_ctl_tbl_hp: int = self.seg.evaluate("PD0_CTL_TBL_HP")
        self.vm.set_value(heap, pd0_base + pd0_ctl_tbl_hp)
        # Init PD0C_CTL_ITM_CNT
        pd0c_ctl_itm_cnt: LabelReference = self.seg.lookup("PD0C_CTL_ITM_CNT")
        self.vm.set_value(1, heap + pd0c_ctl_itm_cnt.dsp, pd0c_ctl_itm_cnt.length)
        # Init PDAT item as header
        pnr_locator: str = self._get_pnr_locator()
        data: Tuple[bytearray, int] = Pnr.get_pnr_data(pnr_locator=pnr_locator, key="20", item_number=1, packed=True)
        data_length: int = len(data[0])
        pd0c_ctl_itm_lgth: LabelReference = self.seg.lookup("PD0C_CTL_ITM_LGTH")
        self.vm.set_value(data_length, heap + pd0c_ctl_itm_lgth.dsp, pd0c_ctl_itm_lgth.length)
        pd0c_ctl_item: int = self.seg.evaluate("PD0C_CTL_ITEM")
        self.vm.set_bytes(data[0], heap + pd0c_ctl_item, data_length)
        return node.fall_down


class RealTimeDbMacro(State):

    def finwc(self, node: KeyValue) -> str:
        level = node.keys[0]
        success_label = node.get_value("SUCCESS") or node.fall_down
        error_label = node.get_value("ERROR") or node.keys[1] if not node.get_value("SUCCESS") else node.fall_down
        # GETCC equivalent process
        address = self.vm.allocate()
        self._core_block(address, level)
        # Get file address and record id
        record_id_address = self.get_ecb_address(level, "CE1FA")
        file_address_address = self.get_ecb_address(level, "EBCFA")
        record_id = self.vm.get_unsigned_value(record_id_address, 2)
        file_address = self.vm.get_unsigned_value(file_address_address, 4)
        # Move the data in the work block
        data = FlatFile.get_record(record_id, file_address)
        if data is None or self.is_error(node.label):
            return error_label
        self.vm.set_bytes(data, address, len(data))
        return success_label

    def face(self, node: InstructionGeneric) -> str:
        ordinal = self.regs.R0
        face_type = self.regs.R6
        address = self.regs.R7 + 4
        file_address = int(FlatFile.face(face_type, ordinal), 16)
        self.vm.set_value(file_address, address)
        return node.fall_down

    def getfc(self, node: KeyValue) -> str:
        level = node.keys[0]
        id_with_type = node.get_value("ID")
        if not id_with_type:
            raise FileError
        record_id: int = self.seg.get_value(id_with_type)
        record_id_address = self.get_ecb_address(level, "CE1FA")
        file_address: int = FlatFile.add_pool(bytearray(), record_id)
        file_address_address: int = self.get_ecb_address(level, "EBCFA")
        self.vm.set_value(file_address, file_address_address, length=4)
        self.vm.set_value(record_id, record_id_address, length=2)
        if node.get_value("BLOCK") == "YES":
            address = self.vm.allocate()
            self._core_block(address, level)
            self.regs.R14 = address
        return node.fall_down

    def relcc(self, node: KeyValue) -> str:
        control_address = self.get_ecb_address(node.keys[0], "CE1CT")
        size_address = self.get_ecb_address(node.keys[0], "CE1CC")
        self.vm.set_value(0x01, control_address, 2)
        self.vm.set_value(0, size_address, 2)
        return node.fall_down

    def filec(self, node: KeyValue) -> str:
        level = node.keys[0]
        record_id_address = self.get_ecb_address(level, "CE1FA")
        file_address_address = self.get_ecb_address(level, "EBCFA")
        record_id = self.vm.get_unsigned_value(record_id_address, length=2)
        file_address = self.vm.get_unsigned_value(file_address_address, length=4)
        core_block_address = self.get_ecb_address(level, "CE1CR")
        core_block = self.vm.get_unsigned_value(core_block_address, length=4)
        data: bytearray = copy(self.vm.get_data_from_base_address(core_block))
        FlatFile.set_data(data, record_id, file_address)
        if node.command in {"FILEC", "FILUC"}:
            self.relcc(node)
        return node.fall_down


class TpfdfMacro(State):
    C = {"E": "==", "EQ": "==", "NE": "!=", "GE": ">=", "LE": "<=", "GT": ">", "LT": "<", "H": ">", "L": "<",
         "NH": "<=", "NL": ">="}

    def _base_sw00sr(self) -> None:
        self.regs.R3 = self.vm.valid_address(self.regs.R3)
        self.seg.load_macro("SW00SR")

    def _get_tpfdf_key(self, node: KeyValue) -> str:
        pky = node.get_sub_value("KEY1", "PKY")
        pky2 = node.get_sub_value("KEY1", "S")
        if pky is not None:
            key = f"{self.seg.evaluate(pky):02X}"
        elif pky2 is not None:
            key = f"{self.seg.evaluate(pky2):02X}"
        else:
            key = str()
        return key

    def _get_other_keys(self, node: KeyValue) -> dict:
        other_keys = dict()
        for key_number in range(2, 7):
            key_n = f"KEY{key_number}"
            if node.get_value(key_n) is None:
                break
            df_field_name = node.get_sub_value(key_n, "R")
            condition = node.get_sub_value(key_n, "C")
            sign = self.C[condition] if condition is not None else "=="
            field: FieldBaseDsp = node.get_sub_value(key_n, "S")
            if field is None:
                # TODO For M, D, L types
                raise DbredError
            base_address = self.regs.get_value(field.base)
            length = self.seg.lookup(df_field_name).length
            byte_array = self.vm.get_bytes(base_address + field.dsp, length)
            other_keys[df_field_name] = (f"{sign} {byte_array}", length)
        return other_keys

    def dbopn(self, node: KeyValue) -> str:
        self.tpfdf_ref[node.get_value("REF")] = 0
        return node.fall_down

    def dbcls(self, node: KeyValue) -> str:
        file_value = node.get_value("FILE")
        ref_value = node.get_value("REF")
        if file_value and file_value != "PR001W":
            raise TpfdfExecutionError(node)
        if file_value == "PR001W":
            return node.fall_down
        if ref_value not in self.tpfdf_ref and ref_value != "ALL":
            raise TpfdfExecutionError(node)
        if ref_value == "ALL":
            self.tpfdf_ref.clear()
        else:
            del self.tpfdf_ref[ref_value]
        return node.fall_down

    def dbifb(self, node: KeyValue) -> str:
        self._base_sw00sr()
        error_label = node.get_value("ERRORA")
        if node.get_value("FILE") == "PR001W":
            if error_label and self.is_error(node.label):
                self.regs.R3 = 0
                return error_label
            return node.fall_down
        if node.get_value("REF") not in self.tpfdf_ref:
            self.regs.R3 = 0
            if error_label:
                return error_label
        return node.fall_down

    def dbred(self, node: KeyValue) -> str:
        self._base_sw00sr()
        # Setup KEY1 Primary key
        key = self._get_tpfdf_key(node)
        # Set up KEY2 to KEY6
        other_keys = self._get_other_keys(node)
        # Get the lrec
        ref_name = node.get_value("REF")
        item_number = 0 if node.get_value("BEGIN") else self.tpfdf_ref.get(ref_name, -1) + 1
        lrec, item_number = Tpfdf.get_lrec(ref_name, key, item_number, other_keys)
        self.tpfdf_ref[ref_name] = item_number
        # Update error_code and REG=
        if lrec is None or self.is_error(node.label):
            error_code = self.seg.evaluate("#TPFDBER")
        else:
            error_code = self.seg.evaluate("#TPFDBOK")
            data_address = self.regs.R3 + self.seg.evaluate("SW00KL1")
            self.vm.set_bytes(lrec, data_address, len(lrec))
            reg = Register(node.get_value("REG"))
            if reg.is_valid():
                self.regs.set_value(data_address, reg)
        self.vm.set_byte(error_code, self.regs.R3 + self.seg.evaluate("SW00RTN"))
        # ERROR=
        error_label = node.get_value("ERRORA")
        if error_label and self.is_error(node.label):
            return error_label
        return node.fall_down

    def dbadd(self, node: KeyValue) -> str:
        self._base_sw00sr()
        # Get Key
        key = self._get_tpfdf_key(node)
        # Get data
        newlrec: FieldBaseDsp = node.get_value("NEWLREC")
        source_address: int = self.regs.get_unsigned_value(newlrec.base) + newlrec.dsp
        length = self.vm.get_value(source_address, 2)
        data: bytearray = self.vm.get_bytes(source_address, length)
        # Build the lrec
        data_bytes: bytearray = DataType("H", input=str(length + 3)).to_bytes(length=2)
        key_bytes: bytearray = DataType("X", input=key).to_bytes(length=1)
        data_bytes.extend(key_bytes)
        data_bytes.extend(data)
        # Add it
        ref_name = node.get_value("REF")
        Tpfdf.add_bytes(data=data_bytes, key=key, ref_name=ref_name)
        return node.fall_down

    def dbdel(self, node) -> str:
        self._base_sw00sr()
        ref_name = node.get_value("REF")
        key = self._get_tpfdf_key(node)
        if key:
            other_keys = self._get_other_keys(node)
            _, item_number = Tpfdf.get_lrec(ref_name, key, item_number=0, other_keys=other_keys)
        else:
            item_number = self.tpfdf_ref.get(ref_name, 0)
        delete_status = Tpfdf.delete_lrec(ref_name, item_number)
        error_label = node.get_value("ERROR") or node.get_value("ERRORA")
        if error_label and delete_status is False:
            return error_label
        return node.fall_down


class DbMacro(UserDefinedDbMacro, RealTimeDbMacro, TpfdfMacro):
    pass
